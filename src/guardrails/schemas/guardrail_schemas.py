"""Guardrails Pydantic schemas."""

from typing import List, Optional
from pydantic import BaseModel


class ValidationResultSchema(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None
    violations: List[str] = []


class SecurityCheckSchema(BaseModel):
    passed: bool
    check_type: str
    details: Optional[str] = None
