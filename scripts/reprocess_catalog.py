#!/usr/bin/env python3
"""
Reprocess catalog from raw HTML.

Reprocesses raw HTML files without hitting the SHL website again.
Useful for:
- Testing parser improvements
- Debugging parsing issues
- Regenerating catalog after parser changes
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.catalog.domain.entities import ScrapedPage
from src.catalog.infrastructure.html_parser import AssessmentHTMLParser
from src.catalog.infrastructure.validators import AssessmentValidator
from src.catalog.infrastructure.normalizer import DataNormalizer
from src.catalog.infrastructure.json_repository import JSONCatalogRepository
from src.shared.config.settings import get_settings
from src.shared.logging.logger import get_logger, setup_logger
from src.shared.utils.timing import Timer

# Setup logging
setup_logger("catalog_reprocess", level="INFO")
logger = get_logger(__name__)

settings = get_settings()


async def main():
    """Reprocess raw HTML files."""
    logger.info("=" * 60)
    logger.info("CATALOG REPROCESSING FROM RAW HTML")
    logger.info("=" * 60)
    logger.info("")
    
    raw_dir = Path("./data/raw")
    catalog_path = settings.catalog_path
    
    # Check if raw HTML exists
    if not raw_dir.exists():
        logger.error(f"❌ Raw HTML directory not found: {raw_dir}")
        logger.error("Run 'python scripts/build_catalog.py' first")
        return 1
    
    html_files = list(raw_dir.glob("*.html"))
    
    if not html_files:
        logger.error(f"❌ No HTML files found in {raw_dir}")
        return 1
    
    logger.info(f"Found {len(html_files)} raw HTML files")
    logger.info(f"Output: {catalog_path}")
    logger.info("")
    
    timer = Timer()
    timer.start()
    
    # Initialize components
    parser = AssessmentHTMLParser()
    validator = AssessmentValidator()
    normalizer = DataNormalizer()
    repository = JSONCatalogRepository(catalog_path)
    
    # Process HTML files
    logger.info("Step 1/5: Loading raw HTML...")
    pages = []
    
    for html_file in html_files:
        try:
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Extract URL from HTML comment
            url = None
            for line in content.split("\n")[:10]:
                if "<!-- URL:" in line:
                    url = line.replace("<!-- URL:", "").replace("-->", "").strip()
                    break
            
            if not url:
                url = f"https://www.shl.com/unknown/{html_file.stem}"
            
            page = ScrapedPage(
                url=url,
                html_content=content,
                status_code=200,
                scraped_at=datetime.utcnow(),
                headers={}
            )
            pages.append(page)
            
        except Exception as e:
            logger.warning(f"Failed to load {html_file.name}: {e}")
            continue
    
    logger.info(f"Loaded {len(pages)} HTML files")
    
    # Parse
    logger.info("Step 2/5: Parsing HTML...")
    assessments = []
    parse_failures = 0
    
    for page in pages:
        assessment = parser.parse(page)
        if assessment:
            assessments.append(assessment)
        else:
            parse_failures += 1
    
    logger.info(f"Parsed {len(assessments)} assessments ({parse_failures} failures)")
    
    # Validate
    logger.info("Step 3/5: Validating...")
    valid_assessments = []
    validation_failures = 0
    
    for assessment in assessments:
        if validator.validate(assessment):
            valid_assessments.append(assessment)
        else:
            validation_failures += 1
    
    logger.info(f"Validated {len(valid_assessments)} assessments ({validation_failures} failures)")
    
    # Normalize
    logger.info("Step 4/5: Normalizing...")
    normalized_assessments = [
        normalizer.normalize(assessment)
        for assessment in valid_assessments
    ]
    logger.info(f"Normalized {len(normalized_assessments)} assessments")
    
    # Deduplicate
    seen_ids = set()
    unique_assessments = []
    
    for assessment in normalized_assessments:
        if assessment.id not in seen_ids:
            seen_ids.add(assessment.id)
            unique_assessments.append(assessment)
    
    duplicates = len(normalized_assessments) - len(unique_assessments)
    logger.info(f"Deduplicated: {len(unique_assessments)} unique ({duplicates} duplicates removed)")
    
    # Save
    logger.info("Step 5/5: Saving...")
    await repository.save(unique_assessments)
    logger.info(f"Saved {len(unique_assessments)} assessments to {catalog_path}")
    
    elapsed = timer.elapsed()
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("REPROCESSING COMPLETE")
    logger.info(f"Time: {elapsed:.2f}s")
    logger.info(f"Raw HTML files: {len(html_files)}")
    logger.info(f"Parsed: {len(assessments)}")
    logger.info(f"Valid: {len(valid_assessments)}")
    logger.info(f"Final: {len(unique_assessments)}")
    logger.info("=" * 60)
    logger.info("")
    logger.info("✅ Catalog regenerated from raw HTML")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
