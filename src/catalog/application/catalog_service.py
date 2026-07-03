"""Catalog service orchestration."""

from typing import List, Optional

from src.catalog.domain.entities import Assessment
from src.catalog.domain.interfaces import ICatalogRepository


class CatalogService:
    """Orchestrates catalog operations."""
    
    def __init__(self, repository: ICatalogRepository) -> None:
        self._repository = repository
    
    async def get_all_assessments(self) -> List[Assessment]:
        return await self._repository.load()
    
    async def get_assessment_by_id(self, assessment_id: str) -> Optional[Assessment]:
        return await self._repository.find_by_id(assessment_id)
