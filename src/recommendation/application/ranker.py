"""Rank recommendations."""

from typing import List

from src.recommendation.domain.entities import Recommendation
from src.recommendation.domain.interfaces import IRanker


class RecommendationRanker(IRanker):
    """Ranks and limits recommendations."""
    
    def rank(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        pass
    
    def limit(self, recommendations: List[Recommendation], max_count: int = 10) -> List[Recommendation]:
        pass
