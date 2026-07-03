"""Hybrid search implementation."""

from typing import List

from src.retrieval.domain.entities import SearchQuery, RetrievalResult
from src.retrieval.domain.interfaces import IRetriever


class HybridRetriever(IRetriever):
    """Combines semantic and metadata search."""
    
    async def retrieve(self, query: SearchQuery) -> List[RetrievalResult]:
        pass
