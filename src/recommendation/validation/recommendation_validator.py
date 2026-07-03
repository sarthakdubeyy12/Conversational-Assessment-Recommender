"""
Recommendation validator.

Validates recommendations before output.
"""

from typing import List, Tuple
from src.recommendation.domain.recommendation_result import AssessmentRecommendation
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class RecommendationValidator:
    """
    Validate recommendations.
    
    Responsibilities:
    - Validate URLs
    - Validate metadata completeness
    - Check for duplicates
    - Generate validation warnings
    
    Design:
    - URL validation (shl.com only)
    - Metadata validation
    - Non-blocking warnings
    - Quality assurance
    """
    
    def validate(
        self,
        recommendations: List[AssessmentRecommendation],
    ) -> Tuple[bool, List[str]]:
        """
        Validate recommendations.
        
        Args:
            recommendations: List of recommendations
        
        Returns:
            (is_valid, warnings)
        """
        logger.debug(f"Validating {len(recommendations)} recommendations")
        
        warnings = []
        is_valid = True
        
        # Check minimum count
        if len(recommendations) == 0:
            warnings.append("No recommendations generated")
            is_valid = False
            return is_valid, warnings
        
        # Check maximum count
        if len(recommendations) > 10:
            warnings.append(f"Too many recommendations ({len(recommendations)} > 10)")
        
        # Validate each recommendation
        seen_ids = set()
        invalid_urls = 0
        missing_metadata = 0
        
        for rec in recommendations:
            # Check for duplicates
            if rec.assessment_id in seen_ids:
                warnings.append(f"Duplicate assessment: {rec.assessment_id}")
            seen_ids.add(rec.assessment_id)
            
            # Validate URL
            if not self._is_valid_url(rec.official_url):
                invalid_urls += 1
            
            # Check metadata completeness
            if not rec.category or not rec.test_type:
                missing_metadata += 1
        
        if invalid_urls > 0:
            warnings.append(f"{invalid_urls} recommendations have invalid URLs")
        
        if missing_metadata > 0:
            warnings.append(
                f"{missing_metadata} recommendations missing category/test_type"
            )
        
        logger.info(
            f"Validation: valid={is_valid}, warnings={len(warnings)}"
        )
        
        return is_valid, warnings
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL is from SHL catalog."""
        if not url:
            return False
        
        # Must be HTTPS
        if not url.startswith("https://"):
            return False
        
        # Must be from shl.com domain
        if "shl.com" not in url:
            return False
        
        return True
