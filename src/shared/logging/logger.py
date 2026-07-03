"""
Logger setup and configuration.

Provides centralized logging with:
- Structured formatting
- Multiple handlers (console, file)
- Request ID support
- Module-based loggers
- Performance timing
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from contextvars import ContextVar

# Context variable for request ID tracking
request_id_ctx_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class RequestIDFilter(logging.Filter):
    """
    Adds request ID to log records.
    
    Uses context variables to track request ID across async operations.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx_var.get() or "N/A"
        return True


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = False
) -> logging.Logger:
    """
    Setup application logger with consistent configuration.
    
    Args:
        name: Logger name (usually module name)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for file logging
        json_format: Use JSON formatter instead of standard
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Add request ID filter
    request_filter = RequestIDFilter()
    logger.addFilter(request_filter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if json_format:
        from src.shared.logging.formatters import JSONFormatter
        console_formatter = JSONFormatter()
    else:
        console_formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(request_id)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        
        if json_format:
            from src.shared.logging.formatters import JSONFormatter
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(request_id)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance for module.
    
    Args:
        name: Logger name (use __name__ in calling module)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_request_id(request_id: str) -> None:
    """Set request ID in context for current request."""
    request_id_ctx_var.set(request_id)


def clear_request_id() -> None:
    """Clear request ID from context."""
    request_id_ctx_var.set(None)


def configure_root_logger(level: str = "INFO") -> None:
    """
    Configure root logger for application.
    
    Should be called once at application startup.
    """
    setup_logger("", level=level)
