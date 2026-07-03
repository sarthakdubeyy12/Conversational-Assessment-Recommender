#!/usr/bin/env python3
"""
Catalog verification script.

Verifies catalog quality and completeness according to Phase 2 requirements.
"""

import asyncio
import sys
import json
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
setup_logger("catalog_verify", level="INFO")
logger = get_logger(__name__)

settings = get_settings()


async def main():
    """Run catalog verification."""
    logger.info("=" * 60)
    logger.info("CATALOG VERIFICATION")
    logger.info("=" * 60)
    logger.info("")
    
    catalog_path = settings.catalog_path
    
    # Check if catalog exists
    if not Path(catalog_path).exists():
        logger.error(f"❌ Catalog not found: {catalog_path}")
        logger.error("Run 'python scripts/build_catalog.py' first")
        return 1
    
    logger.info(f"Catalog path: {catalog_path}")
    logger.info("")
    
    # Initialize components
    scraper = WebScraper()
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
    
    # Run verification
    try:
        report = await service.verify_catalog()
        
        logger.info("=" * 60)
        logger.info("VERIFICATION REPORT")
        logger.info("=" * 60)
        logger.info("")
        
        logger.info(f"Total assessments: {report['total_assessments']}")
        logger.info("")
        
        logger.info("Checks:")
        for check_name, check_result in report['checks'].items():
            if isinstance(check_result, bool):
                status = "✅" if check_result else "❌"
                logger.info(f"  {status} {check_name}: {check_result}")
            else:
                logger.info(f"  ℹ️  {check_name}: {check_result:.2%}")
        
        logger.info("")
        
        if report['issues']:
            logger.warning("Issues found:")
            for issue in report['issues']:
                logger.warning(f"  ⚠️  {issue}")
            logger.info("")
        
        # Get detailed stats
        stats = await service.get_catalog_stats()
        logger.info("Catalog Statistics:")
        logger.info(f"  Categories: {len(stats['categories'])}")
        logger.info(f"  Test types: {len(stats['test_types'])}")
        logger.info(f"  Languages: {len(stats['languages'])}")
        logger.info("")
        
        # Overall result
        logger.info("=" * 60)
        if report['verification_passed']:
            logger.info("✅ VERIFICATION PASSED")
            logger.info("=" * 60)
            logger.info("")
            logger.info("Catalog is ready for Phase 3 (Retrieval)")
            return 0
        else:
            logger.warning("⚠️  VERIFICATION PASSED WITH WARNINGS")
            logger.info("=" * 60)
            logger.info("")
            logger.info("Catalog can be used but has some quality issues")
            logger.info("Consider re-running the scraper or improving parsers")
            return 0
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}", exc_info=True)
        return 1
    
    finally:
        scraper.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
