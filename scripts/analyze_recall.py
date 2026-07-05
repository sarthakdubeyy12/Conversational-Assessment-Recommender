#!/usr/bin/env python3
"""
Analyze why Recall@10 is low.

Examines what assessments are expected vs what's being retrieved.
"""

import asyncio
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.dependencies.orchestrator import get_orchestrator

async def analyze_recall():
    """Analyze recall issues."""
    print("=" * 70)
    print("RECALL ANALYSIS - Why are we missing expected assessments?")
    print("=" * 70)
    
    # Load sample traces
    traces_file = Path("evaluation/traces/sample_traces.json")
    with open(traces_file) as f:
        traces = json.load(f)
    
    orch = get_orchestrator()
    
    for trace in traces[:2]:  # Analyze first 2 traces
        trace_id = trace.get('trace_id')
        description = trace.get('description')
        expected_urls = trace.get('expected_assessments', [])
        
        print(f"\n{'='*70}")
        print(f"TRACE: {trace_id}")
        print(f"Description: {description}")
        print(f"Expected assessments: {len(expected_urls)}")
        
        # Get the initial user message
        turns = trace.get('turns', [])
        user_messages = [t['content'] for t in turns if t['role'] == 'user']
        
        if not user_messages:
            continue
        
        first_query = user_messages[0]
        print(f"Query: '{first_query}'")
        
        # Execute and get recommendations
        result = await orch.execute(first_query, [], '')
        
        if result.recommendation_result:
            recs = result.recommendation_result.recommendations
            rec_urls = [r.official_url for r in recs]
            
            print(f"\nRetrieved: {len(rec_urls)} recommendations")
            
            # Calculate recall
            matches = sum(1 for url in expected_urls if url in rec_urls)
            recall = matches / len(expected_urls) if expected_urls else 0
            
            print(f"Matches: {matches}/{len(expected_urls)}")
            print(f"Recall@10: {recall:.2%}")
            
            # Show what we got
            print(f"\n📊 Retrieved assessments:")
            for i, rec in enumerate(recs[:10], 1):
                matched = "✓" if rec.official_url in expected_urls else " "
                print(f"   {matched} {i}. {rec.assessment_name}")
                print(f"      Score: {rec.ranking_score:.3f}, Similarity: {rec.similarity_score:.3f}")
            
            # Show what we missed
            missed_urls = [url for url in expected_urls if url not in rec_urls]
            if missed_urls:
                print(f"\n❌ Missed assessments ({len(missed_urls)}):")
                for url in missed_urls:
                    # Try to find the assessment name from URL
                    name = url.split('/')[-2].replace('-', ' ').title()
                    print(f"   • {name}")
                    print(f"     URL: {url}")
            
            # Analyze retrieval results
            if result.retrieval_result:
                all_docs = result.retrieval_result.ranked_documents
                print(f"\n🔍 Retrieval analysis:")
                print(f"   Total chunks retrieved: {len(all_docs)}")
                print(f"   Unique assessments: {result.retrieval_result.statistics.assessments_final}")
                
                # Check if missed assessments were in retrieval at all
                retrieved_urls = set()
                for doc in all_docs:
                    retrieved_urls.add(doc.result.url)
                
                for missed_url in missed_urls:
                    if missed_url in retrieved_urls:
                        print(f"   ⚠️  '{missed_url.split('/')[-2]}' WAS retrieved but not recommended")
                    else:
                        print(f"   ❌ '{missed_url.split('/')[-2]}' was NOT retrieved at all")
        
        else:
            print("\n❌ No recommendations generated!")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(analyze_recall())
