"""Embedding model implementation."""

from typing import List

from src.retrieval.domain.interfaces import IEmbedder


class SentenceTransformerEmbedder(IEmbedder):
    """sentence-transformers implementation."""
    
    def __init__(self, model_name: str) -> None:
        self._model_name = model_name
    
    def embed_text(self, text: str) -> List[float]:
        pass
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass
