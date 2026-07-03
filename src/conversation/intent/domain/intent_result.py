"""
Intent detection result.

Structured output from intent detection.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from src.conversation.intent.domain.intent_types import (
    IntentType,
    ConfidenceLevel,
    RoutingTarget,
)


@dataclass(frozen=True)
class IntentResult:
    """
    Intent detection result.
    
    Complete structured output from intent detection engine.
    Consumed by conversation orchestrator for routing decisions.
    
    Design:
    - Immutable (frozen dataclass)
    - Deterministic output
    - Rich metadata for debugging
    - Clear routing instructions
    """
    
    # Primary classification
    primary_intent: IntentType
    secondary_intents: List[IntentType] = field(default_factory=list)
    
    # Confidence
    confidence_level: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    confidence_score: float = 0.0  # 0.0 to 1.0
    
    # Routing
    routing_target: RoutingTarget = RoutingTarget.RESPONSE_FORMATTER
    
    # Requirements flags
    requires_llm: bool = False
    requires_retrieval: bool = False
    requires_clarification: bool = False
    requires_guardrails: bool = False
    requires_comparison: bool = False
    requires_recommendation: bool = False
    requires_refinement: bool = False
    
    # State flags
    conversation_complete: bool = False
    
    # Detection metadata
    matched_patterns: List[str] = field(default_factory=list)
    matched_keywords: List[str] = field(default_factory=list)
    decision_reason: str = ""
    
    # Additional context
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "primary_intent": self.primary_intent.value,
            "secondary_intents": [i.value for i in self.secondary_intents],
            "confidence_level": self.confidence_level.value,
            "confidence_score": self.confidence_score,
            "routing_target": self.routing_target.value,
            "requires_llm": self.requires_llm,
            "requires_retrieval": self.requires_retrieval,
            "requires_clarification": self.requires_clarification,
            "requires_guardrails": self.requires_guardrails,
            "requires_comparison": self.requires_comparison,
            "requires_recommendation": self.requires_recommendation,
            "requires_refinement": self.requires_refinement,
            "conversation_complete": self.conversation_complete,
            "matched_patterns": self.matched_patterns,
            "matched_keywords": self.matched_keywords,
            "decision_reason": self.decision_reason,
            "metadata": self.metadata,
        }
    
    def is_high_confidence(self) -> bool:
        """Check if confidence is high."""
        return self.confidence_level == ConfidenceLevel.HIGH
    
    def is_actionable(self) -> bool:
        """Check if intent is actionable (not unknown/refusal)."""
        return self.primary_intent not in [
            IntentType.UNKNOWN,
            IntentType.REFUSAL,
            IntentType.PROMPT_INJECTION,
        ]
