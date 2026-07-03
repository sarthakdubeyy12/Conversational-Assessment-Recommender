"""Reranking logic for future use."""

from typing import List

from src.retrieval.domain.entities import RetrievalResult


class RerankerService:
    """Reranks retrieval results."""
    
    def rerank(self, results: List[RetrievalResult], query: str) -> List[RetrievalResult]:
        pass
