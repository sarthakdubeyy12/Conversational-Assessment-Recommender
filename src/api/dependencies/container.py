"""
Dependency injection container.

Provides configured dependencies for FastAPI endpoints.
"""

from src.api.dependencies.orchestrator import get_orchestrator

__all__ = ["get_orchestrator"]


class DependencyContainer:
    """Centralized dependency container."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
