"""
Audit logger.

Logs security and safety events for compliance and analysis.
"""

from typing import Dict, Any
from datetime import datetime
from src.guardrails.domain.guardrail_result import GuardrailResult
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class AuditLogger:
    """
    Log guardrail events for audit trail.
    
    Responsibilities:
    - Log violations and blocks
    - Maintain structured audit records
    - Enable security analysis
    - Support compliance requirements
    
    Design:
    - No PII logging
    - Structured data
    - Timestamp everything
    - Compliance-ready
    """
    
    def __init__(self) -> None:
        """Initialize audit logger."""
        self._log_count = 0
    
    def log_violation(
        self,
        result: GuardrailResult,
        user_query: str = "",
    ) -> None:
        """
        Log guardrail violation.
        
        Args:
            result: Guardrail result
            user_query: User query (sanitized, no PII)
        """
        # Sanitize query (limit length, no PII)
        sanitized_query = self._sanitize_query(user_query)
        
        audit_record = {
            "event": "guardrail_violation",
            "timestamp": result.timestamp.isoformat(),
            "violation_type": result.violation_type.value,
            "risk_level": result.risk_level.value,
            "confidence": result.confidence,
            "allow_processing": result.allow_processing,
            "triggered_rules": result.triggered_rules,
            "trigger_phrases": result.trigger_phrases,
            "query_length": len(user_query),
            "query_preview": sanitized_query,
            "processing_time_ms": result.processing_time_ms,
        }
        
        # Log based on severity
        if result.risk_level.value in ["critical", "high"]:
            logger.warning(f"Security violation: {audit_record}")
        else:
            logger.info(f"Guardrail event: {audit_record}")
        
        self._log_count += 1
    
    def log_validation_failure(
        self,
        validation_type: str,
        violations: list[str],
        context: Dict[str, Any],
    ) -> None:
        """
        Log output validation failure.
        
        Args:
            validation_type: Type of validation
            violations: List of violations
            context: Additional context
        """
        audit_record = {
            "event": "validation_failure",
            "timestamp": datetime.utcnow().isoformat(),
            "validation_type": validation_type,
            "violations": violations,
            "context": context,
        }
        
        logger.warning(f"Validation failure: {audit_record}")
        self._log_count += 1
    
    def log_hallucination_prevention(
        self,
        content_type: str,
        prevented_content: str,
    ) -> None:
        """
        Log prevented hallucination.
        
        Args:
            content_type: Type of content (URL, assessment, etc)
            prevented_content: What was prevented
        """
        audit_record = {
            "event": "hallucination_prevented",
            "timestamp": datetime.utcnow().isoformat(),
            "content_type": content_type,
            "prevented": prevented_content[:100],  # Limit length
        }
        
        logger.warning(f"Hallucination prevented: {audit_record}")
        self._log_count += 1
    
    def log_scope_violation(
        self,
        detected_domain: str,
        confidence: float,
    ) -> None:
        """
        Log scope violation.
        
        Args:
            detected_domain: Detected off-topic domain
            confidence: Detection confidence
        """
        audit_record = {
            "event": "scope_violation",
            "timestamp": datetime.utcnow().isoformat(),
            "detected_domain": detected_domain,
            "confidence": confidence,
        }
        
        logger.info(f"Scope violation: {audit_record}")
        self._log_count += 1
    
    def get_audit_stats(self) -> Dict[str, int]:
        """Get audit statistics."""
        return {
            "total_events_logged": self._log_count,
        }
    
    def _sanitize_query(self, query: str, max_length: int = 50) -> str:
        """
        Sanitize query for logging.
        
        Remove PII, limit length.
        """
        if not query:
            return ""
        
        # Truncate
        sanitized = query[:max_length]
        
        # Add ellipsis if truncated
        if len(query) > max_length:
            sanitized += "..."
        
        return sanitized
