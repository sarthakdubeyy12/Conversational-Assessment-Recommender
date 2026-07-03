"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import health, chat
from src.api.middleware.error_handler import add_exception_handlers
from src.api.middleware.logging_middleware import LoggingMiddleware
from src.shared.config.settings import Settings


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = Settings()
    
    app = FastAPI(
        title="SHL Assessment Recommender",
        description="Conversational AI for SHL assessment recommendations",
        version="1.0.0",
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(LoggingMiddleware)
    
    add_exception_handlers(app)
    
    app.include_router(health.router)
    app.include_router(chat.router)
    
    return app
