"""
Intent type definitions.

Comprehensive set of user intents for the conversation system.
"""

from enum import Enum


class IntentType(str, Enum):
    """
    User intent types.
    
    Each intent represents a distinct user goal in the conversation.
    Used by the intent classifier to determine routing.
    """
    
    # Core conversation intents
    GREETING = "greeting"
    CLARIFICATION = "clarification"
    RECOMMENDATION = "recommendation"
    COMPARISON = "comparison"
    REFINEMENT = "refinement"
    COMPLETION = "completion"
    
    # Security & guardrails
    PROMPT_INJECTION = "prompt_injection"
    REFUSAL = "refusal"
    
    # Fallback
    UNKNOWN = "unknown"


class ConfidenceLevel(str, Enum):
    """Confidence level for intent detection."""
    
    HIGH = "high"      # > 0.8
    MEDIUM = "medium"  # 0.5 - 0.8
    LOW = "low"        # 0.3 - 0.5
    UNKNOWN = "unknown"  # < 0.3


class RoutingTarget(str, Enum):
    """
    Routing targets for intents.
    
    Defines which module should handle each intent.
    """
    
    CLARIFICATION_ENGINE = "clarification_engine"
    RECOMMENDATION_ENGINE = "recommendation_engine"
    COMPARISON_ENGINE = "comparison_engine"
    REFINEMENT_HANDLER = "refinement_handler"
    GUARDRAILS = "guardrails"
    RESPONSE_FORMATTER = "response_formatter"
    CONVERSATION_COMPLETE = "conversation_complete"
