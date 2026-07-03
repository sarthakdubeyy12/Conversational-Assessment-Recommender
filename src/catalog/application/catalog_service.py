"""
Catalog service orchestration.

Orchestrates the complete catalog ingestion pipeline:
Crawl → Fetch → Parse → Validate → Normalize → Deduplicate → Store
"""

from typing import List, Optional, Set
from datetime import datetime

from src.catalog.domain.entities import Assessment
from src.catalog.domain.interfaces import (
    ICatalogRepository,
    IWebScraper,
    ILinkDiscoverer,
    IHTMLParser,
    IAssessmentValidator,
    IDataNormalizer,
)
from src.shared.logging.logger import get_logger
from src.shared.utils.timing import Stopwatch

logger = get_logger(__name__)


class CatalogService:
    """
    Orchestrates catalog operations.
    
    Responsibilities:
    - Coordinate scraping pipeline
    - Manage catalog lifecycle
    - Provide catalog access
    """
    
    def __init__(
        self,
        repository: ICatalogRepository,
        scraper: IWebScraper,
        link_discoverer: ILinkDiscoverer,
        parser: IHTMLParser,
        validator: IAssessmentValidator,
        normalizer: IDataNormalizer,
    ) -> None:
        """
        Initialize catalog service.
        
        Args:
            repository: Catalog storage
            scraper: Web scraper
            link_discoverer: Link discovery
            parser: HTML parser
            validator: Data validator
            normalizer: Data normalizer
        """
        self._repository = repository
        self._scraper = scraper
        self._link_discoverer = link_discoverer
        self._parser = parser
        self._validator = validator
        self._normalizer = normalizer
        
        logger.info("CatalogService initialized")
    
    async def build_catalog(self, start_url: str, save_snapshot: bool = True) -> int:
        """
        Build complete catalog from scratch.
        
        Pipeline:
        1. Discover assessment URLs
        2. Fetch pages (saves raw HTML)
        3. Parse HTML
        4. Validate data
        5. Normalize data
        6. Deduplicate
        7. Save to storage
        8. Save snapshot (optional)
        
        Args:
            start_url: Starting URL for crawling
            save_snapshot: Whether to save timestamped snapshot
        
        Returns:
            Number of assessments saved
        """
        logger.info("=" * 60)
        logger.info("CATALOG INGESTION PIPELINE STARTED")
        logger.info("=" * 60)
        
        timer = Stopwatch()
        timer.start()
        
        try:
            # Step 1: Discover links
            logger.info("Step 1/7: Discovering assessment URLs...")
            urls = await self._link_discoverer.discover_assessment_links(start_url)
            logger.info(f"Discovered {len(urls)} assessment URLs")
            
            if not urls:
                logger.warning("No assessment URLs discovered. Exiting.")
                return 0
            
            # Step 2: Fetch pages
            logger.info("Step 2/7: Fetching pages...")
            pages = await self._scraper.fetch_pages(list(urls))
            logger.info(f"Fetched {len(pages)} pages successfully")
            
            if not pages:
                logger.warning("No pages fetched successfully. Exiting.")
                return 0
            
            # Step 3: Parse HTML
            logger.info("Step 3/7: Parsing HTML...")
            assessments = []
            parse_failures = 0
            
            for page in pages:
                assessment = self._parser.parse(page)
                if assessment:
                    assessments.append(assessment)
                else:
                    parse_failures += 1
            
            logger.info(
                f"Parsed {len(assessments)} assessments "
                f"({parse_failures} parse failures)"
            )
            
            if not assessments:
                logger.warning("No assessments parsed successfully. Exiting.")
                return 0
            
            # Step 4: Validate
            logger.info("Step 4/7: Validating assessments...")
            valid_assessments = []
            validation_failures = 0
            
            for assessment in assessments:
                if self._validator.validate(assessment):
                    valid_assessments.append(assessment)
                else:
                    validation_failures += 1
            
            logger.info(
                f"Validated {len(valid_assessments)} assessments "
                f"({validation_failures} validation failures)"
            )
            
            if not valid_assessments:
                logger.warning("No valid assessments. Exiting.")
                return 0
            
            # Step 5: Normalize
            logger.info("Step 5/7: Normalizing data...")
            normalized_assessments = [
                self._normalizer.normalize(assessment)
                for assessment in valid_assessments
            ]
            logger.info(f"Normalized {len(normalized_assessments)} assessments")
            
            # Step 6: Deduplicate
            logger.info("Step 6/7: Deduplicating...")
            unique_assessments = self._deduplicate(normalized_assessments)
            duplicates_removed = len(normalized_assessments) - len(unique_assessments)
            logger.info(
                f"Deduplicated: {len(unique_assessments)} unique assessments "
                f"({duplicates_removed} duplicates removed)"
            )
            
            # Step 7: Save
            logger.info("Step 7/7: Saving to storage...")
            await self._repository.save(unique_assessments)
            logger.info(f"Saved {len(unique_assessments)} assessments to catalog")
            
            # Step 8: Save snapshot (optional)
            if save_snapshot:
                await self._save_snapshot(unique_assessments)
            
            elapsed = timer.elapsed()
            
            logger.info("=" * 60)
            logger.info("CATALOG INGESTION PIPELINE COMPLETED")
            logger.info(f"Total time: {elapsed:.2f}s")
            logger.info(f"Assessments discovered: {len(urls)}")
            logger.info(f"Pages fetched: {len(pages)}")
            logger.info(f"Assessments parsed: {len(assessments)}")
            logger.info(f"Valid assessments: {len(valid_assessments)}")
            logger.info(f"Unique assessments: {len(unique_assessments)}")
            logger.info(f"Final catalog size: {len(unique_assessments)}")
            logger.info("=" * 60)
            
            return len(unique_assessments)
            
        except Exception as e:
            logger.error(f"Catalog ingestion failed: {e}", exc_info=True)
            raise
    
    async def get_all_assessments(self) -> List[Assessment]:
        """
        Get all assessments from catalog.
        
        Returns:
            List of all assessments
        """
        return await self._repository.load()
    
    async def get_assessment_by_id(self, assessment_id: str) -> Optional[Assessment]:
        """
        Get assessment by ID.
        
        Args:
            assessment_id: Assessment ID
        
        Returns:
            Assessment or None if not found
        """
        return await self._repository.find_by_id(assessment_id)
    
    async def catalog_exists(self) -> bool:
        """
        Check if catalog exists.
        
        Returns:
            True if catalog file exists
        """
        return await self._repository.exists()
    
    async def get_catalog_stats(self) -> dict:
        """
        Get catalog statistics.
        
        Returns:
            Dictionary with catalog stats
        """
        assessments = await self.get_all_assessments()
        
        # Gather statistics
        categories = set()
        test_types = set()
        total_skills = 0
        languages_set = set()
        
        for assessment in assessments:
            if assessment.category:
                categories.add(assessment.category)
            if assessment.test_type:
                test_types.add(assessment.test_type)
            total_skills += len(assessment.skills_measured)
            languages_set.update(assessment.languages)
        
        return {
            "total_assessments": len(assessments),
            "categories": list(categories),
            "test_types": list(test_types),
            "unique_skills": total_skills,
            "languages": list(languages_set),
            "last_updated": datetime.utcnow().isoformat(),
        }
    
    def _deduplicate(self, assessments: List[Assessment]) -> List[Assessment]:
        """
        Remove duplicate assessments.
        
        Deduplicates by ID (which is derived from URL).
        
        Args:
            assessments: List with potential duplicates
        
        Returns:
            List of unique assessments
        """
        seen_ids: Set[str] = set()
        unique: List[Assessment] = []
        
        for assessment in assessments:
            if assessment.id not in seen_ids:
                seen_ids.add(assessment.id)
                unique.append(assessment)
            else:
                logger.debug(f"Duplicate removed: {assessment.name}")
        
        return unique
    
    async def _save_snapshot(self, assessments: List[Assessment]) -> None:
        """
        Save timestamped snapshot of catalog.
        
        Args:
            assessments: Assessments to save
        """
        try:
            import json
            from pathlib import Path
            from datetime import datetime
            
            # Create snapshots directory
            snapshots_dir = Path("./data/snapshots")
            snapshots_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate timestamped filename
            timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
            snapshot_file = snapshots_dir / f"catalog_{timestamp}.json"
            
            # Save snapshot
            data = [assessment.to_dict() for assessment in assessments]
            with open(snapshot_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Snapshot saved: {snapshot_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save snapshot: {e}")
    
    async def verify_catalog(self) -> dict:
        """
        Verify catalog quality and completeness.
        
        Returns:
            Verification report
        """
        logger.info("Verifying catalog...")
        
        try:
            assessments = await self.get_all_assessments()
            
            report = {
                "total_assessments": len(assessments),
                "verification_passed": True,
                "issues": [],
                "checks": {}
            }
            
            # Check 1: All assessments have names
            missing_names = [a for a in assessments if not a.name]
            report["checks"]["has_names"] = len(missing_names) == 0
            if missing_names:
                report["issues"].append(f"{len(missing_names)} assessments missing names")
                report["verification_passed"] = False
            
            # Check 2: All assessments have descriptions
            missing_descriptions = [a for a in assessments if not a.description]
            report["checks"]["has_descriptions"] = len(missing_descriptions) == 0
            if missing_descriptions:
                report["issues"].append(f"{len(missing_descriptions)} assessments missing descriptions")
            
            # Check 3: All assessments have valid URLs
            from src.shared.utils.validators import is_valid_url
            invalid_urls = [a for a in assessments if not is_valid_url(a.url)]
            report["checks"]["valid_urls"] = len(invalid_urls) == 0
            if invalid_urls:
                report["issues"].append(f"{len(invalid_urls)} assessments have invalid URLs")
                report["verification_passed"] = False
            
            # Check 4: All assessments have categories
            missing_categories = [a for a in assessments if not a.category]
            report["checks"]["has_categories"] = len(missing_categories) == 0
            if missing_categories:
                report["issues"].append(f"{len(missing_categories)} assessments missing categories")
            
            # Check 5: All assessments have test types
            missing_test_types = [a for a in assessments if not a.test_type]
            report["checks"]["has_test_types"] = len(missing_test_types) == 0
            if missing_test_types:
                report["issues"].append(f"{len(missing_test_types)} assessments missing test types")
            
            # Check 6: URLs are unique
            urls = [a.url for a in assessments]
            unique_urls = set(urls)
            report["checks"]["unique_urls"] = len(urls) == len(unique_urls)
            if len(urls) != len(unique_urls):
                duplicates = len(urls) - len(unique_urls)
                report["issues"].append(f"{duplicates} duplicate URLs found")
                report["verification_passed"] = False
            
            # Check 7: IDs are unique
            ids = [a.id for a in assessments]
            unique_ids = set(ids)
            report["checks"]["unique_ids"] = len(ids) == len(unique_ids)
            if len(ids) != len(unique_ids):
                duplicates = len(ids) - len(unique_ids)
                report["issues"].append(f"{duplicates} duplicate IDs found")
                report["verification_passed"] = False
            
            # Check 8: Assessments have skills or competencies
            with_skills = [a for a in assessments if a.skills_measured or a.competencies]
            report["checks"]["has_skills_ratio"] = len(with_skills) / len(assessments) if assessments else 0
            
            # Check 9: URLs are from SHL domain
            shl_urls = [a for a in assessments if "shl.com" in a.url.lower()]
            report["checks"]["shl_domain_ratio"] = len(shl_urls) / len(assessments) if assessments else 0
            if len(shl_urls) < len(assessments) * 0.9:  # At least 90% should be SHL
                report["issues"].append(f"Only {len(shl_urls)}/{len(assessments)} URLs from SHL domain")
            
            logger.info(f"Verification complete: {'PASSED' if report['verification_passed'] else 'FAILED'}")
            
            return report
            
        except Exception as e:
            logger.error(f"Verification failed: {e}", exc_info=True)
            return {
                "verification_passed": False,
                "issues": [f"Verification error: {str(e)}"],
                "checks": {}
            }
