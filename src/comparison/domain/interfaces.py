"""Comparison domain interfaces."""

from abc import ABC, abstractmethod

from src.comparison.domain.entities import ComparisonResult


class IComparisonEngine(ABC):
    """Interface for comparison engine."""
    
    @abstractmethod
    async def compare(self, assessment_a_id: str, assessment_b_id: str) -> ComparisonResult:
        pass
