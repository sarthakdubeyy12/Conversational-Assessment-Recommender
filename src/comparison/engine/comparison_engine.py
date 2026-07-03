"""
Comparison engine.

Orchestrates assessment comparison using catalog data only.
"""

import time
from typing import Optional
from src.conversation.state.domain.conversation_state import ConversationState
from src.conversation.intent.domain.intent_result import IntentResult
from src.retrieval.pipeline.pipeline_result import PipelineResult
from src.comparison.domain.comparison_result import (
    ComparisonResult,
    ComparisonStatistics,
    AssessmentInfo,
)
from src.comparison.resolver.assessment_resolver import AssessmentResolver
from src.comparison.comparator.field_comparator import FieldComparator
from src.comparison.comparator.similarity_detector import SimilarityDetector
from src.comparison.comparator.difference_detector import DifferenceDetector
from src.comparison.confidence.confidence_calculator import ConfidenceCalculator
from src.comparison.formatting.context_builder import ComparisonContextBuilder
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ComparisonEngine:
    """
    Production comparison engine.
    
    Complete comparison pipeline:
    1. Assessment Resolution (identify assessments from query)
    2. Catalog Retrieval (already done via pipeline)
    3. Field Comparison (compare all fields)
    4. Similarity Detection (find shared attributes)
    5. Difference Detection (find unique attributes)
    6. Confidence Calculation (based on metadata completeness)
    7. Result Assembly (structured output)
    
    Responsibilities:
    - Compare assessments using catalog data only
    - Generate similarities and differences
    - Calculate comparison confidence
    - Build LLM-ready context
    - Track metrics
    
    Design:
    - Catalog-grounded only
    - No LLM hallucination
    - Deterministic comparison
    - Full traceability
    """
    
    def __init__(
        self,
        resolver: AssessmentResolver,
        field_comparator: FieldComparator,
        similarity_detector: SimilarityDetector,
        difference_detector: DifferenceDetector,
        confidence_calculator: ConfidenceCalculator,
        context_builder: ComparisonContextBuilder,
    ) -> None:
        """
        Initialize engine.
        
        Args:
            resolver: Assessment resolver
            field_comparator: Field comparator
            similarity_detector: Similarity detector
            difference_detector: Difference detector
            confidence_calculator: Confidence calculator
            context_builder: Context builder
        """
        self._resolver = resolver
        self._field_comparator = field_comparator
        self._similarity_detector = similarity_detector
        self._difference_detector = difference_detector
        self._confidence_calculator = confidence_calculator
        self._context_builder = context_builder
        
        logger.info("ComparisonEngine initialized")
    
    def compare_assessments(
        self,
        user_message: str,
        retrieval_result: PipelineResult,
        state: ConversationState,
        intent: IntentResult,
    ) -> Optional[ComparisonResult]:
        """
        Compare assessments based on user request and retrieval.
        
        Args:
            user_message: User's comparison request
            retrieval_result: Retrieval pipeline result
            state: Conversation state
            intent: Intent result
        
        Returns:
            ComparisonResult or None if comparison not possible
        """
        logger.info("Starting assessment comparison")
        start_time = time.time()
        
        # Stage 1: Resolve assessments
        assessment_a, assessment_b = self._resolver.resolve_assessments(
            user_message, retrieval_result
        )
        
        if not assessment_a or not assessment_b:
            logger.warning("Could not resolve 2 assessments for comparison")
            return None
        
        logger.info(
            f"Comparing: '{assessment_a.assessment_name}' vs '{assessment_b.assessment_name}'"
        )
        
        retrieval_time_ms = (time.time() - start_time) * 1000
        comparison_start = time.time()
        
        # Stage 2: Compare all fields
        field_comparisons = self._field_comparator.compare_all_fields(
            assessment_a, assessment_b
        )
        
        # Stage 3: Detect similarities
        similarities = self._similarity_detector.detect_similarities(
            assessment_a, assessment_b, field_comparisons
        )
        
        # Stage 4: Detect differences
        differences = self._difference_detector.detect_differences(
            assessment_a, assessment_b, field_comparisons
        )
        
        # Stage 5: Extract unique strengths
        unique_strengths_a = self._extract_unique_strengths(
            assessment_a, assessment_b
        )
        unique_strengths_b = self._extract_unique_strengths(
            assessment_b, assessment_a
        )
        
        # Stage 6: Identify missing fields
        missing_fields_a = self._find_missing_fields(assessment_a, field_comparisons)
        missing_fields_b = self._find_missing_fields(assessment_b, field_comparisons)
        
        missing_note = ""
        if missing_fields_a or missing_fields_b:
            missing_note = "Some metadata is missing. Comparison based on available catalog data."
        
        # Stage 7: Calculate confidence
        confidence_level, confidence_score = self._confidence_calculator.calculate_confidence(
            assessment_a, assessment_b, field_comparisons
        )
        
        # Stage 8: Build LLM-ready context
        structured_context = self._context_builder.build_context(
            assessment_a, assessment_b, similarities, differences, field_comparisons
        )
        
        comparison_time_ms = (time.time() - comparison_start) * 1000
        
        # Calculate statistics
        fields_identical = sum(1 for fc in field_comparisons if fc.status.value == "identical")
        fields_different = sum(1 for fc in field_comparisons if fc.status.value == "different")
        fields_missing = len(field_comparisons) - fields_identical - fields_different
        
        statistics = ComparisonStatistics(
            processing_time_ms=(time.time() - start_time) * 1000,
            retrieval_time_ms=retrieval_time_ms,
            comparison_time_ms=comparison_time_ms,
            fields_compared=len(field_comparisons),
            fields_identical=fields_identical,
            fields_different=fields_different,
            fields_missing=fields_missing,
            similarities_found=len(similarities),
            differences_found=len(differences),
        )
        
        # Build catalog references
        catalog_refs = [
            assessment_a.official_url,
            assessment_b.official_url,
        ]
        
        # Assemble result
        result = ComparisonResult(
            assessment_a=assessment_a,
            assessment_b=assessment_b,
            similarities=similarities,
            differences=differences,
            field_comparisons=field_comparisons,
            unique_strengths_a=unique_strengths_a,
            unique_strengths_b=unique_strengths_b,
            missing_fields_a=missing_fields_a,
            missing_fields_b=missing_fields_b,
            missing_information_note=missing_note,
            confidence=confidence_level,
            confidence_score=confidence_score,
            statistics=statistics,
            retrieval_source="retrieval_pipeline",
            catalog_references=catalog_refs,
            structured_context=structured_context,
        )
        
        logger.info(
            f"Comparison completed: {len(similarities)} similarities, "
            f"{len(differences)} differences, "
            f"{statistics.processing_time_ms:.1f}ms, "
            f"confidence={confidence_level.value}"
        )
        
        return result
    
    def _extract_unique_strengths(
        self,
        assessment: AssessmentInfo,
        other: AssessmentInfo,
    ) -> list[str]:
        """Extract unique strengths of one assessment."""
        strengths = []
        
        # Unique skills
        unique_skills = set(assessment.skills) - set(other.skills)
        if unique_skills:
            strengths.append(f"Unique skills: {', '.join(list(unique_skills)[:3])}")
        
        # Unique competencies
        unique_comps = set(assessment.competencies) - set(other.competencies)
        if unique_comps:
            strengths.append(f"Unique competencies: {', '.join(list(unique_comps)[:2])}")
        
        # Additional languages
        unique_langs = set(assessment.languages) - set(other.languages)
        if unique_langs:
            strengths.append(f"Additional languages: {', '.join(list(unique_langs)[:3])}")
        
        return strengths
    
    def _find_missing_fields(
        self,
        assessment: AssessmentInfo,
        field_comparisons: list,
    ) -> list[str]:
        """Find missing fields for one assessment."""
        missing = []
        
        for comp in field_comparisons:
            if comp.status.value in ["missing_in_a", "missing_in_both"]:
                if comp.field_name not in [fc.field_name for fc in field_comparisons if fc.value_a]:
                    missing.append(comp.field_name)
        
        # Check assessment-specific missing fields
        if not assessment.category:
            missing.append("category")
        if not assessment.test_type:
            missing.append("test_type")
        if not assessment.skills:
            missing.append("skills")
        if not assessment.competencies:
            missing.append("competencies")
        
        return list(set(missing))[:5]  # Dedupe and limit
