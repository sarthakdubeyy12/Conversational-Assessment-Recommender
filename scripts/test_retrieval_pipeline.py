#!/usr/bin/env python3
"""
Test retrieval pipeline.

Demonstrates production retrieval pipeline functionality.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.conversation.domain.entities import Message
from src.conversation.state.state_engine import ConversationStateEngine
from src.conversation.intent.intent_engine import IntentEngine
from src.knowledge_base.embeddings.provider import SentenceTransformerProvider
from src.knowledge_base.vector_store.chroma_client import ChromaVectorStore
from src.retrieval.pipeline.pipeline_factory import PipelineFactory
from src.shared.logging.logger import get_logger, setup_logger

# Setup logging
setup_logger("pipeline_test", level="INFO")
logger = get_logger(__name__)


async def test_pipeline_scenario(
    pipeline,
    state_engine,
    intent_engine,
    scenario_name: str,
    user_message: str,
):
    """Test single pipeline scenario."""
    print(f"\n{'='*70}")
    print(f"SCENARIO: {scenario_name}")
    print(f"{'='*70}")
    print(f"User Message: '{user_message}'")
    print()
    
    # Build state
    messages = [Message(role="user", content=user_message)]
    state = state_engine.reconstruct_state(messages)
    
    # Detect intent
    intent = intent_engine.detect_intent(user_message, state)
    
    print(f"Intent: {intent.primary_intent.value}")
    print(f"Requires Retrieval: {intent.requires_retrieval}")
    print()
    
    # Execute pipeline
    result = await pipeline.execute(state, intent)
    
    # Display results
    print(f"Pipeline Results:")
    print(f"  Generated Queries: {len(result.generated_queries)}")
    for idx, query in enumerate(result.generated_queries, 1):
        print(f"    {idx}. {query}")
    
    print(f"\n  Applied Filters: {len(result.applied_filters)} filters")
    if result.applied_filters:
        for key, value in result.applied_filters.items():
            print(f"    - {key}: {value}")
    
    print(f"\n  Retrieved: {result.statistics.chunks_retrieved} chunks")
    print(f"  Deduplicated: {result.statistics.assessments_final} assessments")
    print(f"  Avg Similarity: {result.statistics.avg_similarity_score:.3f}")
    print(f"  Avg Ranking Score: {result.statistics.avg_ranking_score:.3f}")
    print(f"  Compression Ratio: {result.statistics.compression_ratio:.1%}")
    print(f"  Context Tokens: {result.context_token_count}")
    
    print(f"\n  Performance:")
    print(f"    Total: {result.statistics.total_latency_ms:.1f}ms")
    print(f"    Query Build: {result.statistics.query_build_ms:.1f}ms")
    print(f"    Retrieval: {result.statistics.retrieval_ms:.1f}ms")
    print(f"    Ranking: {result.statistics.ranking_ms:.1f}ms")
    print(f"    Deduplication: {result.statistics.deduplication_ms:.1f}ms")
    print(f"    Compression: {result.statistics.compression_ms:.1f}ms")
    
    print(f"\n  Validation: {'✅ VALID' if result.is_valid else '❌ INVALID'}")
    if result.validation_warnings:
        print(f"  Warnings:")
        for warning in result.validation_warnings:
            print(f"    - {warning}")
    
    print(f"\n  Top 3 Assessments:")
    top_assessments = result.get_top_assessments(3)
    for idx, doc in enumerate(top_assessments, 1):
        print(f"    {idx}. {doc.result.assessment_name}")
        print(f"       Score: {doc.ranking_score:.3f} | Similarity: {doc.result.similarity_score:.3f}")
        print(f"       URL: {doc.result.url}")
        print(f"       Category: {doc.result.category or 'N/A'}")
        print()
    
    print(f"  Decision Rationale:")
    print(f"    {result.decision_rationale}")
    print()
    
    return result


async def main():
    """Run test scenarios."""
    logger.info("=" * 70)
    logger.info("RETRIEVAL PIPELINE TEST")
    logger.info("=" * 70)
    
    # Initialize components
    logger.info("Initializing components...")
    
    embedding_provider = SentenceTransformerProvider(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        device="cpu",
    )
    vector_store = ChromaVectorStore(
        persist_directory="data/embeddings",
        collection_name="shl_assessments",
    )
    
    # Initialize collection (connects to existing)
    await vector_store.create_collection(
        name="shl_assessments",
        dimension=384,  # all-MiniLM-L6-v2 dimension
    )
    
    # Check if knowledge base has data
    count = await vector_store.count()
    if count == 0:
        logger.error("=" * 70)
        logger.error("KNOWLEDGE BASE IS EMPTY")
        logger.error("=" * 70)
        logger.error("Please build the knowledge base first:")
        logger.error("  docker exec conversational-shl-assessment-recommender-api-1 \\")
        logger.error("    python3 scripts/build_knowledge_base.py")
        logger.error("=" * 70)
        return 1
    
    logger.info(f"Knowledge base loaded: {count} embeddings")
    
    pipeline = PipelineFactory.create_production_pipeline(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        top_k=20,
        max_assessments=5,
    )
    
    state_engine = ConversationStateEngine()
    intent_engine = IntentEngine()
    
    logger.info("Components initialized\n")
    
    # Test scenarios
    scenarios = [
        (
            "Senior Java Developer",
            "Hiring senior Java developer with leadership skills"
        ),
        (
            "Junior Data Scientist",
            "Need assessments for junior data scientist position"
        ),
        (
            "Cognitive Assessment",
            "Looking for cognitive reasoning tests"
        ),
        (
            "Sales Manager",
            "Recommend assessments for sales manager role"
        ),
        (
            "Entry Level Position",
            "What assessments for entry level software engineer?"
        ),
    ]
    
    results = []
    for scenario_name, user_message in scenarios:
        result = await test_pipeline_scenario(
            pipeline,
            state_engine,
            intent_engine,
            scenario_name,
            user_message,
        )
        results.append(result)
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total Scenarios: {len(scenarios)}")
    print(f"All Valid: {all(r.is_valid for r in results)}")
    print(f"Avg Latency: {sum(r.statistics.total_latency_ms for r in results) / len(results):.1f}ms")
    print(f"Avg Results: {sum(r.statistics.assessments_final for r in results) / len(results):.1f} assessments")
    print(f"{'='*70}")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)
