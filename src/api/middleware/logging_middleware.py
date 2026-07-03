"""
Request/response logging middleware.

Logs all HTTP requests and responses with timing information.
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.shared.logging.logger import get_logger, set_request_id, clear_request_id
from src.shared.utils.uuid_utils import generate_request_id
from src.shared.middleware.request_context import (
    RequestContext,
    set_request_context,
    clear_request_context,
)
from src.shared.constants.api_constants import HEADER_REQUEST_ID

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs HTTP requests and responses.
    
    Features:
    - Request ID generation and tracking
    - Request timing
    - Request/response logging
    - Context management
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and log details.
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler
        
        Returns:
            HTTP response
        """
        # Generate or extract request ID
        request_id = request.headers.get(HEADER_REQUEST_ID, generate_request_id())
        
        # Set request ID in logging context
        set_request_id(request_id)
        
        # Create request context
        context = RequestContext(request_id=request_id)
        set_request_context(context)
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
            }
        )
        
        start_time = time.perf_counter()
        
        try:
            # Process request
            response: Response = await call_next(request)
            
            # Calculate duration
            duration = time.perf_counter() - start_time
            
            # Add request ID to response headers
            response.headers[HEADER_REQUEST_ID] = request_id
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_seconds": duration,
                }
            )
            
            return response
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                exc_info=True,
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_seconds": duration,
                    "error": str(e),
                }
            )
            raise
            
        finally:
            # Clean up context
            clear_request_id()
            clear_request_context()
