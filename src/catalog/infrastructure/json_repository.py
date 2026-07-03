"""
JSON-based catalog repository.

Stores and loads catalog data from JSON file.
"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from src.catalog.domain.entities import Assessment
from src.catalog.domain.interfaces import ICatalogRepository
from src.shared.exceptions.catalog_exceptions import CatalogNotFoundError
from src.shared.logging.logger import get_logger
from src.shared.utils.path_utils import ensure_directory

logger = get_logger(__name__)


class JSONCatalogRepository(ICatalogRepository):
    """
    JSON file storage for catalog.
    
    Stores assessments as JSON array.
    Thread-safe operations.
    """
    
    def __init__(self, file_path: str) -> None:
        """
        Initialize repository.
        
        Args:
            file_path: Path to JSON file
        """
        self._file_path = Path(file_path)
        
        # Ensure directory exists
        ensure_directory(str(self._file_path.parent))
        
        logger.info(f"JSONCatalogRepository initialized: {self._file_path}")
    
    async def save(self, assessments: List[Assessment]) -> None:
        """
        Save assessments to JSON file.
        
        Args:
            assessments: List of assessments to save
        """
        logger.info(f"Saving {len(assessments)} assessments to {self._file_path}")
        
        try:
            # Convert to dicts
            data = [assessment.to_dict() for assessment in assessments]
            
            # Write to file
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully saved {len(assessments)} assessments")
            
        except Exception as e:
            logger.error(f"Failed to save catalog: {e}", exc_info=True)
            raise
    
    async def load(self) -> List[Assessment]:
        """
        Load all assessments from JSON file.
        
        Returns:
            List of assessments
        
        Raises:
            CatalogNotFoundError: If file doesn't exist
        """
        if not self._file_path.exists():
            raise CatalogNotFoundError(str(self._file_path))
        
        logger.info(f"Loading catalog from {self._file_path}")
        
        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Convert dicts to Assessment objects
            assessments = []
            for item in data:
                assessment = self._dict_to_assessment(item)
                assessments.append(assessment)
            
            logger.info(f"Loaded {len(assessments)} assessments")
            return assessments
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in catalog file: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Failed to load catalog: {e}", exc_info=True)
            raise
    
    async def find_by_id(self, assessment_id: str) -> Optional[Assessment]:
        """
        Find assessment by ID.
        
        Args:
            assessment_id: Assessment ID
        
        Returns:
            Assessment or None if not found
        """
        assessments = await self.load()
        
        for assessment in assessments:
            if assessment.id == assessment_id:
                return assessment
        
        return None
    
    async def exists(self) -> bool:
        """
        Check if catalog file exists.
        
        Returns:
            True if exists
        """
        return self._file_path.exists()
    
    def _dict_to_assessment(self, data: dict) -> Assessment:
        """Convert dictionary to Assessment object."""
        # Parse dates
        scraped_at = None
        if data.get("scraped_at"):
            try:
                scraped_at = datetime.fromisoformat(data["scraped_at"])
            except:
                pass
        
        last_updated = None
        if data.get("last_updated"):
            try:
                last_updated = datetime.fromisoformat(data["last_updated"])
            except:
                pass
        
        return Assessment(
            id=data["id"],
            name=data["name"],
            url=data["url"],
            description=data.get("description"),
            category=data.get("category"),
            test_type=data.get("test_type"),
            skills_measured=data.get("skills_measured", []),
            competencies=data.get("competencies", []),
            duration_minutes=data.get("duration_minutes"),
            question_count=data.get("question_count"),
            languages=data.get("languages", []),
            remote_testing=data.get("remote_testing", False),
            adaptive_testing=data.get("adaptive_testing", False),
            mobile_compatible=data.get("mobile_compatible", False),
            job_levels=data.get("job_levels", []),
            suitable_roles=data.get("suitable_roles", []),
            industries=data.get("industries", []),
            product_code=data.get("product_code"),
            assessment_family=data.get("assessment_family"),
            version=data.get("version"),
            tags=data.get("tags", []),
            difficulty_level=data.get("difficulty_level"),
            delivery_method=data.get("delivery_method"),
            metadata=data.get("metadata", {}),
            scraped_at=scraped_at,
            last_updated=last_updated,
        )
