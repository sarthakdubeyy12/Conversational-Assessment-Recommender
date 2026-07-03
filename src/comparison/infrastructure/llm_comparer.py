"""LLM-based comparison."""

from src.comparison.domain.entities import ComparisonResult
from src.comparison.domain.interfaces import IComparisonEngine


class LLMComparisonEngine(IComparisonEngine):
    """LLM-based assessment comparison."""
    
    async def compare(self, assessment_a_id: str, assessment_b_id: str) -> ComparisonResult:
        pass
