#!/usr/bin/env python3
"""Simple end-to-end test."""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def main():
    print("Testing complete pipeline...\n")
    
    # Test direct semantic search
    print("1️⃣  Testing semantic search...")
    from src.knowledge_base.embeddings.provider import SentenceTransformerProvider
    from src.knowledge_base.vector_store.chroma_client import ChromaVectorStore
    from src.knowledge_base.semantic_search import SemanticSearchService
    from src.retrieval.domain.entities import SearchQuery
    from src.shared.config.settings import get_settings
    
    settings = get_settings()
    provider = SentenceTransformerProvider(settings.embedding_model)
    store = ChromaVectorStore(settings.chroma_persist_directory, settings.chroma_collection_name)
    await store.create_collection(settings.chroma_collection_name, provider.get_dimension())
    
    search = SemanticSearchService(provider, store)
    query = SearchQuery(
        text="cognitive ability assessment problem solving skills reasoning",
        top_k=20,
        similarity_threshold=0.0,
        filters=None
    )
    results = await search.search(query)
    
    print(f"   ✓ Search returned {len(results)} results")
    if results:
        for i, r in enumerate(results[:3], 1):
            print(f"     {i}. {r.assessment_name}: {r.similarity_score:.3f}")
    print()
    
    # Test through API
    print("2️⃣  Testing through /chat API...")
    import httpx
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/chat",
                json={"messages": [{"role": "user", "content": "I need cognitive ability assessments"}]},
                timeout=30.0
            )
            data = response.json()
            print(f"   Status: {response.status_code}")
            print(f"   Reply: {data['reply'][:80]}...")
            print(f"   Recommendations: {len(data.get('recommendations', []))}")
            if data.get('recommendations'):
                print(f"   First: {data['recommendations'][0]['title']}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n✅ Test complete")

if __name__ == "__main__":
    asyncio.run(main())
