"""Main conversation orchestrator."""

from typing import List

from src.conversation.domain.entities import Message
from src.conversation.domain.interfaces import IConversationOrchestrator


class ConversationOrchestrator(IConversationOrchestrator):
    """Orchestrates conversation flow."""
    
    async def process_conversation(self, messages: List[Message]) -> dict:
        pass
