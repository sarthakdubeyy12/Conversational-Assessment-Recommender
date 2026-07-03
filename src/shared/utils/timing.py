"""
Performance timing utilities.

Provides timing decorators and context managers for performance measurement.
"""

import time
import functools
from contextlib import contextmanager
from typing import Generator, Callable, Any
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


@contextmanager
def timer(operation_name: str, log_result: bool = True) -> Generator[dict, None, None]:
    """
    Context manager for timing operations.
    
    Args:
        operation_name: Name of operation being timed
        log_result: Whether to log the result
    
    Yields:
        Dictionary with timing info (populated on exit)
    
    Example:
        >>> with timer("database_query") as t:
        ...     # do work
        ...     pass
        >>> print(t["duration"])
    """
    timing_info = {"operation": operation_name, "duration": 0.0}
    start_time = time.perf_counter()
    
    try:
        yield timing_info
    finally:
        duration = time.perf_counter() - start_time
        timing_info["duration"] = duration
        
        if log_result:
            logger.info(f"{operation_name} completed in {duration:.3f}s")


def timed_function(func: Callable) -> Callable:
    """
    Decorator to time function execution.
    
    Logs function name and execution time.
    
    Example:
        >>> @timed_function
        ... def slow_operation():
        ...     time.sleep(1)
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.perf_counter() - start_time
            logger.debug(f"{func.__name__} executed in {duration:.3f}s")
    
    return wrapper


async def timed_async_function(func: Callable) -> Callable:
    """
    Decorator to time async function execution.
    
    Logs function name and execution time.
    
    Example:
        >>> @timed_async_function
        ... async def slow_async_operation():
        ...     await asyncio.sleep(1)
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.perf_counter() - start_time
            logger.debug(f"{func.__name__} executed in {duration:.3f}s")
    
    return wrapper


class Stopwatch:
    """
    Stopwatch for manual timing control.
    
    Example:
        >>> sw = Stopwatch()
        >>> sw.start()
        >>> # do work
        >>> sw.stop()
        >>> print(sw.elapsed())
    """
    
    def __init__(self) -> None:
        self._start_time: float = 0.0
        self._end_time: float = 0.0
        self._running: bool = False
    
    def start(self) -> None:
        """Start the stopwatch."""
        self._start_time = time.perf_counter()
        self._running = True
    
    def stop(self) -> float:
        """
        Stop the stopwatch.
        
        Returns:
            Elapsed time in seconds
        """
        if not self._running:
            return 0.0
        
        self._end_time = time.perf_counter()
        self._running = False
        return self.elapsed()
    
    def elapsed(self) -> float:
        """
        Get elapsed time.
        
        Returns:
            Elapsed time in seconds
        """
        if self._running:
            return time.perf_counter() - self._start_time
        return self._end_time - self._start_time
    
    def reset(self) -> None:
        """Reset the stopwatch."""
        self._start_time = 0.0
        self._end_time = 0.0
        self._running = False
