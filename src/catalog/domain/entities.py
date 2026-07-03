"""
Catalog domain entities.

Represents SHL Individual Test Solutions as domain objects.
Rich domain model with all attributes extracted from catalog pages.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass(frozen=True)
class Assessment:
    """
    SHL Individual Test Solution entity.
    
    Represents a single assessment product from the SHL catalog.
    Immutable domain object containing all extracted metadata.
    
    This is the core entity that powers all downstream features:
    - Retrieval (embeddings, search)
    - Recommendation (matching, ranking)
    - Conversation (information retrieval)
    - Comparison (feature comparison)
    """
    
    # Required fields
    id: str
    name: str
    url: str
    
    # Core attributes
    description: Optional[str] = None
    category: Optional[str] = None
    test_type: Optional[str] = None
    
    # Skills and competencies
    skills_measured: List[str] = field(default_factory=list)
    competencies: List[str] = field(default_factory=list)
    
    # Assessment characteristics
    duration_minutes: Optional[int] = None
    question_count: Optional[int] = None
    languages: List[str] = field(default_factory=list)
    
    # Support and features
    remote_testing: bool = False
    adaptive_testing: bool = False
    mobile_compatible: bool = False
    
    # Target audience
    job_levels: List[str] = field(default_factory=list)
    suitable_roles: List[str] = field(default_factory=list)
    industries: List[str] = field(default_factory=list)
    
    # Product information
    product_code: Optional[str] = None
    assessment_family: Optional[str] = None
    version: Optional[str] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    difficulty_level: Optional[str] = None
    delivery_method: Optional[str] = None
    
    # Additional structured data
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Tracking
    scraped_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "description": self.description,
            "category": self.category,
            "test_type": self.test_type,
            "skills_measured": self.skills_measured,
            "competencies": self.competencies,
            "duration_minutes": self.duration_minutes,
            "question_count": self.question_count,
            "languages": self.languages,
            "remote_testing": self.remote_testing,
            "adaptive_testing": self.adaptive_testing,
            "mobile_compatible": self.mobile_compatible,
            "job_levels": self.job_levels,
            "suitable_roles": self.suitable_roles,
            "industries": self.industries,
            "product_code": self.product_code,
            "assessment_family": self.assessment_family,
            "version": self.version,
            "tags": self.tags,
            "difficulty_level": self.difficulty_level,
            "delivery_method": self.delivery_method,
            "metadata": self.metadata,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


@dataclass(frozen=True)
class ScrapedPage:
    """
    Represents a scraped web page.
    
    Raw page data before parsing.
    Used in the scraper → parser pipeline.
    """
    
    url: str
    html_content: str
    status_code: int
    scraped_at: datetime
    headers: Dict[str, str] = field(default_factory=dict)
