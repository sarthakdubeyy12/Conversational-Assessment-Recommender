"""Recommendation dependency injection."""

from src.recommendation.application.recommendation_service import RecommendationService


def get_recommendation_service() -> RecommendationService:
    """Factory for recommendation service."""
    pass
