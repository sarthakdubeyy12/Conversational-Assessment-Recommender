"""Intent type definitions."""

from enum import Enum


class IntentType(str, Enum):
    """User intent types."""
    
    INITIAL_REQUEST = "initial_request"
    CLARIFICATION = "clarification"
    REFINEMENT = "refinement"
    COMPARISON = "comparison"
    OFF_TOPIC = "off_topic"
    END_CONVERSATION = "end_conversation"
