#!/usr/bin/env python3
"""Quick test of the complete flow to identify issues."""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def main():
    print("Testing complete flow...\n")
    
    # Test 1: Direct API call
    print("1️⃣  Testing /chat endpoint...")
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/chat",
                json={"messages": [{"role": "user", "content": "I need cognitive ability assessments"}]},
                timeout=30.0
            )
            data = response.json()
            print(f"   Status: {response.status_code}")
            print(f"   Reply: {data['reply'][:100]}...")
            print(f"   Recommendations: {len(data.get('recommendations', []))}")
            
            if data.get('recommendations'):
                print(f"   First rec: {data['recommendations'][0]['title']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ Test complete")

if __name__ == "__main__":
    asyncio.run(main())
