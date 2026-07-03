"""Recommendation service orchestration."""

from typing import List

from src.recommendation.domain.entities import HiringCriteria, Recommendation
from src.recommendation.domain.interfaces import IRecommendationEngine


class RecommendationService:
    """Orchestrates recommendation logic."""
    
    def __init__(self, engine: IRecommendationEngine) -> None:
        self._engine = engine
    
    async def get_recommendations(self, criteria: HiringCriteria) -> List[Recommendation]:
        return await self._engine.recommend(criteria)
