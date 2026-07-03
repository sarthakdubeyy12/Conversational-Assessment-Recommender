#!/usr/bin/env python3
"""
Validate knowledge base integrity.

Checks index quality and completeness.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.catalog.infrastructure.json_repository import JSONCatalogRepository
from src.knowledge_base.vector_store.chroma_client import ChromaVectorStore
from src.knowledge_base.vector_store.collection_manager import CollectionManager
from src.knowledge_base.embeddings.provider import SentenceTransformerProvider
from src.knowledge_base.semantic_search import SemanticSearchService
from src.retrieval.domain.entities import SearchQuery
from src.shared.config.settings import get_settings
from src.shared.logging.logger import get_logger, setup_logger

# Setup logging
setup_logger("kb_validate", level="INFO")
logger = get_logger(__name__)

settings = get_settings()


async def main():
    """Validate knowledge base."""
    logger.info("=" * 60)
    logger.info("KNOWLEDGE BASE VALIDATION")
    logger.info("=" * 60)
    logger.info("")
    
    try:
        # Load catalog
        catalog_path = settings.catalog_path
        if not Path(catalog_path).exists():
            logger.error(f"❌ Catalog not found: {catalog_path}")
            return 1
        
        repository = JSONCatalogRepository(catalog_path)
        assessments = await repository.load()
        
        # Initialize vector store
        vector_store = ChromaVectorStore(
            persist_directory=settings.chroma_persist_directory,
            collection_name=settings.chroma_collection_name,
        )
        
        # Initialize collection manager
        manager = CollectionManager(vector_store)
        
        # Create/load collection
        dimension = settings.embedding_dimension
        await manager.create_or_load(settings.chroma_collection_name, dimension)
        
        # Get statistics
        stats = await manager.get_stats()
        
        logger.info("Collection Statistics:")
        logger.info(f"  Total vectors: {stats['total_vectors']}")
        logger.info(f"  Expected assessments: {len(assessments)}")
        logger.info("")
        
        # Validate
        validation = await manager.validate()
        
        logger.info("Validation Checks:")
        for issue in validation.get("issues", []):
            logger.warning(f"  ⚠️  {issue}")
        
        if not validation.get("issues"):
            logger.info("  ✅ No issues found")
        
        logger.info("")
        
        # Test retrieval
        logger.info("Testing retrieval...")
        
        embedding_provider = SentenceTransformerProvider(
            model_name=settings.embedding_model,
            device="cpu",
        )
        
        search_service = SemanticSearchService(
            embedding_provider=embedding_provider,
            vector_store=vector_store,
        )
        
        # Test query
        test_query = SearchQuery(
            text="cognitive ability reasoning",
            top_k=3,
        )
        
        results = await search_service.search(test_query)
        
        logger.info(f"Test query returned {len(results)} results")
        
        if results:
            logger.info("")
            logger.info("Sample results:")
            for i, result in enumerate(results[:3], 1):
                logger.info(
                    f"  {i}. {result.assessment_name} "
                    f"(similarity: {result.similarity_score:.3f})"
                )
        
        logger.info("")
        
        # Overall result
        logger.info("=" * 60)
        if validation["valid"] and stats["total_vectors"] > 0:
            logger.info("✅ VALIDATION PASSED")
            logger.info("=" * 60)
            logger.info("")
            logger.info("Knowledge base is ready for use")
            return 0
        else:
            logger.warning("⚠️  VALIDATION PASSED WITH WARNINGS")
            logger.info("=" * 60)
            logger.info("")
            logger.info("Knowledge base has issues. Consider rebuilding:")
            logger.info("python scripts/build_knowledge_base.py --rebuild")
            return 0
        
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
