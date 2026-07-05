#!/usr/bin/env python3
"""
Verify the actual size of SHL's Individual Test Solutions catalog.

This script checks:
1. How many Individual Test Solutions exist on shl.com
2. How many we have in our catalog.json
3. Whether we're using complete or mock data
"""

import asyncio
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

async def check_shl_catalog_size():
    """Check actual SHL catalog size."""
    print("=" * 80)
    print("SHL CATALOG SIZE VERIFICATION")
    print("=" * 80)
    print()
    
    # 1. Check current catalog
    print("1️⃣  CURRENT CATALOG IN SYSTEM")
    print("-" * 80)
    
    catalog_path = Path("data/processed/catalog.json")
    if not catalog_path.exists():
        print("❌ Catalog file not found!")
        return
    
    with open(catalog_path) as f:
        catalog = json.load(f)
    
    print(f"📊 Current catalog size: {len(catalog)} assessments")
    print()
    
    if len(catalog) <= 10:
        print("⚠️  WARNING: This appears to be MOCK DATA")
        print("   Real SHL catalog should have 50+ Individual Test Solutions")
    else:
        print("✅ Catalog size suggests real data")
    
    print()
    print("Current assessments:")
    for i, item in enumerate(catalog, 1):
        print(f"  {i}. {item['name']}")
    
    print()
    
    # 2. Try to discover actual SHL catalog size
    print("2️⃣  DISCOVERING REAL SHL CATALOG SIZE")
    print("-" * 80)
    print()
    
    try:
        from src.catalog.infrastructure.web_scraper import WebScraper
        from src.catalog.infrastructure.link_discoverer import LinkDiscoverer
        from src.shared.config.settings import get_settings
        
        settings = get_settings()
        catalog_url = settings.catalog_url
        
        print(f"📍 Crawling: {catalog_url}")
        print("   (This may take 1-2 minutes...)")
        print()
        
        # Initialize scraper and discoverer
        scraper = WebScraper(
            max_retries=3,
            timeout=30,
            rate_limit_delay=1.0,
            save_raw_html=False
        )
        
        discoverer = LinkDiscoverer(scraper)
        
        # Discover assessment URLs
        print("🔍 Discovering Individual Test Solution URLs...")
        urls = await discoverer.discover_assessment_links(catalog_url)
        
        scraper.close()
        
        print()
        print(f"✅ Found {len(urls)} Individual Test Solution URLs on SHL website")
        print()
        
        if len(urls) > 0:
            print("Sample discovered URLs:")
            for i, url in enumerate(list(urls)[:10], 1):
                # Extract assessment name from URL
                name = url.split('/')[-2].replace('-', ' ').title()
                print(f"  {i}. {name}")
                print(f"     {url}")
            
            if len(urls) > 10:
                print(f"  ... and {len(urls) - 10} more")
        
        print()
        
        # 3. Compare
        print("3️⃣  COMPARISON")
        print("-" * 80)
        print()
        
        current_size = len(catalog)
        real_size = len(urls)
        
        print(f"Real SHL Catalog:     {real_size} Individual Test Solutions")
        print(f"Current System:       {current_size} assessments")
        print(f"Coverage:             {(current_size/real_size*100) if real_size > 0 else 0:.1f}%")
        print()
        
        if current_size < real_size * 0.5:
            print("❌ INCOMPLETE: System is missing more than 50% of SHL catalog")
            print(f"   Missing: {real_size - current_size} assessments")
        elif current_size < real_size:
            print("⚠️  PARTIAL: System is missing some assessments")
            print(f"   Missing: {real_size - current_size} assessments")
        else:
            print("✅ COMPLETE: System has the full SHL catalog")
        
        print()
        
        # 4. Final verdict
        print("=" * 80)
        print("FINAL VERDICT")
        print("=" * 80)
        print()
        
        if current_size <= 10 and real_size > 20:
            print("❌ NOT VERIFIED")
            print()
            print("Evidence:")
            print(f"  • Current catalog: {current_size} assessments (MOCK DATA)")
            print(f"  • Real SHL catalog: {real_size} Individual Test Solutions")
            print(f"  • System is using {(current_size/real_size*100) if real_size > 0 else 0:.1f}% of real catalog")
            print()
            print("Action Required:")
            print("  Run: python3 scripts/build_catalog.py")
            print("  Then: python3 scripts/build_knowledge_base.py")
        elif current_size >= real_size * 0.9:
            print("✅ VERIFIED")
            print()
            print("Evidence:")
            print(f"  • Current catalog: {current_size} assessments")
            print(f"  • Real SHL catalog: {real_size} Individual Test Solutions")
            print(f"  • Coverage: {(current_size/real_size*100):.1f}%")
            print()
            print("System is using the complete SHL Product Catalog ✅")
        else:
            print("⚠️  PARTIALLY VERIFIED")
            print()
            print("Evidence:")
            print(f"  • Current catalog: {current_size} assessments")
            print(f"  • Real SHL catalog: {real_size} Individual Test Solutions")
            print(f"  • Coverage: {(current_size/real_size*100):.1f}%")
            print()
            print("Action Required:")
            print("  Re-run scraper to get missing assessments")
        
    except Exception as e:
        print(f"❌ Error discovering real catalog size: {e}")
        print()
        print("Unable to verify against live SHL website.")
        print("Manual verification required.")

if __name__ == "__main__":
    asyncio.run(check_shl_catalog_size())
