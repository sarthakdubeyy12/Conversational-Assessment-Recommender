"""
Timing middleware utilities.

Provides timing functionality for middleware.
"""

import time
from typing import Callable, Awaitable, Any
from src.shared.logging.logger import get_logger
from src.shared.middleware.request_context import get_request_id

logger = get_logger(__name__)


async def time_request(
    call_next: Callable[[], Awaitable[Any]]
) -> Any:
    """
    Time request execution.
    
    Args:
        call_next: Next middleware/handler to call
    
    Returns:
        Response from next handler
    """
    request_id = get_request_id() or "unknown"
    start_time = time.perf_counter()
    
    try:
        response = await call_next()
        return response
    finally:
        duration = time.perf_counter() - start_time
        logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "duration_seconds": duration
            }
        )


def log_slow_requests(threshold_seconds: float = 1.0) -> Callable:
    """
    Log slow requests above threshold.
    
    Args:
        threshold_seconds: Threshold for slow requests
    
    Returns:
        Middleware function
    """
    async def middleware(call_next: Callable[[], Awaitable[Any]]) -> Any:
        request_id = get_request_id() or "unknown"
        start_time = time.perf_counter()
        
        try:
            response = await call_next()
            return response
        finally:
            duration = time.perf_counter() - start_time
            if duration > threshold_seconds:
                logger.warning(
                    f"Slow request detected",
                    extra={
                        "request_id": request_id,
                        "duration_seconds": duration,
                        "threshold_seconds": threshold_seconds
                    }
                )
    
    return middleware
