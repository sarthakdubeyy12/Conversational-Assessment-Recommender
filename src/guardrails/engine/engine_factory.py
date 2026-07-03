"""
Guardrails engine factory.

Creates configured engine instances.
"""

from typing import List
from src.guardrails.engine.guardrails_engine import GuardrailsEngine
from src.guardrails.detectors.prompt_injection_detector import PromptInjectionDetector
from src.guardrails.detectors.scope_detector import ScopeDetector
from src.guardrails.detectors.output_validator import OutputValidator
from src.guardrails.validation.catalog_validator import CatalogValidator
from src.guardrails.refusal.refusal_engine import RefusalEngine
from src.guardrails.risk.risk_classifier import RiskClassifier
from src.guardrails.audit.audit_logger import AuditLogger
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class GuardrailsEngineFactory:
    """
    Factory for guardrails engine.
    
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
        catalog_ids: List[str],
    ) -> GuardrailsEngine:
        """
        Create production guardrails engine.
        
        Args:
            catalog_ids: Valid assessment IDs from catalog
        
        Returns:
            Configured guardrails engine
        """
        logger.info("Creating production guardrails engine")
        
        # Create detectors
        injection_detector = PromptInjectionDetector()
        scope_detector = ScopeDetector()
        output_validator = OutputValidator()
        
        # Create validators
        catalog_validator = CatalogValidator(catalog_ids)
        
        # Create refusal and risk components
        refusal_engine = RefusalEngine()
        risk_classifier = RiskClassifier()
        
        # Create audit logger
        audit_logger = AuditLogger()
        
        # Assemble engine
        engine = GuardrailsEngine(
            prompt_injection_detector=injection_detector,
            scope_detector=scope_detector,
            output_validator=output_validator,
            catalog_validator=catalog_validator,
            refusal_engine=refusal_engine,
            risk_classifier=risk_classifier,
            audit_logger=audit_logger,
        )
        
        logger.info("Production guardrails engine created")
        return engine
