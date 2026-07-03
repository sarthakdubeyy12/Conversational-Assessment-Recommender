"""
Refusal engine.

Generates structured refusal messages.
"""

from src.guardrails.domain.violation_type import ViolationType
from src.guardrails.refusal.refusal_reason import RefusalReason
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class RefusalEngine:
    """
    Generate structured refusals.
    
    Responsibilities:
    - Map violations to refusal reasons
    - Generate user-friendly messages
    - Provide recommended actions
    
    Design:
    - Deterministic mapping
    - User-friendly output
    - Actionable guidance
    """
    
    def __init__(self) -> None:
        """Initialize refusal engine."""
        # Map violations to refusal reasons
        self._violation_to_reason = {
            ViolationType.PROMPT_INJECTION: RefusalReason.PROMPT_INJECTION,
            ViolationType.JAILBREAK: RefusalReason.JAILBREAK_ATTEMPT,
            ViolationType.SYSTEM_PROMPT_LEAK: RefusalReason.MALICIOUS_INPUT,
            ViolationType.TOOL_MANIPULATION: RefusalReason.MALICIOUS_INPUT,
            ViolationType.INSTRUCTION_OVERRIDE: RefusalReason.MALICIOUS_INPUT,
            ViolationType.OUT_OF_SCOPE: RefusalReason.OUT_OF_SCOPE,
            ViolationType.OFF_TOPIC: RefusalReason.OFF_TOPIC,
            ViolationType.UNSUPPORTED_REQUEST: RefusalReason.UNSUPPORTED_DOMAIN,
            ViolationType.HALLUCINATION: RefusalReason.HALLUCINATION_DETECTED,
            ViolationType.FABRICATED_URL: RefusalReason.FABRICATED_CONTENT,
            ViolationType.FABRICATED_ASSESSMENT: RefusalReason.FABRICATED_CONTENT,
            ViolationType.MISSING_GROUNDING: RefusalReason.MISSING_CATALOG_DATA,
        }
        
        # User-facing messages
        self._refusal_messages = {
            RefusalReason.PROMPT_INJECTION: (
                "I detected an attempt to manipulate my instructions. "
                "I can only help with SHL assessment recommendations."
            ),
            RefusalReason.JAILBREAK_ATTEMPT: (
                "I cannot process that request. "
                "I'm designed specifically for SHL assessment recommendations."
            ),
            RefusalReason.MALICIOUS_INPUT: (
                "I cannot process that input. "
                "Please ask about SHL assessments for your hiring needs."
            ),
            RefusalReason.OUT_OF_SCOPE: (
                "That request is outside my scope. "
                "I specialize in recommending SHL Individual Test Solutions. "
                "Please ask about assessments for your hiring needs."
            ),
            RefusalReason.OFF_TOPIC: (
                "I can only help with SHL assessment recommendations. "
                "Please ask about tests or evaluations for hiring."
            ),
            RefusalReason.UNSUPPORTED_DOMAIN: (
                "I cannot help with that topic. "
                "I focus on SHL assessments like cognitive tests, personality inventories, "
                "and situational judgment tests."
            ),
            RefusalReason.HALLUCINATION_DETECTED: (
                "I cannot provide that information as it may not be accurate. "
                "Let me search the SHL catalog for verified assessments."
            ),
            RefusalReason.FABRICATED_CONTENT: (
                "I cannot verify that information in the SHL catalog. "
                "I can only recommend assessments that exist in our database."
            ),
            RefusalReason.MISSING_CATALOG_DATA: (
                "I don't have sufficient information in the catalog to answer that. "
                "Could you provide more details about your hiring needs?"
            ),
            RefusalReason.INSUFFICIENT_INFORMATION: (
                "I need more information to help you. "
                "Could you describe the role and skills you're hiring for?"
            ),
        }
    
    def generate_refusal(
        self,
        violation_type: ViolationType,
    ) -> tuple[RefusalReason, str, str]:
        """
        Generate refusal for violation.
        
        Args:
            violation_type: Type of violation
        
        Returns:
            (reason, message, recommended_action)
        """
        # Map to refusal reason
        reason = self._violation_to_reason.get(
            violation_type,
            RefusalReason.UNKNOWN_ERROR
        )
        
        # Get user message
        message = self._refusal_messages.get(
            reason,
            "I cannot process that request. Please ask about SHL assessments."
        )
        
        # Recommended action
        action = self._get_recommended_action(reason)
        
        logger.info(f"Generated refusal: {reason.value}")
        
        return reason, message, action
    
    def _get_recommended_action(self, reason: RefusalReason) -> str:
        """Get recommended action for reason."""
        if reason in [
            RefusalReason.PROMPT_INJECTION,
            RefusalReason.JAILBREAK_ATTEMPT,
            RefusalReason.MALICIOUS_INPUT,
        ]:
            return "Ask about SHL assessment needs"
        
        if reason in [
            RefusalReason.OUT_OF_SCOPE,
            RefusalReason.OFF_TOPIC,
            RefusalReason.UNSUPPORTED_DOMAIN,
        ]:
            return "Describe your hiring role and required skills"
        
        if reason == RefusalReason.MISSING_CATALOG_DATA:
            return "Provide more context about the position"
        
        return "Rephrase your question about SHL assessments"
