"""
Semantic search service.

Performs semantic search on knowledge base.
"""

from typing import List, Dict, Any, Optional
from src.knowledge_base.domain.interfaces import IEmbeddingProvider, IVectorStore
from src.retrieval.domain.entities import SearchQuery, RetrievalResult
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class SemanticSearchService:
    """
    Semantic search over knowledge base.
    
    Responsibilities:
    - Convert queries to embeddings
    - Perform vector search
    - Apply filters
    - Format results
    
    Design:
    - Query embedding caching
    - Metadata filtering support
    - Similarity thresholding
    - Result deduplication by assessment
    """
    
    def __init__(
        self,
        embedding_provider: IEmbeddingProvider,
        vector_store: IVectorStore,
    ) -> None:
        """
        Initialize search service.
        
        Args:
            embedding_provider: Embedding provider
            vector_store: Vector store
        """
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
    
    async def search(
        self,
        query: SearchQuery,
    ) -> List[RetrievalResult]:
        """
        Perform semantic search.
        
        Args:
            query: Search query
        
        Returns:
            List of retrieval results
        """
        logger.info(f"Semantic search: '{query.text}' (top_k={query.top_k})")
        
        # Generate query embedding
        query_embedding = self._embedding_provider.embed_text(query.text)
        
        # Perform vector search
        raw_results = await self._vector_store.search(
            query_embedding=query_embedding,
            top_k=query.top_k,
            filters=query.filters if query.filters else None,
        )
        
        # Format results
        results = self._format_results(raw_results)
        
        # Apply similarity threshold
        if query.similarity_threshold > 0:
            results = [
                r for r in results
                if r.similarity_score >= query.similarity_threshold
            ]
        
        logger.info(
            f"Search returned {len(results)} results "
            f"(after threshold={query.similarity_threshold})"
        )
        
        return results
    
    def _format_results(
        self,
        raw_results: List[Dict[str, Any]],
    ) -> List[RetrievalResult]:
        """Format raw results into RetrievalResult objects."""
        results = []
        
        for raw in raw_results:
            metadata = raw.get("metadata", {})
            
            # Parse comma-separated lists
            skills = self._parse_list(metadata.get("skills", ""))
            competencies = self._parse_list(metadata.get("competencies", ""))
            languages = self._parse_list(metadata.get("languages", ""))
            job_levels = self._parse_list(metadata.get("job_levels", ""))
            industries = self._parse_list(metadata.get("industries", ""))
            tags = self._parse_list(metadata.get("tags", ""))
            
            result = RetrievalResult(
                chunk_id=raw.get("chunk_id", ""),
                document_id=metadata.get("document_id", ""),
                assessment_id=metadata.get("assessment_id", ""),
                text=raw.get("text", ""),
                assessment_name=metadata.get("assessment_name", ""),
                url=metadata.get("url", ""),
                similarity_score=raw.get("similarity", 0.0),
                distance=raw.get("distance", 0.0),
                chunk_type=metadata.get("chunk_type", ""),
                category=metadata.get("category"),
                test_type=metadata.get("test_type"),
                skills=skills,
                competencies=competencies,
                duration_minutes=metadata.get("duration_minutes"),
                languages=languages,
                job_levels=job_levels,
                industries=industries,
                tags=tags,
                metadata=metadata,
            )
            results.append(result)
        
        return results
    
    def _parse_list(self, value: str) -> List[str]:
        """Parse comma-separated list."""
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]
