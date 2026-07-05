"""
Link discovery component.

Crawls SHL catalog to discover all Individual Test Solution URLs.
Filters out non-assessment pages.
"""

from typing import Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from src.catalog.domain.interfaces import ILinkDiscoverer, IWebScraper
from src.shared.logging.logger import get_logger
from src.shared.utils.validators import is_valid_url

logger = get_logger(__name__)


class LinkDiscoverer(ILinkDiscoverer):
    """
    Discovers assessment URLs from SHL catalog.
    
    Crawls the catalog website to find all Individual Test Solution pages.
    Filters out irrelevant pages (bundles, jobs, resources, etc).
    """
    
    def __init__(self, scraper: IWebScraper):
        """
        Initialize discoverer.
        
        Args:
            scraper: Web scraper instance
        """
        self.scraper = scraper
        
        # Patterns to identify assessment pages (individual assessments, not category pages)
        self.assessment_patterns = [
            "/products/assessments/",  # New SHL URL structure
            "/solutions/products/assessments/",  # Old SHL URL structure
        ]
        
        # Patterns to exclude (category pages, bundles, non-assessments)
        self.exclude_patterns = [
            "/job-solutions/",
            "/job-focused-assessments/",  # Category page
            "/bundles/",
            "/blog/",
            "/resources/",
            "/about/",
            "/contact/",
            "/privacy/",
            "/terms/",
            "/careers/",
            "/services/",
            "/training-services/",
            "/practice-tests/",  # Not individual assessments
            "/assessment-and-development-centers/",  # Category page only
            ".pdf",
            ".jpg",
            ".png",
            ".css",
            ".js",
        ]
        
        # Category pages that should be crawled but not included as assessments
        self.category_patterns = [
            "/products/assessments/$",  # Main catalog page
            "/products/assessments$",
            "/behavioral-assessments/$",
            "/behavioral-assessments$",
            "/cognitive-assessments/$",
            "/cognitive-assessments$",
            "/personality-assessment/$",
            "/personality-assessment$",
            "/skills-and-simulations/$",
            "/skills-and-simulations$",
        ]
        
        logger.info("LinkDiscoverer initialized")
    
    async def discover_assessment_links(self, start_url: str) -> Set[str]:
        """
        Discover all valid assessment URLs from catalog.
        
        Args:
            start_url: Starting URL (catalog homepage)
        
        Returns:
            Set of unique assessment URLs
        """
        logger.info(f"Starting link discovery from: {start_url}")
        
        discovered_urls: Set[str] = set()
        visited_urls: Set[str] = set()
        to_visit: Set[str] = {start_url}
        
        while to_visit and len(visited_urls) < 200:  # Safety limit (increased for full catalog)
            url = to_visit.pop()
            
            if url in visited_urls:
                continue
            
            visited_urls.add(url)
            logger.info(f"Visiting: {url} (visited: {len(visited_urls)})")
            
            try:
                page = await self.scraper.fetch_page(url)
                soup = BeautifulSoup(page.html_content, "html.parser")
                
                # Extract all links
                for link in soup.find_all("a", href=True):
                    href = link.get("href")
                    if not href:
                        continue
                    
                    # Make absolute URL
                    absolute_url = urljoin(url, href)
                    
                    # Clean URL (remove fragments)
                    parsed = urlparse(absolute_url)
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    
                    # Skip if already processed
                    if clean_url in visited_urls or clean_url in discovered_urls:
                        continue
                    
                    # Check if assessment URL
                    if self._is_assessment_url(clean_url):
                        discovered_urls.add(clean_url)
                        logger.info(f"Found assessment: {clean_url}")
                    
                    # Check if should crawl further
                    elif self._should_crawl(clean_url, start_url):
                        to_visit.add(clean_url)
                
            except Exception as e:
                logger.warning(f"Error crawling {url}: {e}")
                continue
        
        logger.info(
            f"Discovery complete: {len(discovered_urls)} assessments found, "
            f"{len(visited_urls)} pages visited"
        )
        
        return discovered_urls
    
    def _is_assessment_url(self, url: str) -> bool:
        """
        Check if URL is an individual assessment page (not a category page).
        
        Args:
            url: URL to check
        
        Returns:
            True if individual assessment URL
        """
        import re
        
        if not is_valid_url(url):
            return False
        
        # Must match assessment patterns
        matches_pattern = any(pattern in url for pattern in self.assessment_patterns)
        if not matches_pattern:
            return False
        
        # Must not match exclude patterns
        matches_exclude = any(pattern in url for pattern in self.exclude_patterns)
        if matches_exclude:
            return False
        
        # Must not be a category page (category pages end with / or are exact matches)
        for cat_pattern in self.category_patterns:
            if re.search(cat_pattern, url):
                return False
        
        # URL must have at least 5 path segments to be an individual assessment
        # e.g., /products/assessments/cognitive-assessments/verify-gplus/
        # but not /products/assessments/ or /products/assessments/cognitive-assessments/
        path = url.split('?')[0].rstrip('/')
        path_segments = [s for s in path.split('/') if s]
        
        # Individual assessments have at least 4 segments: products, assessments, category, name
        if len(path_segments) < 4:
            return False
        
        return True
    
    def _should_crawl(self, url: str, base_url: str) -> bool:
        """
        Check if URL should be crawled for more links.
        
        Args:
            url: URL to check
            base_url: Base URL (stay within domain)
        
        Returns:
            True if should crawl
        """
        if not is_valid_url(url):
            return False
        
        # Stay within same domain
        base_domain = urlparse(base_url).netloc
        url_domain = urlparse(url).netloc
        
        if base_domain != url_domain:
            return False
        
        # Don't crawl excluded patterns
        if any(pattern in url for pattern in self.exclude_patterns):
            return False
        
        # Don't crawl non-HTML resources
        if url.endswith((".pdf", ".jpg", ".png", ".css", ".js")):
            return False
        
        return True
