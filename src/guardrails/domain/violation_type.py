"""
Violation types.

Classification of security and safety violations.
"""

from enum import Enum


class ViolationType(str, Enum):
    """
    Types of guardrail violations.
    
    Each type represents a distinct security or safety concern.
    """
    
    # Security violations
    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK = "jailbreak"
    SYSTEM_PROMPT_LEAK = "system_prompt_leak"
    TOOL_MANIPULATION = "tool_manipulation"
    INSTRUCTION_OVERRIDE = "instruction_override"
    
    # Scope violations
    OUT_OF_SCOPE = "out_of_scope"
    UNSUPPORTED_REQUEST = "unsupported_request"
    OFF_TOPIC = "off_topic"
    
    # Validation violations
    HALLUCINATION = "hallucination"
    INVALID_CATALOG_REFERENCE = "invalid_catalog_reference"
    MISSING_GROUNDING = "missing_grounding"
    FABRICATED_URL = "fabricated_url"
    FABRICATED_ASSESSMENT = "fabricated_assessment"
    
    # Generic
    UNKNOWN_VIOLATION = "unknown_violation"
    NO_VIOLATION = "no_violation"
