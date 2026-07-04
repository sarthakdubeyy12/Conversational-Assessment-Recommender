"""
Prompt package model.

Contains a complete prompt ready for LLM invocation.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class PromptPackage:
    """
    Complete prompt package for LLM invocation.
    
    Contains all data needed to invoke an LLM provider.
    
    Design:
    - Immutable after creation
    - Provider-agnostic
    - Token-optimized
    - Fully structured
    """
    
    # Core prompt content
    system_prompt: str
    user_prompt: str
    
    # Metadata
    prompt_type: str  # "recommendation", "comparison", "clarification", "refusal", "fallback"
    version: str = "1.0.0"
    
    # Context (for debugging/observability)
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Token estimates
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    
    # Provider configuration
    temperature: float = 0.7
    max_tokens: int = 1000
    
    # Optional conversation history (for multi-turn)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging."""
        return {
            "prompt_type": self.prompt_type,
            "version": self.version,
            "system_prompt_length": len(self.system_prompt),
            "user_prompt_length": len(self.user_prompt),
            "estimated_input_tokens": self.estimated_input_tokens,
            "estimated_output_tokens": self.estimated_output_tokens,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "history_length": len(self.conversation_history),
        }
