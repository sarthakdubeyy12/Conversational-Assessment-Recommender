"""Catalog value objects."""

from dataclasses import dataclass
from enum import Enum


class TestTypeEnum(str, Enum):
    """Standard SHL test types."""
    
    KNOWLEDGE = "K"
    ABILITY = "A"
    PERSONALITY = "P"
    SITUATIONAL = "S"
    COMPETENCY = "C"


@dataclass(frozen=True)
class URL:
    """URL value object with validation."""
    
    value: str
    
    def __post_init__(self) -> None:
        if not self.value.startswith("https://www.shl.com/"):
            raise ValueError(f"Invalid SHL URL: {self.value}")
