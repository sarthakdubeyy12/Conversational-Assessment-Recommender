"""
Health check response model.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """
    Health check response.
    
    Returns service health status and metadata.
    """
    
    status: str = Field(description="Service status (healthy/unhealthy)")
    version: str = Field(default="1.0.0", description="API version")
    environment: str = Field(description="Environment name")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "environment": "production"
            }
        }
