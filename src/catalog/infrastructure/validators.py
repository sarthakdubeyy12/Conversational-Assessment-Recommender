"""
Assessment validation.

Validates assessment data quality and completeness.
"""

from typing import List
from src.catalog.domain.entities import Assessment
from src.catalog.domain.interfaces import IAssessmentValidator
from src.shared.utils.validators import is_valid_url, is_non_empty_string
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class AssessmentValidator(IAssessmentValidator):
    """
    Validates assessment data.
    
    Checks:
    - Required fields present
    - Valid URLs
    - Data quality
    - No obvious errors
    """
    
    def validate(self, assessment: Assessment) -> bool:
        """
        Validate assessment.
        
        Args:
            assessment: Assessment to validate
        
        Returns:
            True if valid
        """
        errors = self.get_validation_errors(assessment)
        
        if errors:
            logger.warning(
                f"Validation failed for '{assessment.name}': {errors}"
            )
            return False
        
        return True
    
    def get_validation_errors(self, assessment: Assessment) -> List[str]:
        """
        Get list of validation errors.
        
        Args:
            assessment: Assessment to validate
        
        Returns:
            List of error messages
        """
        errors = []
        
        # Required fields
        if not is_non_empty_string(assessment.id):
            errors.append("Missing ID")
        
        if not is_non_empty_string(assessment.name):
            errors.append("Missing name")
        
        if not is_valid_url(assessment.url):
            errors.append("Invalid URL")
        
        # Data quality checks
        if assessment.name and len(assessment.name) < 3:
            errors.append("Name too short")
        
        if assessment.duration_minutes and assessment.duration_minutes <= 0:
            errors.append("Invalid duration")
        
        if assessment.question_count and assessment.question_count <= 0:
            errors.append("Invalid question count")
        
        return errors
