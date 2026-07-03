"""
Global error handling.

Provides centralized exception handling for FastAPI.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.shared.exceptions.base import BaseAppException
from src.shared.schemas.response_models import ErrorResponse, ErrorDetail
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


def add_exception_handlers(app: FastAPI) -> None:
    """
    Add exception handlers to FastAPI app.
    
    Handles:
    - Custom application exceptions
    - Validation errors
    - Generic exceptions
    
    Args:
        app: FastAPI application
    """
    
    @app.exception_handler(BaseAppException)
    async def base_app_exception_handler(
        request: Request,
        exc: BaseAppException
    ) -> JSONResponse:
        """Handle custom application exceptions."""
        logger.error(
            f"Application error: {exc.error_code}",
            extra={
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "path": request.url.path,
            }
        )
        
        error_response = ErrorResponse(
            error=ErrorDetail(
                message=exc.message,
                code=exc.error_code,
                details=exc.details
            )
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump()
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(
        request: Request,
        exc: ValueError
    ) -> JSONResponse:
        """Handle ValueError as validation error."""
        logger.error(
            f"ValueError: {str(exc)}",
            extra={"path": request.url.path}
        )
        
        error_response = ErrorResponse(
            error=ErrorDetail(
                message=str(exc),
                code="VALIDATION_ERROR",
                details={}
            )
        )
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response.model_dump()
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """Handle all other exceptions."""
        logger.error(
            f"Unhandled exception: {type(exc).__name__}",
            exc_info=True,
            extra={"path": request.url.path}
        )
        
        error_response = ErrorResponse(
            error=ErrorDetail(
                message="Internal server error",
                code="INTERNAL_ERROR",
                details={}
            )
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump()
        )
