"""Catalog domain interfaces."""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.catalog.domain.entities import Assessment


class ICatalogRepository(ABC):
    """Interface for catalog persistence."""
    
    @abstractmethod
    async def save(self, assessments: List[Assessment]) -> None:
        pass
    
    @abstractmethod
    async def load(self) -> List[Assessment]:
        pass
    
    @abstractmethod
    async def find_by_id(self, assessment_id: str) -> Optional[Assessment]:
        pass


class ICatalogScraper(ABC):
    """Interface for web scraping."""
    
    @abstractmethod
    async def scrape_catalog(self, url: str) -> str:
        pass
