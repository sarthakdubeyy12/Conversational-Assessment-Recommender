"""HTML catalog parser."""

from typing import List

from src.catalog.domain.entities import Assessment


class CatalogParser:
    """Parses HTML into Assessment entities."""
    
    def parse(self, html: str) -> List[Assessment]:
        pass
