#!/usr/bin/env python3
"""
Scrape real SHL Individual Test Solutions catalog.

This script:
1. Discovers assessment URLs from downloaded HTML files
2. Fetches additional assessment pages from SHL website
3. Parses assessment metadata from each page
4. Builds catalog.json from scraped data only
"""

import asyncio
import sys
import json
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.catalog.infrastructure.web_scraper import WebScraper
from src.catalog.infrastructure.html_parser import AssessmentHTMLParser
from src.catalog.infrastructure.validators import AssessmentValidator
from src.catalog.infrastructure.normalizer import DataNormalizer
from src.shared.logging.logger import get_logger, setup_logger

setup_logger("catalog_scraper", level="INFO")
logger = get_logger(__name__)


def discover_urls_from_html():
    """Extract assessment URLs from already-downloaded HTML files."""
    logger.info("Discovering assessment URLs from downloaded HTML files...")
    
    html_dir = Path("data/raw")
    if not html_dir.exists():
        logger.warning("No raw HTML directory found")
        return set()
    
    html_files = list(html_dir.glob("*.html"))
    logger.info(f"Analyzing {len(html_files)} HTML files")
    
    discovered_urls = set()
    base_url = "https://www.shl.com"
    
    # Patterns to identify individual assessment pages
    assessment_indicators = [
        '/behavioral-assessments/global-skills-assessment',
        '/behavioral-assessments/situation-judgement',
        '/behavioral-assessments/universal-competency',
        '/behavioral-assessments/realistic-job',
        '/personality-assessment/shl-occupational',
        '/personality-assessment/shl-motivation',
        '/cognitive-assessments/verify',
        '/skills-and-simulations/',
    ]
    
    # Patterns to exclude (not individual assessments)
    exclude_patterns = [
        '/blog/', '/resources/', '/webinars/', '/whitepapers/',
        '/services/', '/training/', '/practice-test', '/careers/',
        '/job-solutions/', '/job-focused-assessments/',
        '/bundles/', '/about/', '/contact/', '/legal/',
        '.pdf', '.jpg', '.png', 'mailto:', 'tel:', '#',
        '/shldirect/', '/login', '/register',
    ]
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html = f.read()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').strip()
                if not href:
                    continue
                
                # Make absolute URL
                if href.startswith('/'):
                    url = base_url + href
                elif href.startswith('http'):
                    url = href
                else:
                    continue
                
                # Must be SHL domain
                if 'shl.com' not in url:
                    continue
                
                # Clean URL
                url = url.split('?')[0].split('#')[0].rstrip('/')
                
                # Check if it matches assessment indicators
                is_assessment = any(indicator in url for indicator in assessment_indicators)
                
                # Exclude non-assessment pages
                is_excluded = any(pattern in url for pattern in exclude_patterns)
                
                if is_assessment and not is_excluded:
                    discovered_urls.add(url)
        
        except Exception as e:
            logger.warning(f"Error reading {html_file}: {e}")
            continue
    
    logger.info(f"Discovered {len(discovered_urls)} unique assessment URLs")
    return discovered_urls


async def fetch_and_parse_assessments(urls):
    """Fetch pages and parse assessment data."""
    logger.info(f"Fetching and parsing {len(urls)} assessment pages...")
    
    scraper = WebScraper(
        save_raw_html=True,
        raw_html_dir="./data/raw",
        timeout=15,
        rate_limit_delay=1.5
    )
    parser = AssessmentHTMLParser()
    validator = AssessmentValidator()
    normalizer = DataNormalizer()
    
    assessments = []
    failed_urls = []
    
    for i, url in enumerate(sorted(urls), 1):
        logger.info(f"[{i}/{len(urls)}] Fetching {url}")
        
        try:
            # Fetch page
            page = await scraper.fetch_page(url)
            
            if not page or page.status_code != 200:
                logger.warning(f"Failed to fetch {url} (status: {page.status_code if page else 'None'})")
                failed_urls.append(url)
                continue
            
            # Parse assessment
            assessment = parser.parse(page)
            
            if not assessment:
                logger.warning(f"Failed to parse {url}")
                failed_urls.append(url)
                continue
            
            # Validate
            if not validator.validate(assessment):
                logger.warning(f"Validation failed for {url}")
                failed_urls.append(url)
                continue
            
            # Normalize
            assessment = normalizer.normalize(assessment)
            assessments.append(assessment)
            
            logger.info(f"✅ Successfully processed: {assessment.name}")
            
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            failed_urls.append(url)
            continue
    
    scraper.close()
    
    logger.info(f"Successfully processed {len(assessments)} assessments")
    if failed_urls:
        logger.warning(f"Failed to process {len(failed_urls)} URLs")
    
    return assessments


