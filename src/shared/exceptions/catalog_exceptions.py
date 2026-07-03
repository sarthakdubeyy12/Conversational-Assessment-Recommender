"""
Catalog-specific exceptions.

Exceptions for catalog scraping, parsing, and validation failures.
"""

from typing import Optional, Dict, Any
from src.shared.exceptions.base import BaseAppException


class CatalogException(BaseAppException):
    """Base exception for catalog operations."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "CATALOG_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details or {}
        )


class CatalogNotFoundError(CatalogException):
    """Raised when catalog file is not found."""
    
    def __init__(self, path: str) -> None:
        super().__init__(
            message=f"Catalog not found at: {path}",
            error_code="CATALOG_NOT_FOUND",
            status_code=404,
            details={"path": path}
        )


class ScrapingException(CatalogException):
    """Raised when web scraping fails."""
    
    def __init__(self, url: str, reason: str) -> None:
        super().__init__(
            message=f"Failed to scrape {url}: {reason}",
            error_code="SCRAPING_ERROR",
            status_code=500,
            details={"url": url, "reason": reason}
        )


class ParsingException(CatalogException):
    """Raised when HTML parsing fails."""
    
    def __init__(self, url: str, reason: str) -> None:
        super().__init__(
            message=f"Failed to parse {url}: {reason}",
            error_code="PARSING_ERROR",
            status_code=500,
            details={"url": url, "reason": reason}
        )


class ValidationException(CatalogException):
    """Raised when assessment validation fails."""
    
    def __init__(self, assessment_name: str, errors: list) -> None:
        super().__init__(
            message=f"Validation failed for '{assessment_name}'",
            error_code="VALIDATION_ERROR",
            status_code=400,
            details={"assessment": assessment_name, "errors": errors}
        )


class DuplicateAssessmentException(CatalogException):
    """Raised when duplicate assessment is detected."""
    
    def __init__(self, assessment_id: str) -> None:
        super().__init__(
            message=f"Duplicate assessment detected: {assessment_id}",
            error_code="DUPLICATE_ASSESSMENT",
            status_code=400,
            details={"assessment_id": assessment_id}
        )
