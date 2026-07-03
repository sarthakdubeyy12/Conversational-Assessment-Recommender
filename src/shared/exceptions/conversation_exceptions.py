"""Conversation-specific exceptions."""

from src.shared.exceptions.base import BaseAppException


class ConversationError(BaseAppException):
    """Raised when conversation processing fails."""
    
    def __init__(self, message: str = "Conversation processing failed") -> None:
        super().__init__(message, status_code=500)


class LLMError(BaseAppException):
    """Raised when LLM call fails."""
    
    def __init__(self, message: str = "LLM generation failed") -> None:
        super().__init__(message, status_code=500)
