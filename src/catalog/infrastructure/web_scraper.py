"""Web scraping implementation."""

from src.catalog.domain.interfaces import ICatalogScraper


class WebScraper(ICatalogScraper):
    """BeautifulSoup/Playwright implementation."""
    
    async def scrape_catalog(self, url: str) -> str:
        pass
