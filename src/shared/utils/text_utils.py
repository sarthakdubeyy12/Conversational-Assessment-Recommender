"""
Text processing utilities.

Provides text cleaning, validation, and manipulation.
"""

import re
from typing import List, Optional


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    - Removes extra whitespace
    - Normalizes line breaks
    - Strips leading/trailing whitespace
    
    Args:
        text: Text to clean
    
    Returns:
        Cleaned text
    """
    # Normalize line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to max length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract keywords from text.
    
    Extracts words that are at least min_length characters.
    
    Args:
        text: Text to extract from
        min_length: Minimum word length
    
    Returns:
        List of keywords
    """
    # Remove punctuation and split
    words = re.findall(r'\b\w+\b', text.lower())
    # Filter by length and deduplicate
    return list(set(word for word in words if len(word) >= min_length))


def sanitize_string(text: str) -> str:
    """
    Sanitize string for safe usage.
    
    Removes potentially dangerous characters.
    
    Args:
        text: Text to sanitize
    
    Returns:
        Sanitized text
    """
    # Remove non-printable characters
    text = ''.join(char for char in text if char.isprintable())
    return text.strip()


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    
    Args:
        text: Text to normalize
    
    Returns:
        Text with normalized whitespace
    """
    return ' '.join(text.split())


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text.
    
    Args:
        text: Text to extract URLs from
    
    Returns:
        List of URLs
    """
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)


def remove_urls(text: str, replacement: str = "") -> str:
    """
    Remove URLs from text.
    
    Args:
        text: Text to remove URLs from
        replacement: Replacement string
    
    Returns:
        Text without URLs
    """
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.sub(url_pattern, replacement, text)


def word_count(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Text to count words in
    
    Returns:
        Word count
    """
    return len(text.split())


def contains_any(text: str, substrings: List[str], case_sensitive: bool = False) -> bool:
    """
    Check if text contains any of the substrings.
    
    Args:
        text: Text to check
        substrings: List of substrings to look for
        case_sensitive: Whether to match case
    
    Returns:
        True if any substring found, False otherwise
    """
    if not case_sensitive:
        text = text.lower()
        substrings = [s.lower() for s in substrings]
    
    return any(substring in text for substring in substrings)
