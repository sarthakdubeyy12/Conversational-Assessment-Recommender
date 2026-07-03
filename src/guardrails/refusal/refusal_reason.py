"""
Refusal reasons.

Structured reasons for blocking requests.
"""

from enum import Enum


class RefusalReason(str, Enum):
    """
    Reasons for refusing to process requests.
    
    Each reason corresponds to a specific violation category.
    """
    
    # Security
    PROMPT_INJECTION = "prompt_injection_detected"
    JAILBREAK_ATTEMPT = "jailbreak_attempt_detected"
    MALICIOUS_INPUT = "malicious_input_detected"
    
    # Scope
    OUT_OF_SCOPE = "request_out_of_scope"
    UNSUPPORTED_DOMAIN = "unsupported_domain"
    OFF_TOPIC = "off_topic_request"
    
    # Validation
    INVALID_OUTPUT = "invalid_output_generated"
    HALLUCINATION_DETECTED = "hallucination_detected"
    MISSING_CATALOG_DATA = "catalog_data_missing"
    FABRICATED_CONTENT = "fabricated_content_detected"
    
    # Generic
    UNKNOWN_ERROR = "unknown_error"
    INSUFFICIENT_INFORMATION = "insufficient_information"
