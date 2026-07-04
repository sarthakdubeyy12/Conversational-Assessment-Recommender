"""
Error handler middleware.

Provides centralized exception handling without exposing internals.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from src.api.models.error_response import ErrorResponse, ValidationErrorResponse, ErrorDetail
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


def add_exception_handlers(app: FastAPI) -> None:
    """
    Add exception handlers to FastAPI application.
    
    Handles all exceptions and returns user-friendly responses
    without exposing internal details.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """
        Handle request validation errors (422).
        
        Args:
            request: FastAPI request
            exc: Validation error
        
        Returns:
            JSON response with validation errors
        """
        logger.warning(f"Validation error: {exc.errors()}")
        
        # Convert Pydantic errors to our format
        details = [
            ErrorDetail(
                loc=list(err["loc"]),
                msg=err["msg"],
                type=err["type"],
            )
            for err in exc.errors()
        ]
        
        response = ValidationErrorResponse(
            error="Validation error",
            detail=details,
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response.model_dump(),
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request,
        exc: ValidationError,
    ) -> JSONResponse:
        """
        Handle Pydantic validation errors.
        
        Args:
            request: FastAPI request
            exc: Validation error
        
        Returns:
            JSON response with validation errors
        """
        logger.warning(f"Pydantic validation error: {exc.errors()}")
        
        details = [
            ErrorDetail(
                loc=list(err["loc"]),
                msg=err["msg"],
                type=err["type"],
            )
            for err in exc.errors()
        ]
        
        response = ValidationErrorResponse(
            error="Validation error",
            detail=details,
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response.model_dump(),
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """
        Handle all other exceptions.
        
        Never exposes stack traces or internal details.
        
        Args:
            request: FastAPI request
            exc: Exception
        
        Returns:
            JSON response with generic error
        """
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        response = ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred",
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response.model_dump(),
        )
