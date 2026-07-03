"""
Difference detector.

Finds differences between assessments.
"""

from typing import List
from src.comparison.domain.comparison_result import AssessmentInfo, FieldComparison, FieldStatus
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class DifferenceDetector:
    """
    Detect differences between assessments.
    
    Responsibilities:
    - Find unique attributes
    - Generate difference statements
    - Base on catalog data only
    
    Design:
    - Catalog-grounded
    - Human-readable output
    - No hallucination
    """
    
    def detect_differences(
        self,
        assessment_a: AssessmentInfo,
        assessment_b: AssessmentInfo,
        field_comparisons: List[FieldComparison],
    ) -> List[str]:
        """
        Detect differences between assessments.
        
        Args:
            assessment_a: First assessment
            assessment_b: Second assessment
            field_comparisons: Field comparison results
        
        Returns:
            List of human-readable difference statements
        """
        logger.debug("Detecting differences")
        
        differences = []
        
        # Check different fields
        for comp in field_comparisons:
            if comp.status == FieldStatus.DIFFERENT:
                difference = self._build_difference_statement(comp, assessment_a, assessment_b)
                if difference:
                    differences.append(difference)
        
        # Check unique skills
        unique_a = set(assessment_a.skills) - set(assessment_b.skills)
        if unique_a:
            skills_str = ", ".join(list(unique_a)[:2])
            differences.append(f"{assessment_a.assessment_name} uniquely measures: {skills_str}")
        
        unique_b = set(assessment_b.skills) - set(assessment_a.skills)
        if unique_b:
            skills_str = ", ".join(list(unique_b)[:2])
            differences.append(f"{assessment_b.assessment_name} uniquely measures: {skills_str}")
        
        logger.info(f"Found {len(differences)} differences")
        return differences
    
    def _build_difference_statement(
        self,
        comp: FieldComparison,
        assessment_a: AssessmentInfo,
        assessment_b: AssessmentInfo,
    ) -> str:
        """Build human-readable difference statement."""
        if comp.field_name == "category":
            return f"Category: {assessment_a.assessment_name} is {comp.value_a}, {assessment_b.assessment_name} is {comp.value_b}"
        
        if comp.field_name == "test_type":
            return f"Type: {assessment_a.assessment_name} is {comp.value_a}, {assessment_b.assessment_name} is {comp.value_b}"
        
        if comp.field_name == "duration_minutes":
            return f"Duration: {assessment_a.assessment_name} takes {comp.value_a} min, {assessment_b.assessment_name} takes {comp.value_b} min"
        
        return ""
