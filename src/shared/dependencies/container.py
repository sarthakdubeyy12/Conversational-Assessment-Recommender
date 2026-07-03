"""
Dependency injection container.

Provides centralized dependency management and resolution.
"""

from typing import Any, Callable, Dict, TypeVar, Optional, Type
from functools import lru_cache

T = TypeVar("T")


class DependencyContainer:
    """
    Dependency injection container.
    
    Manages service registration and resolution.
    Supports:
    - Singleton services
    - Factory functions
    - Lazy initialization
    - Type-based resolution
    """
    
    def __init__(self) -> None:
        self._singletons: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}
        self._instances: Dict[Type, Any] = {}
    
    def register_singleton(self, interface: Type[T], instance: T) -> None:
        """
        Register singleton instance.
        
        Args:
            interface: Interface type
            instance: Singleton instance
        """
        self._singletons[interface] = instance
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """
        Register factory function.
        
        Args:
            interface: Interface type
            factory: Factory function to create instances
        """
        self._factories[interface] = factory
    
    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve dependency.
        
        Resolution order:
        1. Check cached instances
        2. Check singletons
        3. Call factory
        
        Args:
            interface: Interface type to resolve
        
        Returns:
            Instance of requested type
        
        Raises:
            ValueError: If dependency cannot be resolved
        """
        # Check cached instances
        if interface in self._instances:
            return self._instances[interface]
        
        # Check singletons
        if interface in self._singletons:
            instance = self._singletons[interface]
            self._instances[interface] = instance
            return instance
        
        # Check factories
        if interface in self._factories:
            factory = self._factories[interface]
            instance = factory()
            self._instances[interface] = instance
            return instance
        
        raise ValueError(f"Cannot resolve dependency: {interface}")
    
    def has(self, interface: Type) -> bool:
        """
        Check if dependency is registered.
        
        Args:
            interface: Interface type
        
        Returns:
            True if registered, False otherwise
        """
        return (
            interface in self._singletons or
            interface in self._factories or
            interface in self._instances
        )
    
    def clear(self) -> None:
        """Clear all registrations (useful for testing)."""
        self._singletons.clear()
        self._factories.clear()
        self._instances.clear()
    
    def clear_instances(self) -> None:
        """Clear cached instances (keeps registrations)."""
        self._instances.clear()


# Global container instance
_container: Optional[DependencyContainer] = None


@lru_cache
def get_container() -> DependencyContainer:
    """
    Get global dependency container.
    
    Returns:
        Singleton container instance
    """
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container


def reset_container() -> None:
    """Reset global container (for testing)."""
    global _container
    _container = None
    get_container.cache_clear()
