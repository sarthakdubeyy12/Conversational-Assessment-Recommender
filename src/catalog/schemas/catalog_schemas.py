"""Catalog Pydantic schemas."""

from typing import Optional
from pydantic import BaseModel, HttpUrl


class TestTypeSchema(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class CategorySchema(BaseModel):
    name: str
    description: Optional[str] = None


class AssessmentSchema(BaseModel):
    id: str
    name: str
    url: HttpUrl
    test_type: TestTypeSchema
    category: Optional[CategorySchema] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    language: Optional[str] = None
    level: Optional[str] = None
