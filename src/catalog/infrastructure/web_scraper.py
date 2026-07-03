"""
Web scraper infrastructure.

Handles HTTP requests with retry logic, rate limiting, and error handling.
Uses requests library for simplicity and reliability.
"""

import asyncio
import time
from typing import List, Optional
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.catalog.domain.entities import ScrapedPage
from src.catalog.domain.interfaces import IWebScraper
from src.shared.exceptions.catalog_exceptions import ScrapingException
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class WebScraper(IWebScraper):
    """
    Production-grade web scraper.
    
    Features:
    - Automatic retries with exponential backoff
    - Rate limiting
    - User agent rotation
    - Timeout handling
    - Connection pooling
    - Error recovery
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        timeout: int = 30,
        rate_limit_delay: float = 1.0,
        user_agent: Optional[str] = None,
        save_raw_html: bool = False,
        raw_html_dir: Optional[str] = None
    ):
        """
        Initialize scraper.
        
        Args:
            max_retries: Maximum retry attempts
            backoff_factor: Exponential backoff multiplier
            timeout: Request timeout in seconds
            rate_limit_delay: Delay between requests in seconds
            user_agent: Custom user agent string
            save_raw_html: Whether to save raw HTML files
            raw_html_dir: Directory to save raw HTML (if save_raw_html=True)
        """
        self.max_retries = max_retries
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0.0
        self.save_raw_html = save_raw_html
        self.raw_html_dir = raw_html_dir
        self.page_counter = 0
        
        # Default user agent
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        logger.info(f"WebScraper initialized with {max_retries} retries, {timeout}s timeout")
    
    async def fetch_page(self, url: str) -> ScrapedPage:
        """
        Fetch single page with retry logic.
        
        Args:
            url: URL to fetch
        
        Returns:
            ScrapedPage with content
        
        Raises:
            ScrapingException: If fetching fails after retries
        """
        # Rate limiting
        await self._rate_limit()
        
        logger.info(f"Fetching: {url}")
        
        try:
            # Run blocking request in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.session.get(
                    url,
                    headers={"User-Agent": self.user_agent},
                    timeout=self.timeout
                )
            )
            
            response.raise_for_status()
            
            page = ScrapedPage(
                url=url,
                html_content=response.text,
                status_code=response.status_code,
                scraped_at=datetime.utcnow(),
                headers=dict(response.headers)
            )
            
            # Save raw HTML if enabled
            if self.save_raw_html and self.raw_html_dir:
                self._save_raw_html(page)
            
            logger.info(f"Successfully fetched: {url} ({len(page.html_content)} bytes)")
            return page
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout fetching {url}: {e}")
            raise ScrapingException(url, f"Request timeout after {self.timeout}s")
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching {url}: {e}")
            raise ScrapingException(url, f"HTTP {e.response.status_code}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching {url}: {e}")
            raise ScrapingException(url, str(e))
        
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}", exc_info=True)
            raise ScrapingException(url, f"Unexpected error: {type(e).__name__}")
    
    async def fetch_pages(self, urls: List[str]) -> List[ScrapedPage]:
        """
        Fetch multiple pages with rate limiting.
        
        Args:
            urls: List of URLs to fetch
        
        Returns:
            List of successfully fetched pages
        """
        logger.info(f"Fetching {len(urls)} pages...")
        
        pages = []
        failed = 0
        
        for i, url in enumerate(urls, 1):
            try:
                page = await self.fetch_page(url)
                pages.append(page)
                logger.info(f"Progress: {i}/{len(urls)} pages fetched")
            except ScrapingException as e:
                logger.warning(f"Failed to fetch {url}: {e.message}")
                failed += 1
                continue
        
        logger.info(
            f"Completed: {len(pages)} pages fetched successfully, {failed} failed"
        )
        
        return pages
    
    async def _rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        now = time.time()
        elapsed = now - self.last_request_time
        
        if elapsed < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - elapsed
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def _save_raw_html(self, page: ScrapedPage) -> None:
        """Save raw HTML to disk for debugging and reprocessing."""
        try:
            from pathlib import Path
            from src.shared.utils.hash_utils import hash_string
            
            # Create directory if needed
            raw_dir = Path(self.raw_html_dir)
            raw_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename from URL hash
            self.page_counter += 1
            url_hash = hash_string(page.url)[:12]
            filename = f"page_{self.page_counter:04d}_{url_hash}.html"
            filepath = raw_dir / filename
            
            # Save HTML
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"<!-- URL: {page.url} -->\n")
                f.write(f"<!-- Scraped: {page.scraped_at.isoformat()} -->\n")
                f.write(f"<!-- Status: {page.status_code} -->\n\n")
                f.write(page.html_content)
            
            logger.debug(f"Saved raw HTML: {filename}")
            
        except Exception as e:
            logger.warning(f"Failed to save raw HTML: {e}")
    
    def close(self) -> None:
        """Close session and cleanup resources."""
        self.session.close()
        logger.info("WebScraper session closed")
