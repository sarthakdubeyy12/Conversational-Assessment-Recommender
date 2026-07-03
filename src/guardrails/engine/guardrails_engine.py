"""
Guardrails engine.

Main orchestrator for AI safety and validation.
"""

import time
from typing import List, Optional, Any
from src.guardrails.domain.guardrail_result import GuardrailResult, AuditMetadata
from src.guardrails.domain.violation_type import ViolationType
from src.guardrails.domain.risk_level import RiskLevel
from src.guardrails.detectors.prompt_injection_detector import PromptInjectionDetector
from src.guardrails.detectors.scope_detector import ScopeDetector
from src.guardrails.detectors.output_validator import OutputValidator
from src.guardrails.validation.catalog_validator import CatalogValidator
from src.guardrails.refusal.refusal_engine import RefusalEngine
from src.guardrails.risk.risk_classifier import RiskClassifier
from src.guardrails.audit.audit_logger import AuditLogger
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class GuardrailsEngine:
    """
    Production guardrails engine.
    
    Complete safety pipeline:
    1. Input Validation (prompt injection, scope)
    2. Output Validation (catalog grounding, hallucination)
    3. Risk Classification
    4. Refusal Generation
    5. Audit Logging
    
    Responsibilities:
    - Protect against malicious input
    - Enforce scope boundaries
    - Validate catalog grounding
    - Prevent hallucination
    - Generate structured refusals
    - Maintain audit trail
    
    Design:
    - Deterministic execution
    - Fail-safe defaults
    - Comprehensive logging
    - Production-ready
    """
    
    def __init__(
        self,
        prompt_injection_detector: PromptInjectionDetector,
        scope_detector: ScopeDetector,
        output_validator: OutputValidator,
        catalog_validator: CatalogValidator,
        refusal_engine: RefusalEngine,
        risk_classifier: RiskClassifier,
        audit_logger: AuditLogger,
    ) -> None:
        """
        Initialize guardrails engine.
        
        Args:
            prompt_injection_detector: Prompt injection detector
            scope_detector: Scope violation detector
            output_validator: Output validator
            catalog_validator: Catalog grounding validator
            refusal_engine: Refusal message generator
            risk_classifier: Risk level classifier
            audit_logger: Audit event logger
        """
        self._injection_detector = prompt_injection_detector
        self._scope_detector = scope_detector
        self._output_validator = output_validator
        self._catalog_validator = catalog_validator
        self._refusal_engine = refusal_engine
        self._risk_classifier = risk_classifier
        self._audit_logger = audit_logger
        
        logger.info("GuardrailsEngine initialized")
    
    def validate_input(self, user_message: str) -> GuardrailResult:
        """
        Validate user input before processing.
        
        Args:
            user_message: User's input message
        
        Returns:
            GuardrailResult with validation decision
        """
        logger.debug(f"Validating input: length={len(user_message)}")
        start_time = time.time()
        
        # Stage 1: Prompt injection detection
        is_injection, inj_confidence, inj_phrases = self._injection_detector.detect(
            user_message
        )
        
        if is_injection:
            violation_type = ViolationType.PROMPT_INJECTION
            risk_level, should_block = self._risk_classifier.classify(
                violation_type, inj_confidence
            )
            
            reason, message, action = self._refusal_engine.generate_refusal(
                violation_type
            )
            
            result = self._build_result(
                allow_processing=not should_block,
                violation_type=violation_type,
                risk_level=risk_level,
                confidence=inj_confidence,
                triggered_rules=["prompt_injection"],
                trigger_phrases=inj_phrases,
                refusal_reason=message,
                recommended_action=action,
                processing_time_ms=(time.time() - start_time) * 1000,
            )
            
            self._audit_logger.log_violation(result, user_message)
            return result
        
        # Stage 2: Scope detection
        is_out_of_scope, domain, scope_confidence = self._scope_detector.detect(
            user_message
        )
        
        if is_out_of_scope:
            violation_type = ViolationType.OUT_OF_SCOPE
            risk_level, should_block = self._risk_classifier.classify(
                violation_type, scope_confidence
            )
            
            reason, message, action = self._refusal_engine.generate_refusal(
                violation_type
            )
            
            result = self._build_result(
                allow_processing=not should_block,
                violation_type=violation_type,
                risk_level=risk_level,
                confidence=scope_confidence,
                triggered_rules=[f"scope_{domain}"],
                trigger_phrases=[domain],
                refusal_reason=message,
                recommended_action=action,
                processing_time_ms=(time.time() - start_time) * 1000,
            )
            
            self._audit_logger.log_scope_violation(domain, scope_confidence)
            return result
        
        # All checks passed
        result = self._build_result(
            allow_processing=True,
            violation_type=ViolationType.NO_VIOLATION,
            risk_level=RiskLevel.NONE,
            confidence=1.0,
            triggered_rules=[],
            trigger_phrases=[],
            refusal_reason="",
            recommended_action="",
            processing_time_ms=(time.time() - start_time) * 1000,
        )
        
        logger.debug(f"Input validation passed: {result.processing_time_ms:.1f}ms")
        return result
    
    def validate_output(
        self,
        output: Any,
        output_type: str,
        catalog_ids: List[str],
    ) -> GuardrailResult:
        """
        Validate generated output before returning to user.
        
        Args:
            output: Output object to validate
            output_type: Type of output (recommendation, comparison)
            catalog_ids: Valid assessment IDs from catalog
        
        Returns:
            GuardrailResult with validation decision
        """
        logger.debug(f"Validating output: type={output_type}")
        start_time = time.time()
        
        violations = []
        
        # Validate based on output type
        if output_type == "recommendation":
            is_valid, output_violations = self._output_validator.validate_recommendation(
                output, catalog_ids
            )
            violations.extend(output_violations)
        
        elif output_type == "comparison":
            is_valid, output_violations = self._output_validator.validate_comparison(
                output, catalog_ids
            )
            violations.extend(output_violations)
        
        else:
            is_valid = True
        
        # If validation failed
        if not is_valid:
            violation_type = ViolationType.INVALID_CATALOG_REFERENCE
            risk_level = RiskLevel.HIGH
            
            reason, message, action = self._refusal_engine.generate_refusal(
                violation_type
            )
            
            result = self._build_result(
                allow_processing=False,
                violation_type=violation_type,
                risk_level=risk_level,
                confidence=0.9,
                triggered_rules=["output_validation"],
                trigger_phrases=violations,
                catalog_grounded=False,
                output_safe=False,
                refusal_reason=message,
                recommended_action=action,
                processing_time_ms=(time.time() - start_time) * 1000,
            )
            
            self._audit_logger.log_validation_failure(
                output_type, violations, {"output_type": output_type}
            )
            
            return result
        
        # Validation passed
        result = self._build_result(
            allow_processing=True,
            violation_type=ViolationType.NO_VIOLATION,
            risk_level=RiskLevel.NONE,
            confidence=1.0,
            triggered_rules=[],
            trigger_phrases=[],
            catalog_grounded=True,
            output_safe=True,
            refusal_reason="",
            recommended_action="",
            processing_time_ms=(time.time() - start_time) * 1000,
        )
        
        logger.debug(f"Output validation passed: {result.processing_time_ms:.1f}ms")
        return result
    
    def _build_result(
        self,
        allow_processing: bool,
        violation_type: ViolationType,
        risk_level: RiskLevel,
        confidence: float,
        triggered_rules: List[str],
        trigger_phrases: List[str],
        refusal_reason: str,
        recommended_action: str,
        processing_time_ms: float,
        catalog_grounded: bool = True,
        output_safe: bool = True,
    ) -> GuardrailResult:
        """Build guardrail result."""
        return GuardrailResult(
            allow_processing=allow_processing,
            violation_type=violation_type,
            risk_level=risk_level,
            confidence=confidence,
            triggered_rules=triggered_rules,
            trigger_phrases=trigger_phrases,
            catalog_grounded=catalog_grounded,
            output_safe=output_safe,
            refusal_reason=refusal_reason,
            recommended_action=recommended_action,
            processing_time_ms=processing_time_ms,
        )
