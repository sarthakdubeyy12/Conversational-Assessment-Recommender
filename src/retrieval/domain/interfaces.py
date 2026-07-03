"""Retrieval domain interfaces."""

from abc import ABC, abstractmethod
from typing import List

from src.retrieval.domain.entities import SearchQuery, RetrievalResult


class IVectorStore(ABC):
    """Interface for vector database."""
    
    @abstractmethod
    async def search(self, query: SearchQuery) -> List[RetrievalResult]:
        pass
    
    @abstractmethod
    async def add_documents(self, documents: List[dict]) -> None:
        pass


class IEmbedder(ABC):
    """Interface for embedding models."""
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass


class IRetriever(ABC):
    """Interface for retrieval strategies."""
    
    @abstractmethod
    async def retrieve(self, query: SearchQuery) -> List[RetrievalResult]:
        pass
