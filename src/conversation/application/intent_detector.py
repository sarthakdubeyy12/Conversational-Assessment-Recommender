"""Intent detection logic."""

from src.conversation.domain.entities import ConversationState
from src.conversation.domain.interfaces import IIntentDetector


class IntentDetector(IIntentDetector):
    """Detects user intent from conversation."""
    
    async def detect_intent(self, state: ConversationState) -> str:
        pass
