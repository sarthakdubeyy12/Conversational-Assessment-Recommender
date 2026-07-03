"""
UUID utilities.

Provides UUID generation and validation.
"""

import uuid
from typing import Optional


def generate_uuid() -> str:
    """
    Generate a new UUID v4.
    
    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def is_valid_uuid(uuid_string: str, version: int = 4) -> bool:
    """
    Validate UUID string.
    
    Args:
        uuid_string: UUID string to validate
        version: UUID version to check (1, 3, 4, or 5)
    
    Returns:
        True if valid, False otherwise
    """
    try:
        uuid_obj = uuid.UUID(uuid_string, version=version)
        return str(uuid_obj) == uuid_string
    except (ValueError, AttributeError):
        return False


def generate_request_id() -> str:
    """
    Generate a request ID for tracking.
    
    Returns:
        Request ID string
    """
    return f"req_{generate_uuid()}"


def generate_correlation_id() -> str:
    """
    Generate a correlation ID for distributed tracing.
    
    Returns:
        Correlation ID string
    """
    return f"corr_{generate_uuid()}"


def to_uuid(uuid_string: str) -> Optional[uuid.UUID]:
    """
    Convert string to UUID object.
    
    Args:
        uuid_string: UUID string
    
    Returns:
        UUID object or None if invalid
    """
    try:
        return uuid.UUID(uuid_string)
    except (ValueError, AttributeError):
        return None
