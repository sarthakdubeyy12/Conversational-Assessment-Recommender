"""Retrieval domain entities."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass(frozen=True)
class SearchQuery:
    """Search query entity."""
    
    text: str
    filters: Dict[str, Any] = field(default_factory=dict)
    top_k: int = 10
    similarity_threshold: float = 0.0


@dataclass(frozen=True)
class RetrievalResult:
    """
    Enhanced retrieval result.
    
    Contains complete information for rendering recommendations.
    """
    
    # Identification
    chunk_id: str
    document_id: str
    assessment_id: str
    
    # Content
    text: str
    assessment_name: str
    url: str
    
    # Relevance
    similarity_score: float
    distance: float
    
    # Metadata
    chunk_type: str
    category: Optional[str] = None
    test_type: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    competencies: List[str] = field(default_factory=list)
    duration_minutes: Optional[int] = None
    languages: List[str] = field(default_factory=list)
    job_levels: List[str] = field(default_factory=list)
    industries: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "assessment_id": self.assessment_id,
            "text": self.text,
            "assessment_name": self.assessment_name,
            "url": self.url,
            "similarity_score": self.similarity_score,
            "distance": self.distance,
            "chunk_type": self.chunk_type,
            "category": self.category,
            "test_type": self.test_type,
            "skills": self.skills,
            "competencies": self.competencies,
            "duration_minutes": self.duration_minutes,
            "languages": self.languages,
            "job_levels": self.job_levels,
            "industries": self.industries,
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class RetrievalContext:
    """Aggregated retrieval context."""
    
    query: SearchQuery
    results: List[RetrievalResult]
    total_results: int
