"""
Confidence calculator.

Calculates comparison confidence based on metadata completeness.
"""

from typing import List
from src.comparison.domain.comparison_result import (
    AssessmentInfo,
    FieldComparison,
    FieldStatus,
    ConfidenceLevel,
)
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ConfidenceCalculator:
    """
    Calculate comparison confidence.
    
    Responsibilities:
    - Assess metadata completeness
    - Calculate confidence score
    - Determine confidence level
    
    Design:
    - Deterministic calculation
    - Based on data quality
    - Transparent scoring
    """
    
    def calculate_confidence(
        self,
        assessment_a: AssessmentInfo,
        assessment_b: AssessmentInfo,
        field_comparisons: List[FieldComparison],
    ) -> tuple[ConfidenceLevel, float]:
        """
        Calculate comparison confidence.
        
        Args:
            assessment_a: First assessment
            assessment_b: Second assessment
            field_comparisons: Field comparison results
        
        Returns:
            (confidence_level, confidence_score)
        """
        logger.debug("Calculating comparison confidence")
        
        # Count field statuses
        total_fields = len(field_comparisons)
        missing_fields = sum(
            1 for comp in field_comparisons
            if comp.status in [
                FieldStatus.MISSING_IN_A,
                FieldStatus.MISSING_IN_B,
                FieldStatus.MISSING_IN_BOTH,
            ]
        )
        
        comparable_fields = total_fields - missing_fields
        
        # Calculate metadata completeness
        completeness_a = self._calculate_completeness(assessment_a)
        completeness_b = self._calculate_completeness(assessment_b)
        avg_completeness = (completeness_a + completeness_b) / 2
        
        # Calculate confidence score
        if total_fields == 0:
            confidence_score = 0.0
        else:
            field_coverage = comparable_fields / total_fields
            confidence_score = (field_coverage * 0.6) + (avg_completeness * 0.4)
        
        # Determine confidence level
        if confidence_score >= 0.7:
            confidence_level = ConfidenceLevel.HIGH
        elif confidence_score >= 0.4:
            confidence_level = ConfidenceLevel.MEDIUM
        elif confidence_score > 0:
            confidence_level = ConfidenceLevel.LOW
        else:
            confidence_level = ConfidenceLevel.UNKNOWN
        
        logger.info(
            f"Confidence: {confidence_level.value} "
            f"(score={confidence_score:.2f}, "
            f"comparable={comparable_fields}/{total_fields})"
        )
        
        return confidence_level, confidence_score
    
    def _calculate_completeness(self, assessment: AssessmentInfo) -> float:
        """Calculate metadata completeness for one assessment."""
        total_fields = 10
        filled_fields = 0
        
        if assessment.category:
            filled_fields += 1
        if assessment.test_type:
            filled_fields += 1
        if assessment.description:
            filled_fields += 1
        if assessment.skills:
            filled_fields += 1
        if assessment.competencies:
            filled_fields += 1
        if assessment.duration_minutes > 0:
            filled_fields += 1
        if assessment.languages:
            filled_fields += 1
        if assessment.job_levels:
            filled_fields += 1
        if assessment.industries:
            filled_fields += 1
        if assessment.tags:
            filled_fields += 1
        
        return filled_fields / total_fields
