#!/usr/bin/env python3
"""
Build knowledge base from catalog.

Transforms catalog into semantic knowledge base for retrieval.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.catalog.infrastructure.json_repository import JSONCatalogRepository
from src.knowledge_base.document_builder import DocumentBuilder
from src.knowledge_base.semantic_chunker import SemanticChunker
from src.knowledge_base.embeddings.provider import SentenceTransformerProvider
from src.knowledge_base.vector_store.chroma_client import ChromaVectorStore
from src.knowledge_base.index_builder import KnowledgeBaseIndexBuilder
from src.shared.config.settings import get_settings
from src.shared.logging.logger import get_logger, setup_logger

# Setup logging
setup_logger("kb_build", level="INFO")
logger = get_logger(__name__)

settings = get_settings()


async def main():
    """Build knowledge base."""
    logger.info("=" * 60)
    logger.info("KNOWLEDGE BASE BUILDER")
    logger.info("=" * 60)
    logger.info("")
    
    # Check catalog exists
    catalog_path = settings.catalog_path
    if not Path(catalog_path).exists():
        logger.error(f"❌ Catalog not found: {catalog_path}")
        logger.error("Run 'python scripts/build_catalog.py' first")
        return 1
    
    logger.info(f"Catalog: {catalog_path}")
    logger.info(f"Embedding model: {settings.embedding_model}")
    logger.info(f"ChromaDB: {settings.chroma_persist_directory}")
    logger.info(f"Collection: {settings.chroma_collection_name}")
    logger.info("")
    
    try:
        # Load catalog
        logger.info("Loading catalog...")
        repository = JSONCatalogRepository(catalog_path)
        assessments = await repository.load()
        logger.info(f"Loaded {len(assessments)} assessments")
        logger.info("")
        
        if not assessments:
            logger.error("❌ No assessments in catalog")
            return 1
        
        # Initialize components
        logger.info("Initializing components...")
        
        document_builder = DocumentBuilder()
        chunker = SemanticChunker(
            max_chunk_length=512,
            create_overview_chunk=True,
            create_skills_chunk=True,
            create_full_chunk=True,
        )
        embedding_provider = SentenceTransformerProvider(
            model_name=settings.embedding_model,
            device="cpu",
        )
        vector_store = ChromaVectorStore(
            persist_directory=settings.chroma_persist_directory,
            collection_name=settings.chroma_collection_name,
        )
        
        index_builder = KnowledgeBaseIndexBuilder(
            document_builder=document_builder,
            chunker=chunker,
            embedding_provider=embedding_provider,
            vector_store=vector_store,
            enable_cache=True,
        )
        
        logger.info("Components initialized")
        logger.info("")
        
        # Build index
        rebuild = "--rebuild" in sys.argv
        if rebuild:
            logger.info("⚠️  Rebuild mode: existing index will be deleted")
            logger.info("")
        
        stats = await index_builder.build_index(
            assessments=assessments,
            collection_name=settings.chroma_collection_name,
            rebuild=rebuild,
        )
        
        # Success
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ KNOWLEDGE BASE BUILD COMPLETE")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Validate index: python scripts/validate_knowledge_base.py")
        logger.info("2. Query collection: python scripts/query_knowledge_base.py")
        logger.info("3. View statistics: python scripts/kb_stats.py")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Build failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
