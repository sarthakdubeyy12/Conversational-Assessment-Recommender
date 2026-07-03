"""
Application lifecycle management.

Manages startup and shutdown of application components.
"""

from typing import Callable, List, Awaitable
from dataclasses import dataclass, field
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class LifecycleHook:
    """
    Lifecycle hook definition.
    
    Represents a callback to execute during lifecycle events.
    """
    
    name: str
    callback: Callable[[], Awaitable[None]]
    priority: int = 0  # Lower numbers execute first


class ApplicationLifecycle:
    """
    Application lifecycle manager.
    
    Manages startup and shutdown hooks for application components.
    Components can register callbacks for initialization and cleanup.
    """
    
    def __init__(self) -> None:
        self._startup_hooks: List[LifecycleHook] = []
        self._shutdown_hooks: List[LifecycleHook] = []
        self._is_started: bool = False
    
    def on_startup(
        self,
        name: str,
        priority: int = 0
    ) -> Callable[[Callable[[], Awaitable[None]]], Callable[[], Awaitable[None]]]:
        """
        Decorator to register startup hook.
        
        Args:
            name: Hook name for logging
            priority: Execution priority (lower executes first)
        
        Example:
            >>> lifecycle = ApplicationLifecycle()
            >>> @lifecycle.on_startup("database", priority=1)
            ... async def init_database():
            ...     # Initialize database
            ...     pass
        """
        def decorator(func: Callable[[], Awaitable[None]]) -> Callable[[], Awaitable[None]]:
            hook = LifecycleHook(name=name, callback=func, priority=priority)
            self._startup_hooks.append(hook)
            return func
        return decorator
    
    def on_shutdown(
        self,
        name: str,
        priority: int = 0
    ) -> Callable[[Callable[[], Awaitable[None]]], Callable[[], Awaitable[None]]]:
        """
        Decorator to register shutdown hook.
        
        Args:
            name: Hook name for logging
            priority: Execution priority (lower executes first)
        
        Example:
            >>> lifecycle = ApplicationLifecycle()
            >>> @lifecycle.on_shutdown("database", priority=1)
            ... async def close_database():
            ...     # Close database connections
            ...     pass
        """
        def decorator(func: Callable[[], Awaitable[None]]) -> Callable[[], Awaitable[None]]:
            hook = LifecycleHook(name=name, callback=func, priority=priority)
            self._shutdown_hooks.append(hook)
            return func
        return decorator
    
    def register_startup(self, name: str, callback: Callable[[], Awaitable[None]], priority: int = 0) -> None:
        """Register startup hook programmatically."""
        hook = LifecycleHook(name=name, callback=callback, priority=priority)
        self._startup_hooks.append(hook)
    
    def register_shutdown(self, name: str, callback: Callable[[], Awaitable[None]], priority: int = 0) -> None:
        """Register shutdown hook programmatically."""
        hook = LifecycleHook(name=name, callback=callback, priority=priority)
        self._shutdown_hooks.append(hook)
    
    async def startup(self) -> None:
        """
        Execute all startup hooks.
        
        Hooks are executed in priority order (lowest first).
        """
        if self._is_started:
            logger.warning("Application already started")
            return
        
        logger.info("Starting application...")
        
        # Sort by priority
        sorted_hooks = sorted(self._startup_hooks, key=lambda h: h.priority)
        
        for hook in sorted_hooks:
            try:
                logger.info(f"Executing startup hook: {hook.name}")
                await hook.callback()
                logger.info(f"Completed startup hook: {hook.name}")
            except Exception as e:
                logger.error(f"Failed startup hook {hook.name}: {e}", exc_info=True)
                raise
        
        self._is_started = True
        logger.info("Application started successfully")
    
    async def shutdown(self) -> None:
        """
        Execute all shutdown hooks.
        
        Hooks are executed in priority order (lowest first).
        Continues executing even if individual hooks fail.
        """
        if not self._is_started:
            logger.warning("Application not started")
            return
        
        logger.info("Shutting down application...")
        
        # Sort by priority
        sorted_hooks = sorted(self._shutdown_hooks, key=lambda h: h.priority)
        
        for hook in sorted_hooks:
            try:
                logger.info(f"Executing shutdown hook: {hook.name}")
                await hook.callback()
                logger.info(f"Completed shutdown hook: {hook.name}")
            except Exception as e:
                # Log but continue with other hooks
                logger.error(f"Failed shutdown hook {hook.name}: {e}", exc_info=True)
        
        self._is_started = False
        logger.info("Application shut down successfully")
    
    @property
    def is_started(self) -> bool:
        """Check if application is started."""
        return self._is_started


class LifecycleManager:
    """
    Singleton lifecycle manager.
    
    Provides global access to lifecycle management.
    """
    
    _instance: ApplicationLifecycle = None
    
    @classmethod
    def get_instance(cls) -> ApplicationLifecycle:
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = ApplicationLifecycle()
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset instance (for testing)."""
        cls._instance = None
