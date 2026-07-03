"""
Recommendation engine factory.

Creates configured engine instances.
"""

from src.recommendation.engine.recommendation_engine import RecommendationEngine
from src.recommendation.selection.candidate_selector import CandidateSelector
from src.recommendation.ranking.recommendation_ranker import RecommendationRanker
from src.recommendation.validation.recommendation_validator import RecommendationValidator
from src.recommendation.explanation.explanation_builder import ExplanationBuilder
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class RecommendationEngineFactory:
    """
    Factory for recommendation engine.
    
    Responsibilities:
    - Wire up engine dependencies
    - Configure components
    - Provide production instances
    
    Design:
    - Dependency injection
    - Configuration management
    - Single point of creation
    """
    
    @staticmethod
    def create_production_engine(
        min_similarity: float = 0.0,
        max_recommendations: int = 10,
    ) -> RecommendationEngine:
        """
        Create production recommendation engine.
        
        Args:
            min_similarity: Minimum similarity threshold
            max_recommendations: Maximum recommendations
        
        Returns:
            Configured recommendation engine
        """
        logger.info("Creating production recommendation engine")
        
        # Create components
        selector = CandidateSelector(
            min_similarity=min_similarity,
            require_url=True,
            require_category=False,
        )
        
        ranker = RecommendationRanker(
            category_boost=0.1,
            diversity_weight=0.05,
            max_recommendations=max_recommendations,
        )
        
        validator = RecommendationValidator()
        
        explainer = ExplanationBuilder()
        
        # Assemble engine
        engine = RecommendationEngine(
            selector=selector,
            ranker=ranker,
            validator=validator,
            explainer=explainer,
        )
        
        logger.info("Production recommendation engine created")
        return engine
