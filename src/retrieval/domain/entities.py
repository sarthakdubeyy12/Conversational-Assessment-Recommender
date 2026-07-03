"""Retrieval domain entities."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass(frozen=True)
class SearchQuery:
    """Search query entity."""
    
    text: str
    filters: Dict[str, Any]
    top_k: int = 10


@dataclass(frozen=True)
class RetrievalResult:
    """Single retrieval result."""
    
    assessment_id: str
    score: float
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class RetrievalContext:
    """Aggregated retrieval context."""
    
    query: SearchQuery
    results: List[RetrievalResult]
    total_results: int
