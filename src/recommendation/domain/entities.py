"""Recommendation domain entities."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass(frozen=True)
class HiringCriteria:
    """Extracted hiring criteria."""
    
    role: Optional[str] = None
    seniority_level: Optional[str] = None
    skills: List[str] = None
    test_types: List[str] = None
    language: Optional[str] = None
    duration: Optional[int] = None


@dataclass(frozen=True)
class Recommendation:
    """Single recommendation result."""
    
    assessment_id: str
    name: str
    url: str
    test_type: str
    score: float
    match_reasons: List[str]
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class RecommendationResult:
    """Final recommendation result."""
    
    recommendations: List[Recommendation]
    criteria: HiringCriteria
    total_matches: int
