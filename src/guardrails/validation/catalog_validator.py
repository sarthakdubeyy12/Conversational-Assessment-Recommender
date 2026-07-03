"""
Catalog validator.

Validates that all references trace back to catalog.
"""

from typing import List, Dict, Any
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class CatalogValidator:
    """
    Validate catalog grounding.
    
    Responsibilities:
    - Verify assessment IDs exist
    - Verify URLs are from catalog
    - Verify metadata references
    - Ensure no fabricated content
    
    Design:
    - Explicit evidence checking
    - No assumptions
    - Strict validation
    """
    
    def __init__(self, catalog_ids: List[str]) -> None:
        """
        Initialize with catalog data.
        
        Args:
            catalog_ids: Valid assessment IDs from catalog
        """
        self._catalog_ids = set(catalog_ids)
        logger.debug(f"CatalogValidator initialized with {len(catalog_ids)} IDs")
    
    def validate_assessment_id(self, assessment_id: str) -> bool:
        """Check if assessment ID exists in catalog."""
        is_valid = assessment_id in self._catalog_ids
        
        if not is_valid:
            logger.warning(f"Unknown assessment ID: {assessment_id}")
        
        return is_valid
    
    def validate_assessment_ids(self, assessment_ids: List[str]) -> Dict[str, bool]:
        """
        Validate multiple assessment IDs.
        
        Args:
            assessment_ids: IDs to validate
        
        Returns:
            {id: is_valid}
        """
        return {
            aid: self.validate_assessment_id(aid)
            for aid in assessment_ids
        }
    
    def get_invalid_ids(self, assessment_ids: List[str]) -> List[str]:
        """Get list of invalid assessment IDs."""
        return [
            aid for aid in assessment_ids
            if aid not in self._catalog_ids
        ]
    
    def validate_grounding(
        self,
        result: Any,
        required_fields: List[str],
    ) -> tuple[bool, List[str]]:
        """
        Validate that result has required catalog-grounded fields.
        
        Args:
            result: Result object to validate
            required_fields: List of required field names
        
        Returns:
            (is_grounded, missing_fields)
        """
        missing_fields = []
        
        for field_name in required_fields:
            if not hasattr(result, field_name):
                missing_fields.append(field_name)
                continue
            
            value = getattr(result, field_name)
            if value is None or value == "":
                missing_fields.append(field_name)
        
        is_grounded = len(missing_fields) == 0
        
        if not is_grounded:
            logger.warning(f"Missing grounding fields: {missing_fields}")
        
        return is_grounded, missing_fields
