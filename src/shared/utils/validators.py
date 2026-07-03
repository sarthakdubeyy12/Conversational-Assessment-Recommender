"""
Shared validation utilities.

Provides reusable validation functions.
"""

import re
from typing import Any, Optional
from urllib.parse import urlparse


def is_valid_url(url: str, require_https: bool = False) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        require_https: Whether to require HTTPS
    
    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        is_valid = all([result.scheme, result.netloc])
        
        if require_https:
            is_valid = is_valid and result.scheme == "https"
        else:
            is_valid = is_valid and result.scheme in ["http", "https"]
        
        return is_valid
    except Exception:
        return False


def is_valid_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email to validate
    
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_string_length(text: str, min_length: int = 0, max_length: Optional[int] = None) -> bool:
    """
    Validate string length.
    
    Args:
        text: String to validate
        min_length: Minimum length
        max_length: Maximum length (None for no limit)
    
    Returns:
        True if valid, False otherwise
    """
    length = len(text)
    
    if length < min_length:
        return False
    
    if max_length is not None and length > max_length:
        return False
    
    return True


def is_valid_enum(value: Any, valid_values: list) -> bool:
    """
    Validate value is in enum.
    
    Args:
        value: Value to validate
        valid_values: List of valid values
    
    Returns:
        True if valid, False otherwise
    """
    return value in valid_values


def is_valid_integer_range(value: int, min_value: Optional[int] = None, max_value: Optional[int] = None) -> bool:
    """
    Validate integer is in range.
    
    Args:
        value: Integer to validate
        min_value: Minimum value (None for no limit)
        max_value: Maximum value (None for no limit)
    
    Returns:
        True if valid, False otherwise
    """
    if min_value is not None and value < min_value:
        return False
    
    if max_value is not None and value > max_value:
        return False
    
    return True


def is_valid_float_range(value: float, min_value: Optional[float] = None, max_value: Optional[float] = None) -> bool:
    """
    Validate float is in range.
    
    Args:
        value: Float to validate
        min_value: Minimum value (None for no limit)
        max_value: Maximum value (None for no limit)
    
    Returns:
        True if valid, False otherwise
    """
    if min_value is not None and value < min_value:
        return False
    
    if max_value is not None and value > max_value:
        return False
    
    return True


def is_non_empty_string(text: Any) -> bool:
    """
    Validate value is a non-empty string.
    
    Args:
        text: Value to validate
    
    Returns:
        True if valid, False otherwise
    """
    return isinstance(text, str) and len(text.strip()) > 0


def contains_only_alphanumeric(text: str, allow_spaces: bool = False) -> bool:
    """
    Validate string contains only alphanumeric characters.
    
    Args:
        text: String to validate
        allow_spaces: Whether to allow spaces
    
    Returns:
        True if valid, False otherwise
    """
    if allow_spaces:
        return all(c.isalnum() or c.isspace() for c in text)
    return text.isalnum()
