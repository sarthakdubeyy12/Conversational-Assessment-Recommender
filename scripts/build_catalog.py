#!/usr/bin/env python3
"""
Catalog ingestion CLI script.

Runs the complete catalog scraping and ingestion pipeline.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.catalog.application.catalog_service import CatalogService
from src.catalog.infrastructure.web_scraper import WebScraper
from src.catalog.infrastructure.link_discoverer import LinkDiscoverer
from src.catalog.infrastructure.html_parser import AssessmentHTMLParser
from src.catalog.infrastructure.validators import AssessmentValidator
from src.catalog.infrastructure.normalizer import DataNormalizer
from src.catalog.infrastructure.json_repository import JSONCatalogRepository
from src.shared.config.settings import get_settings
from src.shared.logging.logger import get_logger, setup_logger

# Setup logging
setup_logger("catalog_build", level="INFO")
logger = get_logger(__name__)

settings = get_settings()


async def main():
    """Run catalog ingestion pipeline."""
    logger.info("Catalog Ingestion CLI")
    logger.info("=" * 60)
    
    # Get catalog URL from settings
    catalog_url = settings.catalog_url
    catalog_path = settings.catalog_path
    
    logger.info(f"Source URL: {catalog_url}")
    logger.info(f"Output path: {catalog_path}")
    logger.info("")
    
    # Initialize components
    logger.info("Initializing components...")
    
    scraper = WebScraper(
        max_retries=3,
        timeout=30,
        rate_limit_delay=1.0,
        save_raw_html=True,
        raw_html_dir="./data/raw"
    )
    
    link_discoverer = LinkDiscoverer(scraper)
    parser = AssessmentHTMLParser()
    validator = AssessmentValidator()
    normalizer = DataNormalizer()
    repository = JSONCatalogRepository(catalog_path)
    
    service = CatalogService(
        repository=repository,
        scraper=scraper,
        link_discoverer=link_discoverer,
        parser=parser,
        validator=validator,
        normalizer=normalizer,
    )
    
    logger.info("Components initialized")
    logger.info("")
    
    # Run pipeline
    try:
        count = await service.build_catalog(catalog_url, save_snapshot=True)
        
        logger.info("")
        logger.info("=" * 60)
        
        if count > 0:
            logger.info(f"✅ SUCCESS: {count} assessments saved to catalog")
            logger.info(f"Catalog location: {catalog_path}")
            
            # Print stats
            stats = await service.get_catalog_stats()
            logger.info("")
            logger.info("Catalog Statistics:")
            logger.info(f"  Total assessments: {stats['total_assessments']}")
            logger.info(f"  Categories: {len(stats['categories'])}")
            logger.info(f"  Test types: {len(stats['test_types'])}")
            logger.info(f"  Languages: {len(stats['languages'])}")
            
            # Run verification
            logger.info("")
            logger.info("Running verification...")
            report = await service.verify_catalog()
            
            if report['verification_passed']:
                logger.info("✅ Catalog verification PASSED")
            else:
                logger.warning("⚠️  Catalog verification has warnings")
                for issue in report['issues']:
                    logger.warning(f"  - {issue}")
            
            return 0
        else:
            logger.error("❌ FAILED: No assessments were saved")
            return 1
            
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        return 130
    
    except Exception as e:
        logger.error(f"❌ FAILED: {e}", exc_info=True)
        return 1
    
    finally:
        scraper.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
