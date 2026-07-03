"""Workflow routing logic."""

from src.conversation.domain.entities import ConversationState


class WorkflowRouter:
    """Routes conversation to appropriate feature."""
    
    def route(self, state: ConversationState) -> str:
        pass
