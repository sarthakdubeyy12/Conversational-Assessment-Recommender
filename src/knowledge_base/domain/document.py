"""
Document entity for knowledge base.

Represents searchable document with full metadata preservation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass(frozen=True)
class Document:
    """
    Knowledge base document.
    
    Represents a single searchable unit in the knowledge base.
    Each assessment can generate one or more documents.
    
    Preserves all metadata required for:
    - Semantic search
    - Metadata filtering
    - Recommendation
    - Comparison
    - Result rendering
    """
    
    # Document identification
    document_id: str
    assessment_id: str
    
    # Content
    content: str
    content_type: str  # "overview", "skills", "details", "full"
    
    # Assessment core fields
    assessment_name: str
    url: str
    
    # Metadata for filtering and ranking
    description: Optional[str] = None
    category: Optional[str] = None
    test_type: Optional[str] = None
    skills_measured: List[str] = field(default_factory=list)
    competencies: List[str] = field(default_factory=list)
    duration_minutes: Optional[int] = None
    languages: List[str] = field(default_factory=list)
    job_levels: List[str] = field(default_factory=list)
    industries: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "document_id": self.document_id,
            "assessment_id": self.assessment_id,
            "content": self.content,
            "content_type": self.content_type,
            "assessment_name": self.assessment_name,
            "url": self.url,
            "description": self.description,
            "category": self.category,
            "test_type": self.test_type,
            "skills_measured": self.skills_measured,
            "competencies": self.competencies,
            "duration_minutes": self.duration_minutes,
            "languages": self.languages,
            "job_levels": self.job_levels,
            "industries": self.industries,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class DocumentChunk:
    """
    Document chunk with metadata.
    
    Represents a semantically meaningful chunk of a document.
    Preserves context and lineage for reconstruction.
    """
    
    # Chunk identification
    chunk_id: str
    document_id: str
    assessment_id: str
    chunk_index: int
    
    # Content
    text: str
    chunk_type: str  # "overview", "skills", "description", "metadata"
    
    # Context preservation
    assessment_name: str
    url: str
    
    # Metadata (inherited from document)
    category: Optional[str] = None
    test_type: Optional[str] = None
    skills_measured: List[str] = field(default_factory=list)
    competencies: List[str] = field(default_factory=list)
    duration_minutes: Optional[int] = None
    languages: List[str] = field(default_factory=list)
    job_levels: List[str] = field(default_factory=list)
    industries: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for vector store."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "assessment_id": self.assessment_id,
            "chunk_index": self.chunk_index,
            "text": self.text,
            "chunk_type": self.chunk_type,
            "assessment_name": self.assessment_name,
            "url": self.url,
            "category": self.category,
            "test_type": self.test_type,
            "skills_measured": self.skills_measured,
            "competencies": self.competencies,
            "duration_minutes": self.duration_minutes,
            "languages": self.languages,
            "job_levels": self.job_levels,
            "industries": self.industries,
            "tags": self.tags,
            "metadata": self.metadata,
        }
