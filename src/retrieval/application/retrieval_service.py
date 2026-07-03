"""Retrieval service orchestration."""

from typing import List

from src.retrieval.domain.entities import SearchQuery, RetrievalContext, RetrievalResult
from src.retrieval.domain.interfaces import IRetriever


class RetrievalService:
    """Orchestrates retrieval operations."""
    
    def __init__(self, retriever: IRetriever) -> None:
        self._retriever = retriever
    
    async def retrieve_assessments(self, query: SearchQuery) -> RetrievalContext:
        results = await self._retriever.retrieve(query)
        return RetrievalContext(
            query=query,
            results=results,
            total_results=len(results)
        )
