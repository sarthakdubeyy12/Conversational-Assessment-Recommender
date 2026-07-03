"""
Standardized API response models.

Provides consistent response structure across all endpoints.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field


T = TypeVar("T")


class ErrorDetail(BaseModel):
    """
    Error detail structure.
    
    Provides structured error information for clients.
    """
    
    message: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Machine-readable error code")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Validation failed",
                "code": "VALIDATION_ERROR",
                "details": {"field": "email", "reason": "Invalid format"}
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response.
    
    Used for all error responses across the API.
    """
    
    error: ErrorDetail
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "message": "Resource not found",
                    "code": "NOT_FOUND",
                    "details": {}
                }
            }
        }


class SuccessResponse(BaseModel, Generic[T]):
    """
    Standard success response wrapper.
    
    Generic response type that wraps any successful result.
    """
    
    data: T
    message: Optional[str] = Field(None, description="Optional success message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": {"id": "123", "name": "Example"},
                "message": "Operation successful"
            }
        }


class HealthResponse(BaseModel):
    """
    Health check response.
    
    Standard response for health check endpoints.
    """
    
    status: str = Field(..., description="Health status")
    version: Optional[str] = Field(None, description="Application version")
    timestamp: Optional[str] = Field(None, description="Check timestamp")
    details: Dict[str, Any] = Field(default_factory=dict, description="Component health details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "version": "1.0.0",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {
                    "database": "healthy",
                    "cache": "healthy"
                }
            }
        }


class PaginationMeta(BaseModel):
    """
    Pagination metadata.
    
    Standard pagination information.
    """
    
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 10,
                "total_items": 100,
                "total_pages": 10,
                "has_next": True,
                "has_previous": False
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated response wrapper.
    
    Standard response for paginated endpoints.
    """
    
    data: List[T]
    pagination: PaginationMeta
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [{"id": "1"}, {"id": "2"}],
                "pagination": {
                    "page": 1,
                    "page_size": 10,
                    "total_items": 100,
                    "total_pages": 10,
                    "has_next": True,
                    "has_previous": False
                }
            }
        }


class MetadataResponse(BaseModel):
    """
    Response with metadata.
    
    For responses that need additional metadata.
    """
    
    data: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": {"result": "value"},
                "metadata": {
                    "source": "cache",
                    "cached_at": "2024-01-01T00:00:00Z"
                }
            }
        }
