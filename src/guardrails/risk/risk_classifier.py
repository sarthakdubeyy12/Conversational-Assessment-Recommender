"""
Risk classifier.

Classifies violation severity and determines appropriate response.
"""

from src.guardrails.domain.violation_type import ViolationType
from src.guardrails.domain.risk_level import RiskLevel
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class RiskClassifier:
    """
    Classify risk levels for violations.
    
    Responsibilities:
    - Map violations to risk levels
    - Determine blocking decisions
    - Assign severity scores
    
    Design:
    - Deterministic classification
    - Clear severity hierarchy
    - Actionable decisions
    """
    
    def __init__(self) -> None:
        """Initialize classifier with risk mappings."""
        # Map violations to risk levels
        self._violation_risk_map = {
            # Critical security threats
            ViolationType.PROMPT_INJECTION: RiskLevel.CRITICAL,
            ViolationType.JAILBREAK: RiskLevel.CRITICAL,
            ViolationType.SYSTEM_PROMPT_LEAK: RiskLevel.CRITICAL,
            ViolationType.TOOL_MANIPULATION: RiskLevel.CRITICAL,
            ViolationType.INSTRUCTION_OVERRIDE: RiskLevel.HIGH,
            
            # Scope violations
            ViolationType.OUT_OF_SCOPE: RiskLevel.MEDIUM,
            ViolationType.OFF_TOPIC: RiskLevel.LOW,
            ViolationType.UNSUPPORTED_REQUEST: RiskLevel.MEDIUM,
            
            # Output validation failures
            ViolationType.HALLUCINATION: RiskLevel.HIGH,
            ViolationType.FABRICATED_URL: RiskLevel.HIGH,
            ViolationType.FABRICATED_ASSESSMENT: RiskLevel.HIGH,
            ViolationType.INVALID_CATALOG_REFERENCE: RiskLevel.MEDIUM,
            ViolationType.MISSING_GROUNDING: RiskLevel.MEDIUM,
            
            # Default
            ViolationType.NO_VIOLATION: RiskLevel.NONE,
            ViolationType.UNKNOWN_VIOLATION: RiskLevel.MEDIUM,
        }
    
    def classify(
        self,
        violation_type: ViolationType,
        confidence: float,
    ) -> tuple[RiskLevel, bool]:
        """
        Classify risk level for violation.
        
        Args:
            violation_type: Type of violation
            confidence: Detection confidence (0-1)
        
        Returns:
            (risk_level, should_block)
        """
        # Get base risk level
        risk_level = self._violation_risk_map.get(
            violation_type,
            RiskLevel.MEDIUM
        )
        
        # Adjust for confidence
        if confidence < 0.5 and risk_level == RiskLevel.HIGH:
            # Lower to medium if low confidence
            risk_level = RiskLevel.MEDIUM
        
        # Determine if should block
        should_block = self._should_block(risk_level, confidence)
        
        logger.debug(
            f"Risk classification: {violation_type.value} -> "
            f"{risk_level.value} (block={should_block})"
        )
        
        return risk_level, should_block
    
    def _should_block(self, risk_level: RiskLevel, confidence: float) -> bool:
        """Determine if request should be blocked."""
        # Always block critical threats
        if risk_level == RiskLevel.CRITICAL:
            return True
        
        # Block high risk with decent confidence
        if risk_level == RiskLevel.HIGH and confidence >= 0.6:
            return True
        
        # Block medium risk with moderate confidence
        if risk_level == RiskLevel.MEDIUM and confidence >= 0.6:
            return True
        
        # Allow low risk and none
        if risk_level in [RiskLevel.LOW, RiskLevel.NONE]:
            return False
        
        # Default: allow with warning
        return False
    
    def get_risk_score(self, risk_level: RiskLevel) -> float:
        """
        Get numeric risk score.
        
        Returns:
            Score from 0.0 (none) to 1.0 (critical)
        """
        scores = {
            RiskLevel.NONE: 0.0,
            RiskLevel.LOW: 0.25,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.HIGH: 0.75,
            RiskLevel.CRITICAL: 1.0,
        }
        return scores.get(risk_level, 0.5)
