"""Retrieval Pydantic schemas."""

from typing import Dict, Any, List
from pydantic import BaseModel


class SearchQuerySchema(BaseModel):
    text: str
    filters: Dict[str, Any] = {}
    top_k: int = 10


class RetrievalResultSchema(BaseModel):
    assessment_id: str
    score: float
    metadata: Dict[str, Any]


class RetrievalContextSchema(BaseModel):
    query: SearchQuerySchema
    results: List[RetrievalResultSchema]
    total_results: int
