"""
Request context management.

Provides context variables for tracking request-specific information.
"""

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

from src.shared.utils.uuid_utils import generate_request_id
from src.shared.utils.datetime_utils import utcnow


@dataclass
class RequestContext:
    """
    Request context information.
    
    Stores request-specific data that needs to be available
    throughout the request lifecycle.
    """
    
    request_id: str = field(default_factory=generate_request_id)
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    start_time: datetime = field(default_factory=utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def elapsed_seconds(self) -> float:
        """Get elapsed time since request start."""
        return (utcnow() - self.start_time).total_seconds()


# Context variable for request context
_request_context: ContextVar[Optional[RequestContext]] = ContextVar(
    "request_context",
    default=None
)


def get_request_context() -> Optional[RequestContext]:
    """
    Get current request context.
    
    Returns:
        Current request context or None
    """
    return _request_context.get()


def set_request_context(context: RequestContext) -> None:
    """
    Set request context.
    
    Args:
        context: Request context to set
    """
    _request_context.set(context)


def clear_request_context() -> None:
    """Clear request context."""
    _request_context.set(None)


def get_request_id() -> Optional[str]:
    """
    Get current request ID.
    
    Returns:
        Request ID or None
    """
    context = get_request_context()
    return context.request_id if context else None


def get_correlation_id() -> Optional[str]:
    """
    Get current correlation ID.
    
    Returns:
        Correlation ID or None
    """
    context = get_request_context()
    return context.correlation_id if context else None
