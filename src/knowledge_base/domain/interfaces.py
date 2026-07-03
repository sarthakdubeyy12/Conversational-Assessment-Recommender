"""
Knowledge Base domain interfaces.

Defines contracts for knowledge base operations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

from src.knowledge_base.domain.document import Document, DocumentChunk
from src.catalog.domain.entities import Assessment


class IDocumentBuilder(ABC):
    """
    Interface for document building.
    
    Transforms assessments into searchable documents.
    """
    
    @abstractmethod
    def build_documents(self, assessments: List[Assessment]) -> List[Document]:
        """
        Build documents from assessments.
        
        Args:
            assessments: List of assessments
        
        Returns:
            List of documents
        """
        pass


class ISemanticChunker(ABC):
    """
    Interface for semantic chunking.
    
    Splits documents into meaningful chunks.
    """
    
    @abstractmethod
    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """
        Chunk document into smaller units.
        
        Args:
            document: Document to chunk
        
        Returns:
            List of chunks
        """
        pass
    
    @abstractmethod
    def chunk_documents(self, documents: List[Document]) -> List[DocumentChunk]:
        """
        Chunk multiple documents.
        
        Args:
            documents: Documents to chunk
        
        Returns:
            List of all chunks
        """
        pass


class IEmbeddingProvider(ABC):
    """
    Interface for embedding generation.
    
    Provider-agnostic embedding interface.
    """
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for single text.
        
        Args:
            text: Input text
        
        Returns:
            Embedding vector
        """
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
        
        Returns:
            List of embedding vectors
        """
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get embedding dimension.
        
        Returns:
            Embedding dimension
        """
        pass


class IVectorStore(ABC):
    """
    Interface for vector storage.
    
    Database-agnostic vector store interface.
    """
    
    @abstractmethod
    async def create_collection(self, name: str, dimension: int) -> None:
        """Create or load collection."""
        pass
    
    @abstractmethod
    async def add_chunks(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]],
    ) -> None:
        """Add chunks with embeddings."""
        pass
    
    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int,
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks."""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Get total count."""
        pass
    
    @abstractmethod
    async def delete_all(self) -> None:
        """Delete all vectors."""
        pass
