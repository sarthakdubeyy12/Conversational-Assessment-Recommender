"""
Execution context.

Contains all data needed for pipeline execution.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class ConversationMessage:
    """Single conversation message."""
    
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExecutionContext:
    """
    Complete execution context.
    
    Carries all data through the pipeline.
    
    Design:
    - Mutable (accumulates results)
    - Comprehensive state
    - Self-contained
    """
    
    # Input
    user_message: str
    conversation_history: List[ConversationMessage] = field(default_factory=list)
    
    # Configuration
    session_id: str = ""
    max_tokens: int = 1000
    temperature: float = 0.7
    
    # Results (populated during execution)
    conversation_state: Optional[Any] = None
    intent_result: Optional[Any] = None
    guardrail_input_result: Optional[Any] = None
    retrieval_result: Optional[Any] = None
    recommendation_result: Optional[Any] = None
    comparison_result: Optional[Any] = None
    guardrail_output_result: Optional[Any] = None
    final_response: str = ""
    
    # Metadata
    execution_start: datetime = field(default_factory=datetime.utcnow)
    current_stage: str = "initialized"
    
    def add_message(self, role: str, content: str) -> None:
        """Add message to history."""
        msg = ConversationMessage(role=role, content=content)
        self.conversation_history.append(msg)
    
    def get_execution_time_ms(self) -> float:
        """Calculate execution time."""
        return (datetime.utcnow() - self.execution_start).total_seconds() * 1000
