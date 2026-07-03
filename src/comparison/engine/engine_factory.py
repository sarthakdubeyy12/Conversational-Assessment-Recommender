"""
Comparison engine factory.

Creates configured engine instances.
"""

from src.comparison.engine.comparison_engine import ComparisonEngine
from src.comparison.resolver.assessment_resolver import AssessmentResolver
from src.comparison.comparator.field_comparator import FieldComparator
from src.comparison.comparator.similarity_detector import SimilarityDetector
from src.comparison.comparator.difference_detector import DifferenceDetector
from src.comparison.confidence.confidence_calculator import ConfidenceCalculator
from src.comparison.formatting.context_builder import ComparisonContextBuilder
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ComparisonEngineFactory:
    """
    Factory for comparison engine.
    
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
    def create_production_engine() -> ComparisonEngine:
        """
        Create production comparison engine.
        
        Returns:
            Configured comparison engine
        """
        logger.info("Creating production comparison engine")
        
        # Create components
        resolver = AssessmentResolver()
        field_comparator = FieldComparator()
        similarity_detector = SimilarityDetector()
        difference_detector = DifferenceDetector()
        confidence_calculator = ConfidenceCalculator()
        context_builder = ComparisonContextBuilder()
        
        # Assemble engine
        engine = ComparisonEngine(
            resolver=resolver,
            field_comparator=field_comparator,
            similarity_detector=similarity_detector,
            difference_detector=difference_detector,
            confidence_calculator=confidence_calculator,
            context_builder=context_builder,
        )
        
        logger.info("Production comparison engine created")
        return engine
