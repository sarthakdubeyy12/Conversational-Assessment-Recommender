"""Extract hiring criteria from conversation."""

from typing import Dict, Any

from src.recommendation.domain.entities import HiringCriteria


class CriteriaExtractor:
    """Extracts structured hiring criteria."""
    
    def extract(self, conversation_context: Dict[str, Any]) -> HiringCriteria:
        pass
