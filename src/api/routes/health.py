"""
Health check endpoint.
"""

from fastapi import APIRouter, status
from src.api.models.health_response import HealthResponse
from src.shared.config.settings import get_settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns service health status and metadata.
    
    Returns:
        Health response with status and version
    """
    settings = get_settings()
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=settings.environment,
    )
