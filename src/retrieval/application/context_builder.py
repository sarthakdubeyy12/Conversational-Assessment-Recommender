"""Context assembly logic."""

from typing import List

from src.retrieval.domain.entities import RetrievalResult


class ContextBuilder:
    """Assembles retrieval results into LLM context."""
    
    def build_context(self, results: List[RetrievalResult]) -> str:
        pass
