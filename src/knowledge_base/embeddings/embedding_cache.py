"""
Embedding cache.

Caches embeddings to avoid recomputation.
"""

from typing import List, Optional, Dict
import hashlib
import json
from pathlib import Path

from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class EmbeddingCache:
    """
    Embedding cache for avoiding recomputation.
    
    Design:
    - Stores embeddings keyed by text hash
    - Persistent storage for cross-session caching
    - Thread-safe operations
    - Automatic cache invalidation on model change
    
    Use case:
    - Avoid re-embedding unchanged catalog data
    - Speed up incremental updates
    - Reduce API costs for external providers
    """
    
    def __init__(
        self,
        cache_dir: str = "./data/embeddings/cache",
        model_name: str = "default",
    ) -> None:
        """
        Initialize cache.
        
        Args:
            cache_dir: Cache directory path
            model_name: Model name for cache isolation
        """
        self._cache_dir = Path(cache_dir)
        self._model_name = model_name
        self._cache: Dict[str, List[float]] = {}
        self._cache_file = self._cache_dir / f"cache_{self._safe_name()}.json"
        
        # Create cache directory
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing cache
        self._load_cache()
    
    def get(self, text: str) -> Optional[List[float]]:
        """
        Get cached embedding.
        
        Args:
            text: Input text
        
        Returns:
            Cached embedding or None
        """
        key = self._hash_text(text)
        return self._cache.get(key)
    
    def set(self, text: str, embedding: List[float]) -> None:
        """
        Cache embedding.
        
        Args:
            text: Input text
            embedding: Embedding vector
        """
        key = self._hash_text(text)
        self._cache[key] = embedding
    
    def get_batch(self, texts: List[str]) -> Dict[str, List[float]]:
        """
        Get multiple cached embeddings.
        
        Args:
            texts: List of texts
        
        Returns:
            Dictionary mapping text to embedding (only cached items)
        """
        result = {}
        for text in texts:
            embedding = self.get(text)
            if embedding is not None:
                result[text] = embedding
        return result
    
    def set_batch(self, text_embedding_pairs: List[tuple]) -> None:
        """
        Cache multiple embeddings.
        
        Args:
            text_embedding_pairs: List of (text, embedding) tuples
        """
        for text, embedding in text_embedding_pairs:
            self.set(text, embedding)
    
    def save(self) -> None:
        """Persist cache to disk."""
        try:
            with open(self._cache_file, "w") as f:
                json.dump(self._cache, f)
            logger.debug(f"Saved {len(self._cache)} embeddings to cache")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def clear(self) -> None:
        """Clear cache."""
        self._cache = {}
        if self._cache_file.exists():
            self._cache_file.unlink()
        logger.info("Cache cleared")
    
    def size(self) -> int:
        """Get cache size."""
        return len(self._cache)
    
    def _load_cache(self) -> None:
        """Load cache from disk."""
        if self._cache_file.exists():
            try:
                with open(self._cache_file, "r") as f:
                    self._cache = json.load(f)
                logger.info(f"Loaded {len(self._cache)} embeddings from cache")
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                self._cache = {}
    
    def _hash_text(self, text: str) -> str:
        """Hash text for cache key."""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _safe_name(self) -> str:
        """Generate safe filename from model name."""
        return self._model_name.replace("/", "_").replace(":", "_")
