"""
Catalog domain interfaces.

Defines contracts for catalog operations following dependency inversion.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Set
from src.catalog.domain.entities import Assessment, ScrapedPage


class ICatalogRepository(ABC):
    """
    Interface for catalog persistence.
    
    Handles loading and saving the catalog dataset.
    """
    
    @abstractmethod
    async def save(self, assessments: List[Assessment]) -> None:
        """Save assessments to storage."""
        pass
    
    @abstractmethod
    async def load(self) -> List[Assessment]:
        """Load all assessments from storage."""
        pass
    
    @abstractmethod
    async def find_by_id(self, assessment_id: str) -> Optional[Assessment]:
        """Find assessment by ID."""
        pass
    
    @abstractmethod
    async def exists(self) -> bool:
        """Check if catalog exists."""
        pass


class IWebScraper(ABC):
    """
    Interface for web scraping.
    
    Handles HTTP requests, retries, rate limiting.
    """
    
    @abstractmethod
    async def fetch_page(self, url: str) -> ScrapedPage:
        """Fetch single page with retry logic."""
        pass
    
    @abstractmethod
    async def fetch_pages(self, urls: List[str]) -> List[ScrapedPage]:
        """Fetch multiple pages with rate limiting."""
        pass


class ILinkDiscoverer(ABC):
    """
    Interface for discovering assessment links.
    
    Crawls catalog to find all assessment URLs.
    """
    
    @abstractmethod
    async def discover_assessment_links(self, start_url: str) -> Set[str]:
        """Discover all valid assessment URLs from catalog."""
        pass


class IHTMLParser(ABC):
    """
    Interface for HTML parsing.
    
    Extracts structured data from raw HTML.
    """
    
    @abstractmethod
    def parse(self, page: ScrapedPage) -> Optional[Assessment]:
        """Parse HTML page to extract assessment data."""
        pass


class IAssessmentValidator(ABC):
    """
    Interface for assessment validation.
    
    Validates assessment data quality and completeness.
    """
    
    @abstractmethod
    def validate(self, assessment: Assessment) -> bool:
        """Validate assessment. Returns True if valid."""
        pass
    
    @abstractmethod
    def get_validation_errors(self, assessment: Assessment) -> List[str]:
        """Get list of validation errors."""
        pass


class IDataNormalizer(ABC):
    """
    Interface for data normalization.
    
    Cleans, standardizes, and normalizes assessment data.
    """
    
    @abstractmethod
    def normalize(self, assessment: Assessment) -> Assessment:
        """Normalize assessment data."""
        pass
