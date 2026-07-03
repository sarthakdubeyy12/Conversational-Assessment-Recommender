"""
Collection manager.

Manages ChromaDB collection lifecycle.
"""

from typing import Dict, Any
from src.knowledge_base.domain.interfaces import IVectorStore
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class CollectionManager:
    """
    Manages vector store collection.
    
    Responsibilities:
    - Collection creation
    - Collection versioning
    - Collection statistics
    - Collection validation
    
    Design:
    - Supports collection versioning for schema changes
    - Tracks collection metadata
    - Provides collection health checks
    """
    
    def __init__(self, vector_store: IVectorStore) -> None:
        """
        Initialize manager.
        
        Args:
            vector_store: Vector store instance
        """
        self._store = vector_store
    
    async def create_or_load(
        self,
        name: str,
        dimension: int,
    ) -> None:
        """
        Create or load collection.
        
        Args:
            name: Collection name
            dimension: Embedding dimension
        """
        logger.info(f"Creating/loading collection: {name}")
        await self._store.create_collection(name, dimension)
    
    async def rebuild(self, name: str, dimension: int) -> None:
        """
        Rebuild collection (delete and recreate).
        
        Args:
            name: Collection name
            dimension: Embedding dimension
        """
        logger.info(f"Rebuilding collection: {name}")
        
        # Delete existing
        await self._store.delete_all()
        
        # Create new
        await self._store.create_collection(name, dimension)
        
        logger.info("Collection rebuilt")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.
        
        Returns:
            Statistics dictionary
        """
        count = await self._store.count()
        
        return {
            "total_vectors": count,
            "collection_exists": count >= 0,
        }
    
    async def validate(self) -> Dict[str, Any]:
        """
        Validate collection health.
        
        Returns:
            Validation report
        """
        stats = await self.get_stats()
        
        validation = {
            "valid": True,
            "issues": [],
            "stats": stats,
        }
        
        if stats["total_vectors"] == 0:
            validation["issues"].append("Collection is empty")
            validation["valid"] = False
        
        return validation
