#!/usr/bin/env python3
"""
Quick demo of knowledge base functionality.

Tests document building, chunking, and embedding without full indexing.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.catalog.domain.entities import Assessment
from src.knowledge_base.document_builder import DocumentBuilder
from src.knowledge_base.semantic_chunker import SemanticChunker
from src.knowledge_base.embeddings.provider import SentenceTransformerProvider
from src.shared.logging.logger import get_logger, setup_logger

# Setup logging
setup_logger("kb_demo", level="INFO")
logger = get_logger(__name__)


def main():
    """Run demo."""
    logger.info("=" * 60)
    logger.info("KNOWLEDGE BASE DEMO")
    logger.info("=" * 60)
    logger.info("")
    
    try:
        # Create demo assessment
        assessment = Assessment(
            id="demo_assessment",
            name="Verify G+ Cognitive Assessment",
            url="https://www.shl.com/solutions/products/assessments/verify-g-plus/",
            description="Comprehensive cognitive ability test measuring abstract reasoning, "
                       "numerical reasoning, and deductive reasoning skills.",
            category="Cognitive Ability",
            test_type="Reasoning",
            skills_measured=["Abstract Reasoning", "Numerical Analysis", "Deductive Reasoning"],
            competencies=["Problem Solving", "Critical Thinking", "Analytical Skills"],
            duration_minutes=30,
            languages=["English", "Spanish", "French"],
            job_levels=["Entry Level", "Mid Level", "Senior Level"],
            industries=["Technology", "Finance", "Consulting"],
            tags=["Cognitive", "Reasoning", "Assessment"],
        )
        
        # Step 1: Build document
        logger.info("Step 1: Building document...")
        builder = DocumentBuilder()
        documents = builder.build_documents([assessment])
        logger.info(f"✅ Built {len(documents)} document(s)")
        logger.info(f"   Content preview: {documents[0].content[:100]}...")
        logger.info("")
        
        # Step 2: Chunk document
        logger.info("Step 2: Chunking document...")
        chunker = SemanticChunker()
        chunks = chunker.chunk_documents(documents)
        logger.info(f"✅ Created {len(chunks)} chunks")
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"   Chunk {i} ({chunk.chunk_type}): {chunk.text[:60]}...")
        logger.info("")
        
        # Step 3: Generate embeddings
        logger.info("Step 3: Generating embeddings...")
        provider = SentenceTransformerProvider(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            device="cpu",
        )
        
        texts = [chunk.text for chunk in chunks]
        embeddings = provider.embed_batch(texts)
        
        logger.info(f"✅ Generated {len(embeddings)} embeddings")
        logger.info(f"   Dimension: {provider.get_dimension()}")
        logger.info(f"   Sample embedding shape: {len(embeddings[0])}")
        logger.info("")
        
        # Success
        logger.info("=" * 60)
        logger.info("✅ DEMO COMPLETE")
        logger.info("=" * 60)
        logger.info("")
        logger.info("All components working correctly!")
        logger.info("")
        logger.info("Next: Build full knowledge base:")
        logger.info("  docker exec <container> python3 scripts/build_knowledge_base.py")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
