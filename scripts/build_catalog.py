#!/usr/bin/env python3
"""
Catalog ingestion CLI script - Sitemap-based scraper.

Discovers assessment URLs from SHL sitemap and scrapes them.
"""

import asyncio
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.catalog.infrastructure.web_scraper import WebScraper
from src.catalog.infrastructure.html_parser import AssessmentHTMLParser
from src.catalog.infrastructure.validators import AssessmentValidator
from src.catalog.infrastructure.normalizer import DataNormalizer
from src.catalog.infrastructure.json_repository import JSONCatalogRepository
from src.shared.config.settings import get_settings
from src.shared.logging.logger import get_logger, setup_logger

setup_logger("catalog_build", level="INFO")
logger = get_logger(__name__)

settings = get_settings()


async def discover_urls_from_sitemap(scraper: WebScraper) -> set:
    """Discover all assessment URLs from SHL sitemap."""
    logger.info("=" * 70)
    logger.info("STEP 1: DISCOVERING ASSESSMENT URLS FROM SITEMAP")
    logger.info("=" * 70)
    
    sitemap_url = "https://www.shl.com/sitemap.xml"
    logger.info(f"Fetching sitemap index: {sitemap_url}")
    
    page = await scraper.fetch_page(sitemap_url)
    if not page or page.status_code != 200:
        logger.error("Failed to fetch sitemap index")
        return set()
    
    # Extract sub-sitemap URLs
    sitemap_urls = re.findall(r'<loc>(https://www\.shl\.com[^<]+)</loc>', page.html_content)
    logger.info(f"Found {len(sitemap_urls)} sub-sitemaps")
    
    all_urls = set()
    
    # Fetch each sub-sitemap
    for i, sitemap_url in enumerate(sitemap_urls, 1):
        logger.info(f"[{i}/{len(sitemap_urls)}] Fetching sub-sitemap...")
        
        try:
            sub_page = await scraper.fetch_page(sitemap_url)
            if not sub_page or sub_page.status_code != 200:
                continue
            
            # Extract all URLs from this sitemap
            urls = re.findall(r'<loc>(https://www\.shl\.com[^<]+)</loc>', sub_page.html_content)
            
            # Filter for assessment URLs
            for url in urls:
                if '/products/assessments/' in url or '/solutions/products/assessments/' in url:
                    all_urls.add(url.rstrip('/'))
            
        except Exception as e:
            logger.warning(f"Error fetching sub-sitemap: {e}")
            continue
    
    logger.info(f"Found {len(all_urls)} total assessment-related URLs")
    
    # Filter to individual assessments only
    individual_assessments = set()
    
    # Exclude patterns (category pages, non-assessments)
    exclude_patterns = [
        '/job-focused-assessments',
        '/job-solutions/',
        '/assessment-and-development-centers',
        '/blog', '/resources', '/webinars', '/whitepapers',
        '/services/', '/training/', '/careers/',
        '/bundles/',
    ]
    
    # Category page patterns (exclude these)
    category_endings = [
        '/assessments',
        '/behavioral-assessments',
        '/cognitive-assessments',
        '/personality-assessment',
        '/skills-and-simulations',
        '/business-skills',
        '/technical-skills',
        '/call-center-simulations',
        '/coding-simulations',
        '/language-evaluation',
    ]
    
    for url in all_urls:
        # Must not match exclude patterns
        if any(pattern in url for pattern in exclude_patterns):
            continue
        
        # Must not be a category page
        clean_url = url.rstrip('/')
        if any(clean_url.endswith(ending) for ending in category_endings):
            continue
        
        # Individual assessments typically have 4+ path segments
        path = clean_url.replace('https://www.shl.com', '')
        segments = [s for s in path.split('/') if s]
        
        if len(segments) >= 4:
            individual_assessments.add(url)
    
    logger.info(f"Filtered to {len(individual_assessments)} individual assessment URLs")
    logger.info("")
    
    return individual_assessments


