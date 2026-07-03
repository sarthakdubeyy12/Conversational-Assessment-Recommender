"""Retrieval-specific exceptions."""

from src.shared.exceptions.base import BaseAppException


class RetrievalError(BaseAppException):
    """Raised when retrieval fails."""
    
    def __init__(self, message: str = "Retrieval failed") -> None:
        super().__init__(message, status_code=500)


class EmbeddingError(BaseAppException):
    """Raised when embedding fails."""
    
    def __init__(self, message: str = "Embedding generation failed") -> None:
        super().__init__(message, status_code=500)
