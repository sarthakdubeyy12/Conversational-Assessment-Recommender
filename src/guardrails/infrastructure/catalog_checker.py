"""Catalog checking logic."""

from typing import List


class CatalogChecker:
    """Checks data against catalog."""
    
    def __init__(self, catalog_urls: List[str]) -> None:
        self._catalog_urls = catalog_urls
    
    def is_in_catalog(self, url: str) -> bool:
        pass