async def fetch_and_parse_assessments(scraper: WebScraper, parser: AssessmentHTMLParser, 
                                      validator: AssessmentValidator, normalizer: DataNormalizer,
                                      urls: set) -> list:
    """Fetch and parse assessment pages."""
    logger.info("=" * 70)
    logger.info("STEP 2: FETCHING AND PARSING ASSESSMENT PAGES")
    logger.info("=" * 70)
    
    assessments = []
    failed_count = 0
    
    for i, url in enumerate(sorted(urls), 1):
        logger.info(f"[{i}/{len(urls)}] {url}")
        
        try:
            # Fetch page
            page = await scraper.fetch_page(url)
            
            if not page or page.status_code != 200:
                logger.warning(f"  ❌ Failed to fetch (status: {page.status_code if page else 'None'})")
                failed_count += 1
                continue
            
            # Parse assessment
            assessment = parser.parse(page)
            
            if not assessment:
                logger.warning(f"  ❌ Failed to parse")
                failed_count += 1
                continue
            
            # Validate
            if not validator.validate(assessment):
                logger.warning(f"  ❌ Validation failed")
                failed_count += 1
                continue
            
            # Normalize
            assessment = normalizer.normalize(assessment)
            assessments.append(assessment)
            
            logger.info(f"  ✅ {assessment.name}")
            
        except Exception as e:
            logger.error(f"  ❌ Error: {str(e)[:60]}")
            failed_count += 1
            continue
    
    logger.info("")
    logger.info(f"Successfully processed: {len(assessments)} assessments")
    logger.info(f"Failed: {failed_count} URLs")
    logger.info("")
    
    return assessments


async def main():
    """Run sitemap-based catalog scraping pipeline."""
    logger.info("=" * 70)
    logger.info("SHL CATALOG SCRAPER - SITEMAP-BASED DISCOVERY")
    logger.info("=" * 70)
    logger.info("")
    
    # Initialize components
    scraper = WebScraper(
        max_retries=3,
        timeout=20,
        rate_limit_delay=1.5,
        save_raw_html=True,
        raw_html_dir="./data/raw"
    )
    
    parser = AssessmentHTMLParser()
    validator = AssessmentValidator()
    normalizer = DataNormalizer()
    repository = JSONCatalogRepository(settings.catalog_path)
    
    try:
        # Step 1: Discover URLs from sitemap
        urls = await discover_urls_from_sitemap(scraper)
        
        if not urls:
            logger.error("No assessment URLs discovered")
            return 1
        
        # Step 2: Fetch and parse assessments
        assessments = await fetch_and_parse_assessments(scraper, parser, validator, normalizer, urls)
        
        if not assessments:
            logger.error("No assessments were successfully parsed")
            return 1
        
        # Step 3: Save to repository
        logger.info("=" * 70)
        logger.info("STEP 3: SAVING TO CATALOG")
        logger.info("=" * 70)
        
        await repository.save(assessments)
        
        logger.info(f"✅ Saved {len(assessments)} assessments to {settings.catalog_path}")
        logger.info("")
        
        # Print summary
        logger.info("=" * 70)
        logger.info("CATALOG SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total Assessments: {len(assessments)}")
        
        # Group by category
        by_category = {}
        for assessment in assessments:
            cat = assessment.category or "Unknown"
            by_category[cat] = by_category.get(cat, 0) + 1
        
        logger.info("\nBy Category:")
        for category, count in sorted(by_category.items()):
            logger.info(f"  {category}: {count}")
        
        logger.info("\nAssessments:")
        for i, assessment in enumerate(assessments, 1):
            logger.info(f"  {i}. {assessment.name}")
            logger.info(f"     URL: {assessment.url}")
        
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ CATALOG BUILD COMPLETE")
        logger.info("=" * 70)
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ FAILED: {e}", exc_info=True)
        return 1
    
    finally:
        scraper.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
