"""
Error response models.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Single error detail."""
    
    loc: List[str] = Field(description="Error location")
    msg: str = Field(description="Error message")
    type: str = Field(description="Error type")


class ErrorResponse(BaseModel):
    """
    Standard error response.
    
    Returns user-friendly error information without exposing internals.
    """
    
    error: str = Field(description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional detail")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "error": "Invalid request",
                "detail": "Message content cannot be empty"
            }
        }


class ValidationErrorResponse(BaseModel):
    """
    Validation error response.
    
    Returned for 422 validation errors.
    """
    
    error: str = Field(default="Validation error", description="Error type")
    detail: List[ErrorDetail] = Field(description="Validation errors")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "error": "Validation error",
                "detail": [
                    {
                        "loc": ["body", "messages"],
                        "msg": "At least one message is required",
                        "type": "value_error"
                    }
                ]
            }
        }
