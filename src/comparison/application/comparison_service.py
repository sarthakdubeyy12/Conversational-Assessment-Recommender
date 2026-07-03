"""Comparison service orchestration."""

from src.comparison.domain.entities import ComparisonResult
from src.comparison.domain.interfaces import IComparisonEngine


class ComparisonService:
    """Orchestrates comparison operations."""
    
    def __init__(self, engine: IComparisonEngine) -> None:
        self._engine = engine
    
    async def compare_assessments(self, assessment_a_id: str, assessment_b_id: str) -> ComparisonResult:
        return await self._engine.compare(assessment_a_id, assessment_b_id)
