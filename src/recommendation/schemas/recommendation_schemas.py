"""Recommendation Pydantic schemas."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class HiringCriteriaSchema(BaseModel):
    role: Optional[str] = None
    seniority_level: Optional[str] = None
    skills: List[str] = []
    test_types: List[str] = []
    language: Optional[str] = None
    duration: Optional[int] = None


class RecommendationSchema(BaseModel):
    assessment_id: str
    name: str
    url: str
    test_type: str
    score: float
    match_reasons: List[str]
    metadata: Dict[str, Any]
