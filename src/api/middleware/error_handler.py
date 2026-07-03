"""Global error handling."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def add_exception_handlers(app: FastAPI) -> None:
    """Add exception handlers to FastAPI app."""
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
