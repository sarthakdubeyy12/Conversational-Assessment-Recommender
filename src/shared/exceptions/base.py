"""
Base exception for all application exceptions.

Provides consistent error handling with:
- Error messages
- Error codes
- HTTP status codes
- Additional context
"""

from typing import Any, Dict, Optional


class BaseAppException(Exception):
    """
    Base exception for all application exceptions.
    
    Provides:
    - Consistent error structure
    - HTTP status code mapping
    - Error code for client handling
    - Additional context/details
    
    All custom exceptions should inherit from this.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            status_code: HTTP status code
            details: Additional context/details
        """
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": {
                "message": self.message,
                "code": self.error_code,
                "details": self.details
            }
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.error_code}: {self.message}"
    
    def __repr__(self) -> str:
        """Representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"error_code={self.error_code!r}, "
            f"status_code={self.status_code})"
        )
