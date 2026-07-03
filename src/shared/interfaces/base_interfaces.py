"""
Base shared interfaces.

Abstract interfaces for dependency inversion.
These define contracts that implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic


T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """
    Base repository interface.
    
    Generic repository pattern for data persistence.
    """
    
    @abstractmethod
    async def save(self, entity: T) -> None:
        """Save entity to repository."""
        pass
    
    @abstractmethod
    async def load(self) -> List[T]:
        """Load all entities from repository."""
        pass
    
    @abstractmethod
    async def find_by_id(self, entity_id: str) -> Optional[T]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> None:
        """Delete entity by ID."""
        pass


class IService(ABC):
    """
    Base service interface.
    
    Marker interface for application services.
    """
    pass


class ILLMProvider(ABC):
    """
    Interface for LLM providers.
    
    Abstracts different LLM implementations (OpenAI, Gemini, Groq).
    """
    
    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2000
    ) -> str:
        """Generate completion from messages."""
        pass
    
    @abstractmethod
    async def generate_streaming(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2000
    ):
        """Generate completion with streaming."""
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        pass


class IEmbeddingProvider(ABC):
    """
    Interface for embedding providers.
    
    Abstracts different embedding implementations.
    """
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts."""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        pass


class IVectorStore(ABC):
    """
    Interface for vector databases.
    
    Abstracts different vector store implementations (ChromaDB, Pinecone, etc).
    """
    
    @abstractmethod
    async def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """Add documents to vector store."""
        pass
    
    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    async def delete(self, ids: List[str]) -> None:
        """Delete documents by IDs."""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all documents."""
        pass


class ICache(ABC):
    """
    Interface for caching.
    
    Abstracts caching implementations (Redis, in-memory, etc).
    """
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache entries."""
        pass


class ILogger(ABC):
    """
    Interface for logging.
    
    Abstracts logging implementations.
    """
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        pass
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        pass
    
    @abstractmethod
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        pass
