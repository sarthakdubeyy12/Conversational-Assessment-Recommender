"""Guardrails domain interfaces."""

from abc import ABC, abstractmethod
from typing import Any

from src.guardrails.domain.entities import ValidationResult


class IGuardrail(ABC):
    """Interface for guardrails."""
    
    @abstractmethod
    async def validate(self, data: Any) -> ValidationResult:
        pass


class IValidator(ABC):
    """Interface for validators."""
    
    @abstractmethod
    def is_valid(self, data: Any) -> bool:
        pass
