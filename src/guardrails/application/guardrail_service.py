"""Guardrail service orchestration."""

from typing import Any

from src.guardrails.domain.entities import ValidationResult


class GuardrailService:
    """Orchestrates guardrail checks."""
    
    async def validate_input(self, user_message: str) -> ValidationResult:
        pass
    
    async def validate_output(self, response: dict) -> ValidationResult:
        pass
