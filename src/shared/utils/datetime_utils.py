"""
Datetime utilities.

Provides consistent datetime handling across the application.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional


def utcnow() -> datetime:
    """Get current UTC datetime with timezone info."""
    return datetime.now(timezone.utc)


def to_iso_string(dt: datetime) -> str:
    """
    Convert datetime to ISO 8601 string.
    
    Args:
        dt: Datetime to convert
    
    Returns:
        ISO 8601 formatted string
    """
    return dt.isoformat()


def from_iso_string(iso_string: str) -> datetime:
    """
    Parse ISO 8601 string to datetime.
    
    Args:
        iso_string: ISO 8601 formatted string
    
    Returns:
        Parsed datetime
    """
    return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))


def seconds_ago(seconds: int) -> datetime:
    """
    Get datetime N seconds ago from now.
    
    Args:
        seconds: Number of seconds
    
    Returns:
        Datetime N seconds ago
    """
    return utcnow() - timedelta(seconds=seconds)


def seconds_from_now(seconds: int) -> datetime:
    """
    Get datetime N seconds from now.
    
    Args:
        seconds: Number of seconds
    
    Returns:
        Datetime N seconds from now
    """
    return utcnow() + timedelta(seconds=seconds)


def is_expired(expiry_time: datetime) -> bool:
    """
    Check if datetime has expired.
    
    Args:
        expiry_time: Expiry datetime
    
    Returns:
        True if expired, False otherwise
    """
    return utcnow() >= expiry_time


def format_timestamp(dt: Optional[datetime] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime as string.
    
    Args:
        dt: Datetime to format (defaults to now)
        fmt: Format string
    
    Returns:
        Formatted datetime string
    """
    if dt is None:
        dt = utcnow()
    return dt.strftime(fmt)
