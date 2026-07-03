"""Guardrails dependency injection."""

from src.guardrails.application.guardrail_service import GuardrailService


def get_guardrail_service() -> GuardrailService:
    """Factory for guardrail service."""
    return GuardrailService()
