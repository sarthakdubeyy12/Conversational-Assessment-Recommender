"""Query construction logic."""

from typing import Dict, Any

from src.retrieval.domain.entities import SearchQuery


class QueryBuilder:
    """Builds search queries from user requirements."""
    
    def build_from_criteria(self, text: str, filters: Dict[str, Any]) -> SearchQuery:
        pass
