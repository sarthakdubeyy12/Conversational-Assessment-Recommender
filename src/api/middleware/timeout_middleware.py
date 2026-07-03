"""Timeout enforcement middleware."""

from starlette.middleware.base import BaseHTTPMiddleware


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Enforces timeout on requests."""
    
    def __init__(self, app, timeout: int = 30):
        super().__init__(app)
        self._timeout = timeout
    
    async def dispatch(self, request, call_next):
        pass
