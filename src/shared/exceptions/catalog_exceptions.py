"""Catalog-specific exceptions."""

from src.shared.exceptions.base import BaseAppException


class CatalogNotFoundError(BaseAppException):
    """Raised when catalog is not found."""
    
    def __init__(self, message: str = "Catalog not found") -> None:
        super().__init__(message, status_code=404)


class CatalogParseError(BaseAppException):
    """Raised when catalog parsing fails."""
    
    def __init__(self, message: str = "Failed to parse catalog") -> None:
        super().__init__(message, status_code=500)
