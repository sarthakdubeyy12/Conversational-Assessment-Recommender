"""
Recommendation engine.

Transforms retrieval results into ranked, validated recommendations.
"""

import time
from typing import List
from src.conversation.state.domain.conversation_state import ConversationState
from src.conversation.intent.domain.intent_result import IntentResult
from src.retrieval.pipeline.pipeline_result import PipelineResult, RankedDocument
from src.recommendation.domain.recommendation_result import (
    AssessmentRecommendation,
    RecommendationResult,
    RecommendationStatistics,
)
from src.recommendation.selection.candidate_selector import CandidateSelector
from src.recommendation.ranking.recommendation_ranker import RecommendationRanker
from src.recommendation.validation.recommendation_validator import RecommendationValidator
from src.recommendation.explanation.explanation_builder import ExplanationBuilder
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class RecommendationEngine:
    """
    Production recommendation engine.
    
    Complete recommendation pipeline:
    1. Candidate Selection
    2. Ranking
    3. Explanation Generation
    4. Validation
    5. Result Assembly
    
    Responsibilities:
    - Transform retrieval results into recommendations
    - Rank and score assessments
    - Generate explanations
    - Validate outputs
    - Track metrics
    
    Design:
    - Modular pipeline
    - Catalog-grounded only
    - No hallucination
    - Full traceability
    """
    
    def __init__(
        self,
        selector: CandidateSelector,
        ranker: RecommendationRanker,
        validator: RecommendationValidator,
        explainer: ExplanationBuilder,
    ) -> None:
        """
        Initialize engine.
        
        Args:
            selector: Candidate selector
            ranker: Recommendation ranker
            validator: Recommendation validator
            explainer: Explanation builder
        """
        self._selector = selector
        self._ranker = ranker
        self._validator = validator
        self._explainer = explainer
        
        logger.info("RecommendationEngine initialized")
    
    def generate_recommendations(
        self,
        retrieval_result: PipelineResult,
        state: ConversationState,
        intent: IntentResult,
    ) -> RecommendationResult:
        """
        Generate recommendations from retrieval results.
        
        Args:
            retrieval_result: Retrieval pipeline result
            state: Conversation state
            intent: Intent result
        
        Returns:
            Recommendation result
        """
        logger.info("Generating recommendations")
        start_time = time.time()
        
        candidates_received = len(retrieval_result.ranked_documents)
        
        # Stage 1: Select viable candidates
        candidates = self._selector.select_candidates(
            retrieval_result.ranked_documents
        )
        candidates_filtered = candidates_received - len(candidates)
        
        # Stage 2: Rank candidates
        ranked_candidates = self._ranker.rank(candidates, state)
        
        # Stage 3: Build recommendations with explanations
        recommendations = []
        for rank, (doc, final_score) in enumerate(ranked_candidates, 1):
            recommendation = self._build_recommendation(
                doc, final_score, rank, state
            )
            recommendations.append(recommendation)
        
        # Stage 4: Validate recommendations
        is_valid, warnings = self._validator.validate(recommendations)
        
        # Calculate statistics
        processing_time_ms = (time.time() - start_time) * 1000
        
        statistics = RecommendationStatistics(
            candidates_received=candidates_received,
            candidates_filtered=candidates_filtered,
            candidates_validated=len(candidates),
            recommendations_generated=len(recommendations),
            processing_time_ms=processing_time_ms,
            avg_ranking_score=self._calc_avg_score(recommendations, "ranking"),
            avg_similarity_score=self._calc_avg_score(recommendations, "similarity"),
            invalid_urls=sum(1 for w in warnings if "invalid URL" in w),
            missing_metadata=sum(1 for w in warnings if "missing" in w),
            duplicates_removed=0,
            low_confidence=candidates_filtered,
        )
        
        # Determine confidence level
        confidence = self._determine_confidence(
            recommendations, retrieval_result
        )
        
        # Build decision rationale
        rationale = self._build_rationale(statistics, retrieval_result)
        
        # Assemble result
        result = RecommendationResult(
            recommendations=recommendations,
            confidence=confidence,
            total_candidates=candidates_received,
            retrieval_source="retrieval_pipeline",
            statistics=statistics,
            is_valid=is_valid,
            validation_warnings=warnings,
            decision_rationale=rationale,
        )
        
        logger.info(
            f"Recommendations generated: {len(recommendations)} assessments, "
            f"{processing_time_ms:.1f}ms, confidence={confidence}"
        )
        
        return result
    
    def _build_recommendation(
        self,
        doc: RankedDocument,
        final_score: float,
        rank: int,
        state: ConversationState,
    ) -> AssessmentRecommendation:
        """Build single recommendation."""
        # Generate explanation
        reason, factors = self._explainer.build_explanation(doc, state)
        
        # Extract matching information
        hiring_ctx = state.hiring_context
        
        # Find skill matches
        required_skills = set(
            skill.lower() for skill in
            hiring_ctx.required_skills + hiring_ctx.technical_skills
        )
        assessment_skills = set(
            skill.lower() for skill in doc.result.skills
        )
        matching_skills = list(required_skills.intersection(assessment_skills))
        
        # Find competency matches
        matching_competencies = doc.result.competencies[:3]  # Top 3
        
        # Build recommendation
        recommendation = AssessmentRecommendation(
            assessment_id=doc.result.assessment_id,
            assessment_name=doc.result.assessment_name,
            official_url=doc.result.url,
            test_type=doc.result.test_type or "Unknown",
            category=doc.result.category or "General",
            matching_skills=matching_skills,
            matching_competencies=matching_competencies,
            ranking_score=final_score,
            similarity_score=doc.result.similarity_score,
            metadata_score=doc.ranking_factors.get("metadata", 0.0),
            skill_score=doc.ranking_factors.get("skill", 0.0),
            recommendation_reason=reason,
            matching_factors=factors,
            duration_minutes=doc.result.duration_minutes or 0,
            languages=doc.result.languages,
            job_levels=doc.result.job_levels,
            industries=doc.result.industries,
            retrieval_rank=rank,
            chunk_id=doc.result.chunk_id,
        )
        
        return recommendation
    
    def _calc_avg_score(
        self,
        recommendations: List[AssessmentRecommendation],
        score_type: str,
    ) -> float:
        """Calculate average score."""
        if not recommendations:
            return 0.0
        
        if score_type == "ranking":
            scores = [rec.ranking_score for rec in recommendations]
        elif score_type == "similarity":
            scores = [rec.similarity_score for rec in recommendations]
        else:
            return 0.0
        
        return sum(scores) / len(scores)
    
    def _determine_confidence(
        self,
        recommendations: List[AssessmentRecommendation],
        retrieval_result: PipelineResult,
    ) -> str:
        """Determine overall confidence level."""
        if not recommendations:
            return "low"
        
        avg_sim = sum(r.similarity_score for r in recommendations) / len(recommendations)
        
        if avg_sim >= 0.5 and len(recommendations) >= 3:
            return "high"
        elif avg_sim >= 0.3 or len(recommendations) >= 2:
            return "medium"
        else:
            return "low"
    
    def _build_rationale(
        self,
        statistics: RecommendationStatistics,
        retrieval_result: PipelineResult,
    ) -> str:
        """Build decision rationale."""
        parts = []
        
        parts.append(
            f"Generated {statistics.recommendations_generated} recommendations "
            f"from {statistics.candidates_received} candidates"
        )
        
        if statistics.candidates_filtered > 0:
            parts.append(f"Filtered {statistics.candidates_filtered} low-quality candidates")
        
        parts.append(
            f"Average similarity: {statistics.avg_similarity_score:.2f}"
        )
        
        return ". ".join(parts)
