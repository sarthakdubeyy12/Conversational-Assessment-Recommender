"""Clarification logic."""

from src.conversation.domain.entities import ConversationState


class ClarificationEngine:
    """Determines when to ask clarifying questions."""
    
    def needs_clarification(self, state: ConversationState) -> bool:
        pass
    
    def generate_clarification_question(self, state: ConversationState) -> str:
        pass
