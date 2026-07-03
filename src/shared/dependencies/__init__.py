"""Dependency injection infrastructure."""

from src.shared.dependencies.container import DependencyContainer, get_container

__all__ = [
    "DependencyContainer",
    "get_container",
]
