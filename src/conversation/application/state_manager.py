"""Conversation state management."""

from typing import List

from src.conversation.domain.entities import Message, ConversationState


class StateManager:
    """Reconstructs conversation state from messages."""
    
    def reconstruct_state(self, messages: List[Message]) -> ConversationState:
        pass
