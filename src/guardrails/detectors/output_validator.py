"""
Output validator.

Validates that outputs are catalog-grounded and safe.
"""

import re
from typing import Tuple, List, Optional, Any
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class OutputValidator:
    """
    Validate output safety and grounding.
    
    Responsibilities:
    - Validate catalog grounding
    - Detect hallucinated content
    - Validate URL format
    - Verify assessment references
    
    Design:
    - Deterministic validation
    - Explicit evidence checking
    - No guessing
    """
    
    def __init__(self) -> None:
        """Initialize validator."""
        # Valid SHL URL pattern
        self._shl_url_pattern = re.compile(
            r"https?://(?:www\.)?shl\.com/",
            re.IGNORECASE
        )
    
    def validate_recommendation(
        self,
        recommendation: Any,
        catalog_ids: List[str],
    ) -> Tuple[bool, List[str]]:
        """
        Validate recommendation is catalog-grounded.
        
        Args:
            recommendation: Recommendation object
            catalog_ids: Valid assessment IDs from catalog
        
        Returns:
            (is_valid, violations)
        """
        violations = []
        
        # Check assessment ID exists in catalog
        if hasattr(recommendation, "assessment_id"):
            if recommendation.assessment_id not in catalog_ids:
                violations.append(
                    f"Unknown assessment ID: {recommendation.assessment_id}"
                )
        
        # Validate URL
        if hasattr(recommendation, "official_url"):
            if not self._is_valid_shl_url(recommendation.official_url):
                violations.append(
                    f"Invalid URL: {recommendation.official_url}"
                )
        
        # Check for empty critical fields
        if hasattr(recommendation, "assessment_name"):
            if not recommendation.assessment_name:
                violations.append("Missing assessment name")
        
        is_valid = len(violations) == 0
        
        if not is_valid:
            logger.warning(f"Invalid recommendation: {violations}")
        
        return is_valid, violations
    
    def validate_comparison(
        self,
        comparison: Any,
        catalog_ids: List[str],
    ) -> Tuple[bool, List[str]]:
        """
        Validate comparison is catalog-grounded.
        
        Args:
            comparison: Comparison result object
            catalog_ids: Valid assessment IDs from catalog
        
        Returns:
            (is_valid, violations)
        """
        violations = []
        
        # Validate both assessments
        if hasattr(comparison, "assessment_a"):
            a_id = getattr(comparison.assessment_a, "assessment_id", None)
            if a_id and a_id not in catalog_ids:
                violations.append(f"Unknown assessment A: {a_id}")
            
            a_url = getattr(comparison.assessment_a, "official_url", None)
            if a_url and not self._is_valid_shl_url(a_url):
                violations.append(f"Invalid URL for A: {a_url}")
        
        if hasattr(comparison, "assessment_b"):
            b_id = getattr(comparison.assessment_b, "assessment_id", None)
            if b_id and b_id not in catalog_ids:
                violations.append(f"Unknown assessment B: {b_id}")
            
            b_url = getattr(comparison.assessment_b, "official_url", None)
            if b_url and not self._is_valid_shl_url(b_url):
                violations.append(f"Invalid URL for B: {b_url}")
        
        is_valid = len(violations) == 0
        
        if not is_valid:
            logger.warning(f"Invalid comparison: {violations}")
        
        return is_valid, violations
    
    def _is_valid_shl_url(self, url: str) -> bool:
        """Check if URL is valid SHL URL."""
        if not url:
            return False
        
        return self._shl_url_pattern.match(url) is not None
