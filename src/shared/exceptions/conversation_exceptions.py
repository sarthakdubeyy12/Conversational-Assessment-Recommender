"""
Conversation exceptions.

Domain-specific exceptions for conversation operations.
"""

from src.shared.exceptions.base import BaseApplicationException


class ConversationException(BaseApplicationException):
    """Base conversation exception."""
    pass


class StateReconstructionException(ConversationException):
    """State reconstruction failed."""
    pass


class InvalidMessageException(ConversationException):
    """Invalid message format."""
    pass


class ValidationException(ConversationException):
    """State validation failed."""
    pass