def save_catalog(assessments):
    """Save assessments to catalog.json."""
    catalog_path = Path("data/processed/catalog.json")
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to dict format
    catalog_data = []
    for assessment in assessments:
        data = {
            "id": assessment.id,
            "name": assessment.name,
            "url": assessment.url,
            "description": assessment.description,
            "category": assessment.category,
            "test_type": assessment.test_type,
            "skills_measured": assessment.skills_measured or [],
            "competencies": assessment.competencies or [],
            "duration_minutes": assessment.duration_minutes,
            "question_count": assessment.question_count,
            "languages": assessment.languages or [],
            "remote_testing": assessment.remote_testing,
            "adaptive_testing": assessment.adaptive_testing,
            "mobile_compatible": assessment.mobile_compatible,
            "job_levels": assessment.job_levels or [],
            "suitable_roles": assessment.suitable_roles or [],
            "industries": assessment.industries or [],
            "product_code": assessment.product_code,
            "assessment_family": assessment.assessment_family,
            "version": assessment.version,
            "tags": assessment.tags or [],
            "difficulty_level": assessment.difficulty_level,
            "delivery_method": assessment.delivery_method,
            "metadata": assessment.metadata or {},
            "scraped_at": assessment.scraped_at.isoformat() if assessment.scraped_at else None,
            "last_updated": assessment.last_updated.isoformat() if assessment.last_updated else None,
        }
        catalog_data.append(data)
    
    # Save to file
    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Saved {len(catalog_data)} assessments to {catalog_path}")
    
    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("CATALOG SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total Assessments: {len(catalog_data)}")
    
    # Group by category
    by_category = {}
    for item in catalog_data:
        cat = item.get("category", "Unknown")
        by_category[cat] = by_category.get(cat, 0) + 1
    
    logger.info("\nBy Category:")
    for category, count in sorted(by_category.items()):
        logger.info(f"  {category}: {count}")
    
    logger.info("\nAssessments:")
    for i, item in enumerate(catalog_data, 1):
        logger.info(f"  {i}. {item['name']}")
        logger.info(f"     URL: {item['url']}")
        logger.info(f"     Category: {item.get('category', 'N/A')}")
        logger.info(f"     Type: {item.get('test_type', 'N/A')}")
        logger.info("")
    
    logger.info("=" * 70)
    
    return len(catalog_data)


async def main():
    """Main scraping workflow."""
    logger.info("=" * 70)
    logger.info("SHL CATALOG SCRAPER - REAL DATA ONLY")
    logger.info("=" * 70)
    logger.info("")
    
    # Step 1: Discover URLs from downloaded HTML
    urls = discover_urls_from_html()
    
    if not urls:
        logger.error("No assessment URLs discovered. Exiting.")
        return 1
    
    logger.info(f"\nDiscovered assessment URLs:")
    for i, url in enumerate(sorted(urls), 1):
        logger.info(f"  {i}. {url}")
    
    logger.info("")
    
    # Step 2: Fetch and parse assessments
    assessments = await fetch_and_parse_assessments(urls)
    
    if not assessments:
        logger.error("No assessments were successfully parsed. Exiting.")
        return 1
    
    # Step 3: Save catalog
    count = save_catalog(assessments)
    
    logger.info("")
    logger.info("=" * 70)
    logger.info(f"✅ SCRAPING COMPLETE: {count} assessments in catalog")
    logger.info("=" * 70)
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
