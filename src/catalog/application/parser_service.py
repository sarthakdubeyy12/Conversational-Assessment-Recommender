"""Catalog parsing service."""

from typing import List

from src.catalog.domain.entities import Assessment


class ParserService:
    """Parses raw catalog data into domain entities."""
    
    def parse_html_to_assessments(self, html_content: str) -> List[Assessment]:
        pass
