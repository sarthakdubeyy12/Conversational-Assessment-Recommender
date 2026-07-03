"""Scraper orchestration service."""

from src.catalog.domain.interfaces import ICatalogScraper


class ScraperService:
    """Orchestrates web scraping operations."""
    
    def __init__(self, scraper: ICatalogScraper) -> None:
        self._scraper = scraper
    
    async def scrape_shl_catalog(self, url: str) -> str:
        return await self._scraper.scrape_catalog(url)
