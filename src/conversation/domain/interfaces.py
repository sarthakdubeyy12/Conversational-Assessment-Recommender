"""Conversation domain interfaces."""

from abc import ABC, abstractmethod
from typing import List

from src.conversation.domain.entities import Message, ConversationState


class IConversationOrchestrator(ABC):
    """Interface for conversation orchestration."""
    
    @abstractmethod
    async def process_conversation(self, messages: List[Message]) -> dict:
        pass


class IIntentDetector(ABC):
    """Interface for intent detection."""
    
    @abstractmethod
    async def detect_intent(self, state: ConversationState) -> str:
        pass


class ILLMClient(ABC):
    """Interface for LLM providers."""
    
    @abstractmethod
    async def generate(self, messages: List[dict], system_prompt: str) -> str:
        pass
