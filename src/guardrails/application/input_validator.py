"""Input validation logic."""

from src.guardrails.domain.entities import ValidationResult


class InputValidator:
    """Validates user inputs."""
    
    def validate(self, user_message: str) -> ValidationResult:
        pass
