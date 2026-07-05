#!/usr/bin/env python3
"""
Build catalog from already-downloaded HTML files.

This script parses the 203 HTML files that were successfully downloaded
and extracts assessment information from them.
"""

import sys
import json
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.shared.logging.logger import get_logger, setup_logger

setup_logger("catalog_builder", level="INFO")
logger = get_logger(__name__)


def generate_id(url: str) -> str:
    """Generate unique ID from URL."""
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def extract_assessment_from_html(html_content: str, file_path: str) -> dict:
    """Extract assessment information from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Try to extract title
    title = None
    h1 = soup.find('h1')
    if h1:
        title = h1.get_text().strip()
    
    if not title:
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            # Clean up title (remove " | SHL" suffix)
            title = title.split('|')[0].strip()
    
    # Try to extract description
    description = None
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        description = meta_desc.get('content', '').strip()
    
    # Extract text content for analysis
    text_content = soup.get_text().lower()
    
    # Determine category and type from content
    category = None
    test_type = None
    
    if any(kw in text_content for kw in ['cognitive', 'reasoning', 'numerical', 'verbal', 'inductive']):
        category = "Cognitive Assessments"
        if 'numerical' in text_content:
            test_type = "numerical_reasoning"
        elif 'verbal' in text_content:
            test_type = "verbal_reasoning"
        elif 'inductive' in text_content:
            test_type = "inductive_reasoning"
        else:
            test_type = "cognitive_ability"
    elif any(kw in text_content for kw in ['personality', 'opq', 'questionnaire']):
        category = "Personality Assessments"
        test_type = "personality"
    elif any(kw in text_content for kw in ['situational', 'judgment', 'sjt']):
        category = "Behavioral Assessments"
        test_type = "situational_judgment"
    elif any(kw in text_content for kw in ['skills', 'simulation', 'coding', 'technical']):
        category = "Technical Skills"
        test_type = "skills_assessment"
    
    # Extract links to find the actual assessment URL
    assessment_url = None
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if href and ('/products/assessments/' in href or '/solutions/products/assessments/' in href):
            # Look for specific assessment pages (not category pages)
            if any(kw in href for kw in ['opq', 'gsa', 'sjt', 'verify', 'mq', 'svar']):
                if href.startswith('/'):
                    assessment_url = f"https://www.shl.com{href}"
                elif href.startswith('http'):
                    assessment_url = href
                break
    
    return {
        'title': title,
        'description': description,
        'category': category,
        'test_type': test_type,
        'url': assessment_url,
        'file': file_path
    }


def build_catalog():
    """Build catalog from downloaded HTML files."""
    logger.info("=" * 70)
    logger.info("BUILDING CATALOG FROM DOWNLOADED HTML FILES")
    logger.info("=" * 70)
    
    html_dir = Path("data/raw")
    if not html_dir.exists():
        logger.error("data/raw directory not found")
        return 0
    
    html_files = list(html_dir.glob("*.html"))
    logger.info(f"Found {len(html_files)} HTML files")
    
    # Extract information from each file
    assessments_info = []
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            info = extract_assessment_from_html(html_content, html_file.name)
            if info['title'] and info['url']:
                assessments_info.append(info)
        
        except Exception as e:
            logger.warning(f"Error processing {html_file.name}: {e}")
            continue
    
    # Deduplicate by URL
    seen_urls = set()
    unique_assessments = []
    
    for info in assessments_info:
        if info['url'] not in seen_urls:
            seen_urls.add(info['url'])
            unique_assessments.append(info)
    
    logger.info(f"Found {len(unique_assessments)} unique assessments")
    
    # Build catalog entries
    catalog = []
    timestamp = datetime.utcnow().isoformat()
    
    for info in unique_assessments:
        assessment = {
            "id": generate_id(info['url']),
            "name": info['title'],
            "url": info['url'],
            "description": info['description'] or f"{info['title']} - SHL Assessment",
            "category": info['category'] or "Assessments",
            "test_type": info['test_type'] or "assessment",
            "skills_measured": [],
            "competencies": [],
            "duration_minutes": None,
            "question_count": None,
            "languages": ["English"],
            "remote_testing": True,
            "adaptive_testing": False,
            "mobile_compatible": True,
            "job_levels": [],
            "suitable_roles": [],
            "industries": [],
            "product_code": None,
            "assessment_family": None,
            "version": "2024",
            "tags": [],
            "difficulty_level": None,
            "delivery_method": "online",
            "metadata": {
                "source": "scraped_html",
                "source_file": info['file'],
                "created_at": timestamp,
            },
            "scraped_at": timestamp,
            "last_updated": timestamp,
        }
        catalog.append(assessment)
    
    # Save catalog
    catalog_path = Path("data/processed/catalog.json")
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Saved {len(catalog)} assessments to {catalog_path}")
    
    # Print summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("CATALOG SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total Assessments: {len(catalog)}")
    
    # Group by category
    by_category = {}
    for item in catalog:
        cat = item.get("category", "Unknown")
        by_category[cat] = by_category.get(cat, 0) + 1
    
    logger.info("\nBy Category:")
    for category, count in sorted(by_category.items()):
        logger.info(f"  {category}: {count}")
    
    logger.info("\nAssessments:")
    for i, item in enumerate(catalog, 1):
        logger.info(f"  {i:2d}. {item['name']}")
        logger.info(f"      URL: {item['url']}")
        logger.info(f"      Category: {item.get('category', 'N/A')}")
    
    logger.info("")
    logger.info("=" * 70)
    
    return len(catalog)


if __name__ == "__main__":
    try:
        count = build_catalog()
        sys.exit(0 if count > 0 else 1)
    except Exception as e:
        logger.error(f"Failed to build catalog: {e}", exc_info=True)
        sys.exit(1)
