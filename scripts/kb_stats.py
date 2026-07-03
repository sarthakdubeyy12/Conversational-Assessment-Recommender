#!/usr/bin/env python3
"""
Display knowledge base statistics.

Shows collection stats and metadata coverage.
"""

import asyncio
import sys
from pathlib import Path
from collections import Counter

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.catalog.infrastructure.json_repository import JSONCatalogRepository
from src.knowledge_base.vector_store.chroma_client import ChromaVectorStore
from src.knowledge_base.embeddings.provider import SentenceTransformerProvider
from src.shared.config.settings import get_settings
from src.shared.logging.logger import setup_logger

# Setup logging
setup_logger("kb_stats", level="WARNING")

settings = get_settings()


async def main():
    """Display statistics."""
    print("=" * 60)
    print("KNOWLEDGE BASE STATISTICS")
    print("=" * 60)
    print()
    
    try:
        # Load catalog
        catalog_path = settings.catalog_path
        if not Path(catalog_path).exists():
            print(f"❌ Catalog not found: {catalog_path}")
            return 1
        
        repository = JSONCatalogRepository(catalog_path)
        assessments = await repository.load()
        
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
        
        # Get count
        vector_count = await vector_store.count()
        
        # Display stats
        print("Catalog Statistics:")
        print(f"  Total assessments: {len(assessments)}")
        print()
        
        # Category distribution
        categories = Counter(a.category for a in assessments if a.category)
        print("Categories:")
        for cat, count in categories.most_common():
            print(f"  {cat}: {count}")
        print()
        
        # Test type distribution
        test_types = Counter(a.test_type for a in assessments if a.test_type)
        print("Test Types:")
        for tt, count in test_types.most_common():
            print(f"  {tt}: {count}")
        print()
        
        print("Vector Store Statistics:")
        print(f"  Collection: {settings.chroma_collection_name}")
        print(f"  Total vectors: {vector_count}")
        print(f"  Embedding dimension: {dimension}")
        print(f"  Model: {settings.embedding_model}")
        print()
        
        # Estimate avg chunks per assessment
        if len(assessments) > 0:
            avg_chunks = vector_count / len(assessments)
            print(f"  Average chunks per assessment: {avg_chunks:.1f}")
        print()
        
        # Storage info
        chroma_dir = Path(settings.chroma_persist_directory)
        if chroma_dir.exists():
            total_size = sum(
                f.stat().st_size
                for f in chroma_dir.rglob("*")
                if f.is_file()
            )
            size_mb = total_size / (1024 * 1024)
            print(f"Storage:")
            print(f"  Directory: {chroma_dir}")
            print(f"  Size: {size_mb:.2f} MB")
        print()
        
        print("=" * 60)
        print("✅ Statistics complete")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
