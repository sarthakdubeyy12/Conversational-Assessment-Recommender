"""API-specific exceptions."""

from src.shared.exceptions.base import BaseAppException


class ValidationError(BaseAppException):
    """Raised when validation fails."""
    
    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, status_code=400)


class TimeoutError(BaseAppException):
    """Raised when request times out."""
    
    def __init__(self, message: str = "Request timeout") -> None:
        super().__init__(message, status_code=408)
