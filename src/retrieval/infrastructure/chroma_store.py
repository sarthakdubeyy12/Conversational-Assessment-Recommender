"""ChromaDB vector store implementation."""

from typing import List

from src.retrieval.domain.entities import SearchQuery, RetrievalResult
from src.retrieval.domain.interfaces import IVectorStore


class ChromaVectorStore(IVectorStore):
    """ChromaDB implementation of vector store."""
    
    def __init__(self, collection_name: str, persist_directory: str) -> None:
        self._collection_name = collection_name
        self._persist_directory = persist_directory
    
    async def search(self, query: SearchQuery) -> List[RetrievalResult]:
        pass
    
    async def add_documents(self, documents: List[dict]) -> None:
        pass
