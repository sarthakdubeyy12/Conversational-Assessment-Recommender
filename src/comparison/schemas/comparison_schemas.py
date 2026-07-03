"""Comparison Pydantic schemas."""

from typing import List, Any
from pydantic import BaseModel


class DifferenceSchema(BaseModel):
    attribute: str
    assessment_a_value: Any
    assessment_b_value: Any
    significance: str


class ComparisonResultSchema(BaseModel):
    assessment_a_id: str
    assessment_b_id: str
    differences: List[DifferenceSchema]
    similarities: List[str]
    summary: str
