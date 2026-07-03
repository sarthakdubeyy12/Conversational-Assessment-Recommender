"""Output validation logic."""

from src.guardrails.domain.entities import ValidationResult


class OutputValidator:
    """Validates agent outputs."""
    
    def validate(self, response: dict) -> ValidationResult:
        pass
