#!/usr/bin/env python3
"""
Diagnose the retrieval pipeline to find where documents are lost.
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.knowledge_base.embeddings.provider import SentenceTransformerProvider
from src.knowledge_base.vector_store.chroma_client import ChromaVectorStore
from src.knowledge_base.semantic_search import SemanticSearchService
from src.retrieval.domain.entities import SearchQuery
from src.retrieval.pipeline.query.query_builder import ProductionQueryBuilder
from src.retrieval.pipeline.filters.metadata_filter_builder import MetadataFilterBuilder
from src.retrieval.pipeline.ranking.hybrid_ranker import HybridRanker
from src.retrieval.pipeline.compression.duplicate_remover import DuplicateRemover
from src.retrieval.pipeline.compression.context_compressor import ContextCompressor
from src.retrieval.pipeline.validation.retrieval_validator import RetrievalValidator
from src.retrieval.pipeline.retrieval_pipeline import RetrievalPipeline
from src.conversation.state.state_engine import ConversationStateEngine
from src.conversation.intent.intent_engine import IntentEngine
from src.shared.config.settings import get_settings

settings = get_settings()


async def main():
    print("=" * 70)
    print("RETRIEVAL PIPELINE DIAGNOSTIC")
    print("=" * 70)
    print()
    
    # Setup components
    print("1️⃣  Setting up components...")
    provider = SentenceTransformerProvider(settings.embedding_model)
    store = ChromaVectorStore(
        settings.chroma_persist_directory,
        settings.chroma_collection_name
    )
    await store.create_collection(
        settings.chroma_collection_name,
        provider.get_dimension()
    )
    
    semantic_search = SemanticSearchService(provider, store)
    query_builder = ProductionQueryBuilder()
    filter_builder = MetadataFilterBuilder()
    ranker = HybridRanker()
    duplicate_remover = DuplicateRemover()
    compressor = ContextCompressor()
    validator = RetrievalValidator()
    
    pipeline = RetrievalPipeline(
        semantic_search=semantic_search,
        query_builder=query_builder,
        filter_builder=filter_builder,
        ranker=ranker,
        duplicate_remover=duplicate_remover,
        compressor=compressor,
        validator=validator,
        top_k=20,
    )
    print("   ✓ Components ready\n")
    
    # Create conversation state
    print("2️⃣  Creating conversation state...")
    state_engine = ConversationStateEngine()
    intent_engine = IntentEngine()
    
    user_message = "I need cognitive ability assessments"
    messages = [{"role": "user", "content": user_message}]
    
    state = state_engine.reconstruct_state(messages)
    intent = intent_engine.detect_intent(user_message, state)
    
    print(f"   Message: '{user_message}'")
    print(f"   Intent: {intent.primary_intent}")
    print(f"   Requires retrieval: {intent.requires_retrieval}")
    print()
    
    # Test semantic search directly
    print("3️⃣  Testing semantic search directly...")
    query = SearchQuery(
        text=user_message,
        top_k=20,
        similarity_threshold=0.0,
        filters=None
    )
    raw_results = await semantic_search.search(query)
    print(f"   ✓ Semantic search returned: {len(raw_results)} results")
    if raw_results:
        print(f"     Top result: {raw_results[0].assessment_name}")
        print(f"     Similarity: {raw_results[0].similarity_score:.3f}")
    print()
    
    # Test full pipeline
    print("4️⃣  Testing full retrieval pipeline...")
    result = await pipeline.execute(state, intent)
    print(f"   ✓ Pipeline complete")
    print(f"   Chunks retrieved: {result.statistics.chunks_retrieved}")
    print(f"   Chunks filtered: {result.statistics.chunks_filtered}")
    print(f"   Chunks deduplicated: {result.statistics.chunks_deduplicated}")
    print(f"   Final documents: {len(result.ranked_documents)}")
    print()
    
    if result.ranked_documents:
        print("5️⃣  Top 3 ranked documents:")
        for i, doc in enumerate(result.ranked_documents[:3], 1):
            print(f"   {i}. {doc.result.assessment_name}")
            print(f"      Similarity: {doc.result.similarity_score:.3f}")
            print(f"      Ranking: {doc.ranking_score:.3f}")
            print(f"      URL: {doc.result.url}")
        print()
        print("✅ SUCCESS: Pipeline is working correctly!")
    else:
        print("❌ PROBLEM: Pipeline returned zero documents!")
        print()
        print("Debug info:")
        print(f"   Queries generated: {result.generated_queries}")
        print(f"   Filters applied: {result.applied_filters}")
        print(f"   Validation warnings: {result.validation_warnings}")


if __name__ == "__main__":
    asyncio.run(main())
