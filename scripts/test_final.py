#!/usr/bin/env python3
"""
Final comprehensive test to verify all fixes.
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def main():
    print("=" * 70)
    print("FINAL COMPREHENSIVE TEST")
    print("=" * 70)
    
    # Test 1: Intent pattern matching
    print("\n✅ TEST 1: Intent Pattern Matching")
    from src.conversation.intent.detection.pattern_matcher import PatternMatcher
    pm = PatternMatcher()
    
    test_queries = [
        "I need cognitive ability assessments for problem solving",
        "I need assessment for problem solving",  # singular
        "Recommend tests for leadership",  # plural
        "Recommend test for leadership",  # singular
    ]
    
    for query in test_queries:
        is_rec, patterns = pm.match_recommendation(query)
        status = "✓" if is_rec else "✗"
        print(f"   {status} '{query}' -> {is_rec}")
    
    # Test 2: Full orchestrator test
    print("\n✅ TEST 2: Full Orchestrator Execution")
    from src.api.dependencies.orchestrator import get_orchestrator
    
    orch = get_orchestrator()
    result = await orch.execute('I need cognitive ability assessments for problem solving', [], '')
    
    print(f"   Success: {result.success}")
    print(f"   Intent: {result.intent_result.primary_intent if result.intent_result else 'None'}")
    print(f"   Recommendations: {len(result.recommendation_result.recommendations) if result.recommendation_result else 0}")
    
    if result.recommendation_result and result.recommendation_result.recommendations:
        print(f"   ✓ {len(result.recommendation_result.recommendations)} recommendations generated")
        for i, rec in enumerate(result.recommendation_result.recommendations[:3], 1):
            print(f"     {i}. {rec.assessment_name} ({rec.duration_minutes} min)")
    else:
        print(f"   ✗ No recommendations!")
        return 1
    
    # Test 3: API endpoint
    print("\n✅ TEST 3: API Endpoint")
    import httpx
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                'http://localhost:8000/chat',
                json={'messages': [{'role': 'user', 'content': 'I need cognitive ability assessments for problem solving'}]}
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Recommendations: {len(data.get('recommendations', []))}")
                
                if data.get('recommendations'):
                    for i, rec in enumerate(data['recommendations'][:3], 1):
                        print(f"     {i}. {rec['title']}")
                        print(f"        Duration: {rec.get('duration', 'N/A')}")
                        print(f"        URL: {rec['url'][:60]}...")
                else:
                    print("   ✗ No recommendations returned!")
                    return 1
            else:
                print(f"   ✗ HTTP {response.status_code}")
                return 1
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return 1
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
