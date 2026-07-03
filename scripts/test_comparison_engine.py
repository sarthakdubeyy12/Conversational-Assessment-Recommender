"""
Test script for comparison engine.

Tests the complete comparison pipeline.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.comparison.engine.engine_factory import ComparisonEngineFactory
from src.retrieval.pipeline.pipeline_factory import PipelineFactory
from src.knowledge_base.embeddings.provider import SentenceTransformerProvider
from src.knowledge_base.vector_store.chroma_client import ChromaVectorStore
from src.conversation.state.domain.conversation_state import ConversationState, HiringContext
from src.conversation.intent.domain.intent_result import IntentResult
from src.conversation.intent.domain.intent_types import IntentType, ConfidenceLevel
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


async def test_comparison(
    engine,
    pipeline,
    user_message: str,
    description: str,
) -> bool:
    """Test single comparison scenario."""
    print("\n" + "=" * 60)
    print(f"Scenario: {description}")
    print("=" * 60)
    print(f"Query: '{user_message}'")
    print()
    
    try:
        # Create conversation state
        state = ConversationState(
            hiring_context=HiringContext(
                role_title="Software Engineer",
                required_skills=["python", "problem solving"],
                technical_skills=["coding", "algorithms"],
            ),
        )
        
        # Create intent
        intent = IntentResult(
            primary_intent=IntentType.COMPARISON,
            confidence_level=ConfidenceLevel.HIGH,
            requires_retrieval=True,
            requires_comparison=True,
            requires_recommendation=False,
            decision_reason="Comparison request detected",
        )
        
        # Run retrieval pipeline
        retrieval_result = await pipeline.execute(state, intent)
        
        print(f"Retrieved {len(retrieval_result.ranked_documents)} assessments")
        
        if len(retrieval_result.ranked_documents) < 2:
            print("❌ Need at least 2 assessments for comparison")
            return False
        
        # Run comparison
        comparison_result = engine.compare_assessments(
            user_message=user_message,
            retrieval_result=retrieval_result,
            state=state,
            intent=intent,
        )
        
        if not comparison_result:
            print("❌ Comparison failed - could not resolve assessments")
            return False
        
        # Display results
        print(f"\n📊 Comparison Result:")
        print(f"Assessment A: {comparison_result.assessment_a.assessment_name}")
        print(f"  URL: {comparison_result.assessment_a.official_url}")
        print(f"  Category: {comparison_result.assessment_a.category}")
        print(f"  Type: {comparison_result.assessment_a.test_type}")
        
        print(f"\nAssessment B: {comparison_result.assessment_b.assessment_name}")
        print(f"  URL: {comparison_result.assessment_b.official_url}")
        print(f"  Category: {comparison_result.assessment_b.category}")
        print(f"  Type: {comparison_result.assessment_b.test_type}")
        
        print(f"\n✅ Similarities ({len(comparison_result.similarities)}):")
        for sim in comparison_result.similarities[:5]:
            print(f"  - {sim}")
        
        print(f"\n🔄 Differences ({len(comparison_result.differences)}):")
        for diff in comparison_result.differences[:5]:
            print(f"  - {diff}")
        
        if comparison_result.unique_strengths_a:
            print(f"\n💪 Unique Strengths of {comparison_result.assessment_a.assessment_name}:")
            for strength in comparison_result.unique_strengths_a:
                print(f"  - {strength}")
        
        if comparison_result.unique_strengths_b:
            print(f"\n💪 Unique Strengths of {comparison_result.assessment_b.assessment_name}:")
            for strength in comparison_result.unique_strengths_b:
                print(f"  - {strength}")
        
        print(f"\n📈 Statistics:")
        print(f"  Fields Compared: {comparison_result.statistics.fields_compared}")
        print(f"  Identical: {comparison_result.statistics.fields_identical}")
        print(f"  Different: {comparison_result.statistics.fields_different}")
        print(f"  Missing: {comparison_result.statistics.fields_missing}")
        print(f"  Processing Time: {comparison_result.statistics.processing_time_ms:.1f}ms")
        print(f"  Confidence: {comparison_result.confidence.value} ({comparison_result.confidence_score:.2f})")
        
        if comparison_result.missing_information_note:
            print(f"\n⚠️  {comparison_result.missing_information_note}")
        
        print(f"\n✅ PASSED")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main() -> int:
    """Run all comparison tests."""
    print("=" * 60)
    print("COMPARISON ENGINE TEST")
    print("=" * 60)
    
    try:
        # Initialize components
        print("\n🔧 Initializing components...")
        
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
            dimension=384,  # all-MiniLM-L6-v2 dimension
        )
        
        # Check if knowledge base has data
        count = await vector_store.count()
        if count == 0:
            print("❌ Knowledge base is empty. Run 'python scripts/build_knowledge_base.py' first")
            return 1
        
        print(f"✅ Knowledge base loaded: {count} documents")
        
        # Create engines
        comparison_engine = ComparisonEngineFactory.create_production_engine()
        retrieval_pipeline = PipelineFactory.create_production_pipeline(
            embedding_provider=embedding_provider,
            vector_store=vector_store,
        )
        
        print("✅ Components initialized")
        
        # Test scenarios
        scenarios = [
            {
                "message": "Compare Verify Interactive and Verify G+",
                "description": "Explicit comparison with assessment names",
            },
            {
                "message": "What's the difference between cognitive and personality assessments?",
                "description": "Category-level comparison",
            },
            {
                "message": "Compare the top 2 assessments for problem solving",
                "description": "Implicit comparison using top retrieved",
            },
        ]
        
        results = []
        for scenario in scenarios:
            success = await test_comparison(
                comparison_engine,
                retrieval_pipeline,
                scenario["message"],
                scenario["description"],
            )
            results.append(success)
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        passed = sum(results)
        total = len(results)
        print(f"Passed: {passed}/{total}")
        
        if passed == total:
            print("✅ All tests passed!")
            return 0
        else:
            print(f"❌ {total - passed} test(s) failed")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
