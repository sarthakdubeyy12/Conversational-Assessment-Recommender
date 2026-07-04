"""
Embedding provider implementation.

Implements sentence-transformers embedding generation.
"""

from typing import List
from sentence_transformers import SentenceTransformer

from src.knowledge_base.domain.interfaces import IEmbeddingProvider
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class SentenceTransformerProvider(IEmbeddingProvider):
    """
    Sentence Transformers embedding provider.
    
    Supports any sentence-transformers model from HuggingFace.
    
    Recommended models:
    - all-MiniLM-L6-v2: Fast, 384 dimensions, good for retrieval
    - all-mpnet-base-v2: Better quality, 768 dimensions
    - bge-base-en-v1.5: State-of-the-art, 768 dimensions
    
    Design:
    - Lazy loading (model loaded on first use)
    - Thread-safe embedding generation
    - Batch processing support
    - Device selection (CPU/GPU)
    """
    
    def __init__(self, model_name: str, device: str = "cpu") -> None:
        """
        Initialize provider.
        
        Args:
            model_name: HuggingFace model name
            device: Device to use ('cpu' or 'cuda')
        """
        self._model_name = model_name
        self._device = device
        self._model = None
        self._dimension = None
        
        logger.info(
            f"Initialized SentenceTransformerProvider: "
            f"model={model_name}, device={device}"
        )
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for single text.
        
        Args:
            text: Input text
        
        Returns:
            Embedding vector
        """
        self._ensure_loaded()
        
        embedding = self._model.encode(
            text,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
        
        Returns:
            List of embedding vectors
        """
        self._ensure_loaded()
        
        if not texts:
            return []
        
        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 100,
            batch_size=32,
        )
        
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """
        Get embedding dimension.
        
        Returns:
            Embedding dimension
        """
        self._ensure_loaded()
        return self._dimension
    
    def _ensure_loaded(self) -> None:
        """Ensure model is loaded."""
        if self._model is None:
            logger.info(f"Loading model: {self._model_name}")
            self._model = SentenceTransformer(
                self._model_name,
                device=self._device,
            )
            # Use the new method name (renamed in newer versions)
            try:
                self._dimension = self._model.get_embedding_dimension()
            except AttributeError:
                # Fallback to old method name for compatibility
                self._dimension = self._model.get_sentence_embedding_dimension()
            logger.info(
                f"Model loaded: dimension={self._dimension}, "
                f"max_seq_length={self._model.max_seq_length}"
            )
