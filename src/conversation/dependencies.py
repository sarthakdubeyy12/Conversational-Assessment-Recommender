"""Conversation dependency injection."""

from src.conversation.application.orchestrator import ConversationOrchestrator
from src.shared.config.settings import Settings


def get_conversation_orchestrator() -> ConversationOrchestrator:
    """Factory for conversation orchestrator."""
    settings = Settings()
    return ConversationOrchestrator()
