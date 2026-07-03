"""Conversation domain entities."""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass(frozen=True)
class Message:
    """Single conversation message."""
    
    role: str
    content: str
    timestamp: Optional[datetime] = None


@dataclass
class ConversationState:
    """Reconstructed conversation state."""
    
    messages: List[Message]
    extracted_criteria: Dict[str, Any]
    intent: Optional[str] = None
    needs_clarification: bool = True
    has_recommendations: bool = False


@dataclass(frozen=True)
class Turn:
    """Single conversation turn."""
    
    user_message: Message
    assistant_message: Optional[Message] = None
