"""
FastAPI application factory.

Creates and configures the FastAPI application with middleware and routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import health, chat
from src.api.middleware.error_handler import add_exception_handlers
from src.api.middleware.logging_middleware import LoggingMiddleware
from src.shared.config.settings import get_settings
from src.shared.logging.logger import get_logger
from src.shared.lifecycle import LifecycleManager

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    settings = get_settings()
    lifecycle = LifecycleManager.get_instance()
    
    app = FastAPI(
        title="SHL Assessment Recommender",
        description="Conversational AI for SHL assessment recommendations",
        version="1.0.0",
        debug=settings.debug,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Logging middleware - temporarily disabled due to format issue
    # app.add_middleware(LoggingMiddleware)
    
    # Exception handlers
    add_exception_handlers(app)
    
    # Lifecycle events
    @app.on_event("startup")
    async def startup_event():
        """Execute startup hooks."""
        logger.info("FastAPI startup event triggered")
        await lifecycle.startup()
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Execute shutdown hooks."""
        logger.info("FastAPI shutdown event triggered")
        await lifecycle.shutdown()
    
    # Include routers
    app.include_router(health.router, tags=["health"])
    app.include_router(chat.router, tags=["chat"])
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint - API information."""
        return {
            "service": "SHL Assessment Recommender",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "health": "/health",
                "chat": "/chat",
                "docs": "/docs",
                "openapi": "/openapi.json"
            }
        }
    
    logger.info("FastAPI application created successfully")
    
    return app
