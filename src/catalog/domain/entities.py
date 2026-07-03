"""Catalog domain entities."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TestType:
    """Test type value object."""
    
    code: str
    name: str
    description: Optional[str] = None


@dataclass(frozen=True)
class Category:
    """Assessment category value object."""
    
    name: str
    description: Optional[str] = None


@dataclass(frozen=True)
class Assessment:
    """Core assessment entity."""
    
    id: str
    name: str
    url: str
    test_type: TestType
    category: Optional[Category] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    language: Optional[str] = None
    level: Optional[str] = None
