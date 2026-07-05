#!/usr/bin/env python3
"""
Comprehensive diagnostic to find where documents are lost.
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def main():
    print("=" * 70)
    print("FULL PIPELINE DIAGNOSTIC")
    print("=" * 70)
    
    # Setup
    print("\n1️⃣  Setting up components...")
    from src.shared.config.settings import get_settings
    from src.knowledge_base.embeddings.provider import SentenceTransformerProvider
    from src.knowledge_base.vector_store.chroma_client import ChromaVectorStore
    from src.knowledge_base.semantic_search import SemanticSearchService
    from src.retrieval.domain.entities import SearchQuery
    from src.recommendation.selection.candidate_selector import CandidateSelector
    
    settings = get_settings()
    provider = SentenceTransformerProvider(settings.embedding_model)
    store = ChromaVectorStore(settings.chroma_persist_directory, settings.chroma_collection_name)
    await store.create_collection(settings.chroma_collection_name, provider.get_dimension())
    search = SemanticSearchService(provider, store)
    
    print("✓ Components ready")
    
    # Test semantic search
    print("\n2️⃣  Testing semantic search...")
    query = SearchQuery(
        text="cognitive ability assessment problem solving skills reasoning",
        top_k=20,
        similarity_threshold=0.0,
        filters=None
    )
    results = await search.search(query)
    print(f"✓ Semantic search returned {len(results)} results")
    
    if not results:
        print("❌ PROBLEM: Semantic search returned 0 results!")
        return
    
    # Show top results
    print("\n   Top results from semantic search:")
    for i, r in enumerate(results[:5], 1):
        print(f"     {i}. {r.assessment_name}")
        print(f"        Similarity: {r.similarity_score:.3f}")
        print(f"        URL: {r.url}")
        print(f"        Category: {r.category}")
        print(f"        Test Type: {r.test_type}")
    
    # Test candidate selector with different configurations
    print("\n3️⃣  Testing CandidateSelector filtering...")
    
    # Wrap results in RankedDocument format
    from src.retrieval.pipeline.pipeline_result import RankedDocument
    ranked_docs = []
    for r in results:
        ranked_doc = RankedDocument(
            result=r,
            ranking_score=r.similarity_score,
            ranking_factors={"semantic": r.similarity_score}
        )
        ranked_docs.append(ranked_doc)
    
    # Test 1: Default selector (min_similarity=0.0, require_url=True)
    print("\n   Test A: Default selector (min_similarity=0.0, require_url=True)")
    selector_default = CandidateSelector(
        min_similarity=0.0,
        require_url=True,
        require_category=False
    )
    candidates_default = selector_default.select_candidates(ranked_docs)
    print(f"   Result: {len(candidates_default)} candidates passed")
    
    if len(candidates_default) == 0:
        print("   ❌ PROBLEM: All candidates filtered out!")
        print("   Checking why...")
        
        for i, doc in enumerate(ranked_docs[:3], 1):
            print(f"\n   Document {i}:")
            print(f"     Name: {doc.result.assessment_name}")
            print(f"     Similarity: {doc.result.similarity_score:.3f} (threshold: 0.0)")
            print(f"     URL: {doc.result.url}")
            
            # Check URL validation
            url = doc.result.url
            has_url = bool(url)
            is_https = url.startswith("https://") if url else False
            has_shl = "shl.com" in url if url else False
            url_valid = is_https and has_shl
            
            print(f"     URL checks:")
            print(f"       - Has URL: {has_url}")
            print(f"       - Is HTTPS: {is_https}")
            print(f"       - Contains shl.com: {has_shl}")
            print(f"       - Valid: {url_valid}")
            print(f"     Has name: {bool(doc.result.assessment_name)}")
    
    # Test 2: No URL requirement
    print("\n   Test B: No URL requirement (min_similarity=0.0, require_url=False)")
    selector_no_url = CandidateSelector(
        min_similarity=0.0,
        require_url=False,
        require_category=False
    )
    candidates_no_url = selector_no_url.select_candidates(ranked_docs)
    print(f"   Result: {len(candidates_no_url)} candidates passed")
    
    # Test through full API
    print("\n4️⃣  Testing through full API...")
    import httpx
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/chat",
                json={"messages": [{"role": "user", "content": "I need cognitive ability assessments for problem solving"}]},
                timeout=30.0
            )
            data = response.json()
            print(f"   Status: {response.status_code}")
            print(f"   Recommendations: {len(data.get('recommendations', []))}")
            
            if data.get('recommendations'):
                print("\n   Recommendations returned:")
                for i, rec in enumerate(data['recommendations'][:3], 1):
                    print(f"     {i}. {rec['title']}")
            else:
                print("   ❌ No recommendations returned!")
                print(f"   Reply: {data.get('reply', 'N/A')[:200]}...")
                print(f"\n   Full response data:")
                print(f"     reply: {data.get('reply', 'N/A')}")
                print(f"     end_of_conversation: {data.get('end_of_conversation', 'N/A')}")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Test recommendation engine directly
    print("\n5️⃣  Testing RecommendationEngine directly...")
    from src.recommendation.engine.engine_factory import RecommendationEngineFactory
    from src.conversation.state.domain.conversation_state import ConversationState, HiringContext
    from src.conversation.intent.domain.intent_result import IntentResult
    from src.conversation.intent.domain.intent_types import IntentType
    from src.retrieval.pipeline.pipeline_result import PipelineResult, PipelineStatistics
    
    # Create mock pipeline result
    pipeline_result = PipelineResult(
        ranked_documents=ranked_docs,
        generated_queries=["cognitive ability assessment"],
        applied_filters={},
        retrieval_strategy="semantic_search",
        ranking_strategy="hybrid",
        decision_rationale="test",
        compressed_context="test",
        context_token_count=100,
        statistics=PipelineStatistics(
            total_latency_ms=100,
            query_build_ms=10,
            retrieval_ms=50,
            filtering_ms=10,
            ranking_ms=10,
            deduplication_ms=10,
            compression_ms=10,
            chunks_retrieved=18,
            chunks_filtered=0,
            chunks_deduplicated=0,
            chunks_final=18,
            assessments_final=6,
            avg_similarity_score=0.6,
            avg_ranking_score=0.6,
            compression_ratio=1.0,
            metadata_coverage=1.0
        ),
        is_valid=True
    )
    
    # Create mock state and intent
    state = ConversationState(
        hiring_context=HiringContext(
            job_title="Software Engineer",
            required_skills=["problem-solving", "analytical thinking"],
            technical_skills=[],
            soft_skills=[],
            job_level="Mid Level",
            industry="Technology"
        )
    )
    
    intent = IntentResult(
        primary_intent=IntentType.RECOMMENDATION,
        confidence=0.9,
        requires_retrieval=True,
        requires_recommendation=True,
        requires_comparison=False
    )
    
    # Test engine
    engine = RecommendationEngineFactory.create_production_engine()
    rec_result = engine.generate_recommendations(pipeline_result, state, intent)
    
    print(f"   Recommendations generated: {len(rec_result.recommendations)}")
    print(f"   Confidence: {rec_result.confidence}")
    print(f"   Valid: {rec_result.is_valid}")
    
    if rec_result.recommendations:
        print("\n   Top recommendations:")
        for i, rec in enumerate(rec_result.recommendations[:3], 1):
            print(f"     {i}. {rec.assessment_name}")
            print(f"        URL: {rec.official_url}")
            print(f"        Score: {rec.ranking_score:.3f}")
    else:
        print("   ❌ No recommendations generated by engine!")
        print(f"   Validation warnings: {rec_result.validation_warnings}")
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())

