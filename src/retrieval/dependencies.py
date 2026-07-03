"""Retrieval dependency injection."""

from src.retrieval.application.retrieval_service import RetrievalService
from src.retrieval.infrastructure.hybrid_search import HybridRetriever
from src.shared.config.settings import Settings


def get_retrieval_service() -> RetrievalService:
    """Factory for retrieval service."""
    settings = Settings()
    retriever = HybridRetriever()
    return RetrievalService(retriever=retriever)
