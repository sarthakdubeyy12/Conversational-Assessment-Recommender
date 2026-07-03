"""
Similarity detector.

Finds similarities between assessments.
"""

from typing import List
from src.comparison.domain.comparison_result import AssessmentInfo, FieldComparison, FieldStatus
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class SimilarityDetector:
    """
    Detect similarities between assessments.
    
    Responsibilities:
    - Find shared attributes
    - Generate similarity statements
    - Base on catalog data only
    
    Design:
    - Catalog-grounded
    - Human-readable output
    - No hallucination
    """
    
    def detect_similarities(
        self,
        assessment_a: AssessmentInfo,
        assessment_b: AssessmentInfo,
        field_comparisons: List[FieldComparison],
    ) -> List[str]:
        """
        Detect similarities between assessments.
        
        Args:
            assessment_a: First assessment
            assessment_b: Second assessment
            field_comparisons: Field comparison results
        
        Returns:
            List of human-readable similarity statements
        """
        logger.debug("Detecting similarities")
        
        similarities = []
        
        # Check identical fields
        for comp in field_comparisons:
            if comp.status == FieldStatus.IDENTICAL:
                similarity = self._build_similarity_statement(comp)
                if similarity:
                    similarities.append(similarity)
        
        # Check shared list items
        shared_skills = set(assessment_a.skills).intersection(set(assessment_b.skills))
        if shared_skills:
            skills_str = ", ".join(list(shared_skills)[:3])
            similarities.append(f"Both measure: {skills_str}")
        
        shared_competencies = set(assessment_a.competencies).intersection(
            set(assessment_b.competencies)
        )
        if shared_competencies:
            comp_str = ", ".join(list(shared_competencies)[:2])
            similarities.append(f"Both assess: {comp_str}")
        
        shared_languages = set(assessment_a.languages).intersection(set(assessment_b.languages))
        if shared_languages:
            lang_str = ", ".join(list(shared_languages)[:3])
            similarities.append(f"Available in: {lang_str}")
        
        shared_levels = set(assessment_a.job_levels).intersection(set(assessment_b.job_levels))
        if shared_levels:
            levels_str = ", ".join(list(shared_levels)[:2])
            similarities.append(f"Suitable for: {levels_str}")
        
        logger.info(f"Found {len(similarities)} similarities")
        return similarities
    
    def _build_similarity_statement(self, comp: FieldComparison) -> str:
        """Build human-readable similarity statement."""
        if comp.field_name == "category" and comp.value_a:
            return f"Both are {comp.value_a} assessments"
        
        if comp.field_name == "test_type" and comp.value_a:
            return f"Both are {comp.value_a} tests"
        
        if comp.field_name == "duration_minutes" and comp.value_a:
            return f"Same duration: {comp.value_a} minutes"
        
        return ""
