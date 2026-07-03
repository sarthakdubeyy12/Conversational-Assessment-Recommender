"""Comparison domain entities."""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass(frozen=True)
class Difference:
    """Single difference between assessments."""
    
    attribute: str
    assessment_a_value: Any
    assessment_b_value: Any
    significance: str


@dataclass(frozen=True)
class ComparisonResult:
    """Comparison result entity."""
    
    assessment_a_id: str
    assessment_b_id: str
    differences: List[Difference]
    similarities: List[str]
    summary: str
