"""
Health check endpoint.

Provides application health status.
"""

from fastapi import APIRouter

from src.shared.schemas.response_models import HealthResponse
from src.shared.utils.datetime_utils import utcnow, to_iso_string

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        Health status information
    """
    return HealthResponse(
        status="ok",
        version="1.0.0",
        timestamp=to_iso_string(utcnow()),
        details={}
    )
