"""Recommendation domain interfaces."""

from abc import ABC, abstractmethod
from typing import List

from src.recommendation.domain.entities import HiringCriteria, Recommendation


class IRecommendationEngine(ABC):
    """Interface for recommendation engine."""
    
    @abstractmethod
    async def recommend(self, criteria: HiringCriteria) -> List[Recommendation]:
        pass


class IRanker(ABC):
    """Interface for ranking recommendations."""
    
    @abstractmethod
    def rank(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        pass
