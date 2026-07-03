#!/usr/bin/env python3
"""
Test recommendation engine.

Demonstrates end-to-end recommendation generation.
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
from src.recommendation.engine.engine_factory import RecommendationEngineFactory
from src.shared.logging.logger import get_logger, setup_logger

# Setup logging
setup_logger("recommendation_test", level="INFO")
logger = get_logger(__name__)


async def test_recommendation_scenario(
    retrieval_pipeline,
    recommendation_engine,
    state_engine,
    intent_engine,
    scenario_name: str,
    user_message: str,
):
    """Test single recommendation scenario."""
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
    print(f"Requires Recommendation: {intent.requires_recommendation}")
    print()
    
    # Execute retrieval pipeline
    retrieval_result = await retrieval_pipeline.execute(state, intent)
    
    print(f"Retrieval Results:")
    print(f"  Retrieved: {retrieval_result.statistics.chunks_retrieved} chunks")
    print(f"  Assessments: {retrieval_result.statistics.assessments_final}")
    print()
    
    # Generate recommendations
    recommendation_result = recommendation_engine.generate_recommendations(
        retrieval_result, state, intent
    )
    
    # Display recommendation results
    print(f"Recommendation Results:")
    print(f"  Candidates Received: {recommendation_result.total_candidates}")
    print(f"  Recommendations: {len(recommendation_result.recommendations)}")
    print(f"  Confidence: {recommendation_result.confidence}")
    print(f"  Processing Time: {recommendation_result.statistics.processing_time_ms:.1f}ms")
    print()
    
    print(f"  Statistics:")
    print(f"    Filtered: {recommendation_result.statistics.candidates_filtered}")
    print(f"    Avg Ranking Score: {recommendation_result.statistics.avg_ranking_score:.3f}")
    print(f"    Avg Similarity: {recommendation_result.statistics.avg_similarity_score:.3f}")
    print()
    
    print(f"  Validation: {'✅ VALID' if recommendation_result.is_valid else '❌ INVALID'}")
    if recommendation_result.validation_warnings:
        print(f"  Warnings:")
        for warning in recommendation_result.validation_warnings:
            print(f"    - {warning}")
    print()
    
    # Display recommendations
    if recommendation_result.has_recommendations():
        print(f"  Top Recommendations:")
        for idx, rec in enumerate(recommendation_result.get_top_recommendations(3), 1):
            print(f"    {idx}. {rec.assessment_name}")
            print(f"       URL: {rec.official_url}")
            print(f"       Category: {rec.category} | Type: {rec.test_type}")
            print(f"       Ranking Score: {rec.ranking_score:.3f}")
            print(f"       Similarity: {rec.similarity_score:.3f}")
            print(f"       Reason: {rec.recommendation_reason}")
            if rec.matching_skills:
                print(f"       Matching Skills: {', '.join(rec.matching_skills[:3])}")
            print()
    else:
        print(f"  ⚠️  No recommendations generated")
    
    print(f"  Decision Rationale:")
    print(f"    {recommendation_result.decision_rationale}")
    print()
    
    return recommendation_result


async def main():
    """Run test scenarios."""
    logger.info("=" * 70)
    logger.info("RECOMMENDATION ENGINE TEST")
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
    
    # Initialize collection
    await vector_store.create_collection(
        name="shl_assessments",
        dimension=384,
    )
    
    # Check knowledge base
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
    
    # Create pipelines and engines
    retrieval_pipeline = PipelineFactory.create_production_pipeline(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        top_k=20,
        max_assessments=5,
    )
    
    recommendation_engine = RecommendationEngineFactory.create_production_engine(
        min_similarity=0.0,
        max_recommendations=10,
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
            "Sales Manager",
            "Recommend assessments for sales manager role"
        ),
        (
            "Data Scientist",
            "Looking for assessments for data scientist position"
        ),
    ]
    
    results = []
    for scenario_name, user_message in scenarios:
        result = await test_recommendation_scenario(
            retrieval_pipeline,
            recommendation_engine,
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
    print(f"Avg Recommendations: {sum(len(r.recommendations) for r in results) / len(results):.1f}")
    print(f"Avg Processing Time: {sum(r.statistics.processing_time_ms for r in results) / len(results):.1f}ms")
    total_recs = sum(len(r.recommendations) for r in results)
    print(f"Total Recommendations: {total_recs}")
    print(f"{'='*70}")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)
