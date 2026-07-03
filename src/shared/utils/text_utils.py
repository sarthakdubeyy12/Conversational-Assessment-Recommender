"""Text processing utilities."""

import re
from typing import List


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text."""
    pass
