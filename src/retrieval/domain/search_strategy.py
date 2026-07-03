"""Search strategy patterns."""

from enum import Enum


class SearchStrategy(str, Enum):
    """Available search strategies."""
    
    SEMANTIC = "semantic"
    METADATA = "metadata"
    HYBRID = "hybrid"
