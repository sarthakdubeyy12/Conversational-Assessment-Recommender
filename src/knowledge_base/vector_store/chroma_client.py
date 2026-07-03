"""
ChromaDB vector store implementation.

Production-grade ChromaDB integration.
"""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

from src.knowledge_base.domain.interfaces import IVectorStore
from src.knowledge_base.domain.document import DocumentChunk
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ChromaVectorStore(IVectorStore):
    """
    ChromaDB vector store implementation.
    
    Responsibilities:
    - Manage ChromaDB client and collection
    - Store chunks with embeddings and metadata
    - Perform similarity search
    - Support metadata filtering
    - Persistent storage
    
    Design:
    - Persistent client with local storage
    - Rich metadata storage for filtering
    - Batch operations for efficiency
    - Automatic collection creation
    """
    
    def __init__(
        self,
        persist_directory: str,
        collection_name: str,
    ) -> None:
        """
        Initialize ChromaDB client.
        
        Args:
            persist_directory: Directory for persistent storage
            collection_name: Collection name
        """
        self._persist_directory = persist_directory
        self._collection_name = collection_name
        self._client = None
        self._collection = None
        
        logger.info(
            f"Initialized ChromaVectorStore: "
            f"dir={persist_directory}, collection={collection_name}"
        )
    
    async def create_collection(self, name: str, dimension: int) -> None:
        """
        Create or load collection.
        
        Args:
            name: Collection name
            dimension: Embedding dimension (not used by Chroma)
        """
        self._ensure_client()
        
        # Get or create collection
        self._collection = self._client.get_or_create_collection(
            name=name,
            metadata={"dimension": dimension},
        )
        
        count = self._collection.count()
        logger.info(
            f"Collection '{name}' ready: {count} existing vectors, "
            f"dimension={dimension}"
        )
    
    async def add_chunks(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]],
    ) -> None:
        """
        Add chunks with embeddings.
        
        Args:
            chunks: Document chunks
            embeddings: Corresponding embeddings
        """
        if not chunks or not embeddings:
            return
        
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings length mismatch")
        
        self._ensure_collection()
        
        # Prepare data for ChromaDB
        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [self._prepare_metadata(chunk) for chunk in chunks]
        
        # Add to collection (ChromaDB handles batching)
        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        
        logger.info(f"Added {len(chunks)} chunks to collection")
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results
            filters: Metadata filters (ChromaDB where clause)
        
        Returns:
            List of search results with metadata
        """
        self._ensure_collection()
        
        # Perform search
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filters if filters else None,
        )
        
        # Format results
        formatted_results = self._format_results(results)
        
        logger.debug(
            f"Search returned {len(formatted_results)} results "
            f"(top_k={top_k}, filters={filters})"
        )
        
        return formatted_results
    
    async def count(self) -> int:
        """Get total vector count."""
        self._ensure_collection()
        return self._collection.count()
    
    async def delete_all(self) -> None:
        """Delete all vectors."""
        self._ensure_client()
        
        try:
            self._client.delete_collection(name=self._collection_name)
            logger.info(f"Deleted collection '{self._collection_name}'")
            self._collection = None
        except Exception as e:
            logger.warning(f"Failed to delete collection: {e}")
    
    def _ensure_client(self) -> None:
        """Ensure ChromaDB client is initialized."""
        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=self._persist_directory,
                settings=Settings(anonymized_telemetry=False),
            )
            logger.debug("ChromaDB client initialized")
    
    def _ensure_collection(self) -> None:
        """Ensure collection is loaded."""
        if self._collection is None:
            raise RuntimeError(
                "Collection not initialized. Call create_collection() first."
            )
    
    def _prepare_metadata(self, chunk: DocumentChunk) -> Dict[str, Any]:
        """
        Prepare metadata for ChromaDB.
        
        ChromaDB supports: str, int, float, bool
        """
        metadata = {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "assessment_id": chunk.assessment_id,
            "assessment_name": chunk.assessment_name,
            "url": chunk.url,
            "chunk_type": chunk.chunk_type,
            "chunk_index": chunk.chunk_index,
        }
        
        # Add optional fields
        if chunk.category:
            metadata["category"] = chunk.category
        if chunk.test_type:
            metadata["test_type"] = chunk.test_type
        if chunk.duration_minutes:
            metadata["duration_minutes"] = chunk.duration_minutes
        
        # Lists as comma-separated strings
        if chunk.skills_measured:
            metadata["skills"] = ",".join(chunk.skills_measured)
        if chunk.competencies:
            metadata["competencies"] = ",".join(chunk.competencies)
        if chunk.languages:
            metadata["languages"] = ",".join(chunk.languages)
        if chunk.job_levels:
            metadata["job_levels"] = ",".join(chunk.job_levels)
        if chunk.industries:
            metadata["industries"] = ",".join(chunk.industries)
        if chunk.tags:
            metadata["tags"] = ",".join(chunk.tags)
        
        return metadata
    
    def _format_results(self, results: Dict) -> List[Dict[str, Any]]:
        """Format ChromaDB results."""
        formatted = []
        
        # ChromaDB returns results in nested lists
        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        
        for i, chunk_id in enumerate(ids):
            formatted.append({
                "chunk_id": chunk_id,
                "distance": distances[i],
                "similarity": 1 - distances[i],  # Convert distance to similarity
                "text": documents[i],
                "metadata": metadatas[i],
            })
        
        return formatted
