"""
Field comparator.

Compares individual assessment fields.
"""

from typing import Any, List
from src.comparison.domain.comparison_result import (
    AssessmentInfo,
    FieldComparison,
    FieldStatus,
)
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class FieldComparator:
    """
    Compare assessment fields.
    
    Responsibilities:
    - Compare each catalog field
    - Determine field status
    - Handle missing values
    - Support all field types
    
    Design:
    - Deterministic comparison
    - Type-aware comparison
    - Handles None/empty values
    - Structured output
    """
    
    def compare_all_fields(
        self,
        assessment_a: AssessmentInfo,
        assessment_b: AssessmentInfo,
    ) -> List[FieldComparison]:
        """
        Compare all fields between assessments.
        
        Args:
            assessment_a: First assessment
            assessment_b: Second assessment
        
        Returns:
            List of field comparisons
        """
        logger.debug("Comparing all fields")
        
        comparisons = []
        
        # Define fields to compare
        fields = [
            ("category", assessment_a.category, assessment_b.category),
            ("test_type", assessment_a.test_type, assessment_b.test_type),
            ("description", assessment_a.description, assessment_b.description),
            ("duration_minutes", assessment_a.duration_minutes, assessment_b.duration_minutes),
            ("skills", assessment_a.skills, assessment_b.skills),
            ("competencies", assessment_a.competencies, assessment_b.competencies),
            ("languages", assessment_a.languages, assessment_b.languages),
            ("job_levels", assessment_a.job_levels, assessment_b.job_levels),
            ("industries", assessment_a.industries, assessment_b.industries),
            ("tags", assessment_a.tags, assessment_b.tags),
        ]
        
        for field_name, value_a, value_b in fields:
            comparison = self._compare_field(field_name, value_a, value_b)
            comparisons.append(comparison)
        
        logger.info(f"Compared {len(comparisons)} fields")
        return comparisons
    
    def _compare_field(
        self,
        field_name: str,
        value_a: Any,
        value_b: Any,
    ) -> FieldComparison:
        """Compare single field."""
        # Check if both are missing/empty
        if self._is_empty(value_a) and self._is_empty(value_b):
            return FieldComparison(
                field_name=field_name,
                status=FieldStatus.MISSING_IN_BOTH,
                value_a=None,
                value_b=None,
            )
        
        # Check if A is missing
        if self._is_empty(value_a):
            return FieldComparison(
                field_name=field_name,
                status=FieldStatus.MISSING_IN_A,
                value_a=None,
                value_b=value_b,
            )
        
        # Check if B is missing
        if self._is_empty(value_b):
            return FieldComparison(
                field_name=field_name,
                status=FieldStatus.MISSING_IN_B,
                value_a=value_a,
                value_b=None,
            )
        
        # Both have values - check if identical
        if self._are_equal(value_a, value_b):
            return FieldComparison(
                field_name=field_name,
                status=FieldStatus.IDENTICAL,
                value_a=value_a,
                value_b=value_b,
            )
        
        # Different values
        return FieldComparison(
            field_name=field_name,
            status=FieldStatus.DIFFERENT,
            value_a=value_a,
            value_b=value_b,
        )
    
    def _is_empty(self, value: Any) -> bool:
        """Check if value is empty/missing."""
        if value is None:
            return True
        
        if isinstance(value, str) and not value.strip():
            return True
        
        if isinstance(value, list) and len(value) == 0:
            return True
        
        if isinstance(value, int) and value == 0:
            return True
        
        return False
    
    def _are_equal(self, value_a: Any, value_b: Any) -> bool:
        """Check if two values are equal."""
        # For lists, check set equality (order-independent)
        if isinstance(value_a, list) and isinstance(value_b, list):
            return set(value_a) == set(value_b)
        
        # For strings, case-insensitive comparison
        if isinstance(value_a, str) and isinstance(value_b, str):
            return value_a.lower().strip() == value_b.lower().strip()
        
        # Direct equality
        return value_a == value_b
