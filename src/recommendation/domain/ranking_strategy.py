"""Ranking strategy patterns."""

from enum import Enum


class RankingStrategy(str, Enum):
    """Available ranking strategies."""
    
    SCORE_BASED = "score_based"
    RELEVANCE = "relevance"
    POPULARITY = "popularity"
    HYBRID = "hybrid"
