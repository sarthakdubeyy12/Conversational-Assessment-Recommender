"""
Pipeline factory.

Creates configured retrieval pipeline instances.
"""

from src.knowledge_base.semantic_search import SemanticSearchService
from src.knowledge_base.domain.interfaces import IEmbeddingProvider, IVectorStore
from src.retrieval.pipeline.retrieval_pipeline import RetrievalPipeline
from src.retrieval.pipeline.query.query_builder import ProductionQueryBuilder
from src.retrieval.pipeline.filters.metadata_filter_builder import MetadataFilterBuilder
from src.retrieval.pipeline.ranking.hybrid_ranker import HybridRanker
from src.retrieval.pipeline.compression.duplicate_remover import DuplicateRemover
from src.retrieval.pipeline.compression.context_compressor import ContextCompressor
from src.retrieval.pipeline.validation.retrieval_validator import RetrievalValidator
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class PipelineFactory:
    """
    Factory for creating configured pipelines.
    
    Responsibilities:
    - Wire up pipeline dependencies
    - Configure components
    - Provide production instances
    
    Design:
    - Dependency injection
    - Configuration management
    - Single point of creation
    """
    
    @staticmethod
    def create_production_pipeline(
        embedding_provider: IEmbeddingProvider,
        vector_store: IVectorStore,
        top_k: int = 20,
        max_assessments: int = 5,
    ) -> RetrievalPipeline:
        """
        Create production retrieval pipeline.
        
        Args:
            embedding_provider: Embedding provider
            vector_store: Vector store
            top_k: Number of chunks to retrieve
            max_assessments: Max assessments in compressed context
        
        Returns:
            Configured retrieval pipeline
        """
        logger.info("Creating production retrieval pipeline")
        
        # Create semantic search service
        semantic_search = SemanticSearchService(
            embedding_provider=embedding_provider,
            vector_store=vector_store,
        )
        
        # Create pipeline components
        query_builder = ProductionQueryBuilder()
        filter_builder = MetadataFilterBuilder()
        
        ranker = HybridRanker(
            semantic_weight=0.5,
            metadata_weight=0.3,
            skill_weight=0.2,
        )
        
        duplicate_remover = DuplicateRemover()
        
        compressor = ContextCompressor(
            max_assessments=max_assessments,
        )
        
        validator = RetrievalValidator(
            min_similarity=0.3,
            min_results=1,
        )
        
        # Assemble pipeline
        pipeline = RetrievalPipeline(
            semantic_search=semantic_search,
            query_builder=query_builder,
            filter_builder=filter_builder,
            ranker=ranker,
            duplicate_remover=duplicate_remover,
            compressor=compressor,
            validator=validator,
            top_k=top_k,
        )
        
        logger.info("Production pipeline created successfully")
        return pipeline
