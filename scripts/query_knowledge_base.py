#!/usr/bin/env python3
"""
Query knowledge base interactively.

Test semantic search with custom queries.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.knowledge_base.embeddings.provider import SentenceTransformerProvider
from src.knowledge_base.vector_store.chroma_client import ChromaVectorStore
from src.knowledge_base.semantic_search import SemanticSearchService
from src.retrieval.domain.entities import SearchQuery
from src.shared.config.settings import get_settings
from src.shared.logging.logger import get_logger, setup_logger

# Setup logging
setup_logger("kb_query", level="WARNING")  # Less verbose for interactive use
logger = get_logger(__name__)

settings = get_settings()


async def main():
    """Interactive query interface."""
    print("=" * 60)
    print("KNOWLEDGE BASE QUERY")
    print("=" * 60)
    print()
    
    # Get query from command line or prompt
    if len(sys.argv) > 1:
        query_text = " ".join(sys.argv[1:])
    else:
        print("Enter search query (or press Ctrl+C to exit):")
        try:
            query_text = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            return 0
    
    if not query_text:
        print("Error: Empty query")
        return 1
    
    try:
        # Initialize components
        embedding_provider = SentenceTransformerProvider(
            model_name=settings.embedding_model,
            device="cpu",
        )
        
        vector_store = ChromaVectorStore(
            persist_directory=settings.chroma_persist_directory,
            collection_name=settings.chroma_collection_name,
        )
        
        # Load collection
        dimension = embedding_provider.get_dimension()
        await vector_store.create_collection(settings.chroma_collection_name, dimension)
        
        search_service = SemanticSearchService(
            embedding_provider=embedding_provider,
            vector_store=vector_store,
        )
        
        # Perform search
        print(f"\nSearching for: '{query_text}'")
        print()
        
        query = SearchQuery(
            text=query_text,
            top_k=5,
            similarity_threshold=0.0,
        )
        
        results = await search_service.search(query)
        
        # Display results
        print(f"Found {len(results)} results:")
        print()
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.assessment_name}")
            print(f"   Similarity: {result.similarity_score:.3f}")
            print(f"   Category: {result.category}")
            print(f"   Type: {result.test_type}")
            if result.skills:
                print(f"   Skills: {', '.join(result.skills[:3])}")
            print(f"   URL: {result.url}")
            print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Query failed: {e}")
        logger.error(f"Query error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
