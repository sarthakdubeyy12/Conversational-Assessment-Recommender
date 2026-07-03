"""
Guardrail result entity.

Structured output from guardrails engine.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.guardrails.domain.violation_type import ViolationType
from src.guardrails.domain.risk_level import RiskLevel


@dataclass(frozen=True)
class AuditMetadata:
    """
    Audit trail metadata.
    
    Captures violation details for logging and analysis.
    """
    
    matched_rule: str
    trigger_phrase: Optional[str]
    detector_name: str
    processing_time_ms: float
    rule_version: str = "1.0"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    additional_context: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GuardrailResult:
    """
    Complete guardrail engine output.
    
    Determines whether request/response should proceed or be blocked.
    
    Design:
    - Immutable
    - Strongly typed
    - Audit-ready
    - Decision-focused
    """
    
    # Primary decision
    allow_processing: bool
    
    # Classification
    violation_type: ViolationType
    risk_level: RiskLevel
    confidence: float  # 0.0 to 1.0
    
    # Evidence
    triggered_rules: List[str]
    trigger_phrases: List[str] = field(default_factory=list)
    
    # Validation results
    catalog_grounded: bool = True
    output_safe: bool = True
    
    # Refusal
    refusal_reason: str = ""
    recommended_action: str = ""
    
    # Audit
    audit_metadata: Optional[AuditMetadata] = None
    
    # Processing
    processing_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def is_safe(self) -> bool:
        """Check if request is safe to process."""
        return (
            self.allow_processing
            and self.violation_type == ViolationType.NO_VIOLATION
            and self.risk_level in [RiskLevel.NONE, RiskLevel.LOW]
        )
    
    def should_block(self) -> bool:
        """Check if request should be blocked."""
        return not self.allow_processing
    
    def requires_audit(self) -> bool:
        """Check if result requires audit logging."""
        return (
            not self.allow_processing
            or self.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
            or len(self.triggered_rules) > 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "allow_processing": self.allow_processing,
            "violation_type": self.violation_type.value,
            "risk_level": self.risk_level.value,
            "confidence": self.confidence,
            "triggered_rules": self.triggered_rules,
            "trigger_phrases": self.trigger_phrases,
            "catalog_grounded": self.catalog_grounded,
            "output_safe": self.output_safe,
            "refusal_reason": self.refusal_reason,
            "recommended_action": self.recommended_action,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat(),
        }
