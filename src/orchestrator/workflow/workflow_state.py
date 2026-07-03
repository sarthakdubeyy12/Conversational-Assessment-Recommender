"""
Workflow states.

Defines state machine states for orchestration.
"""

from enum import Enum


class WorkflowState(str, Enum):
    """
    Orchestration workflow states.
    
    Represents current position in the state machine.
    """
    
    # Initial
    START = "start"
    
    # Core states
    STATE_RECONSTRUCTION = "state_reconstruction"
    INTENT_DETECTION = "intent_detection"
    GUARDRAILS_CHECK = "guardrails_check"
    
    # Branching states
    NEEDS_RETRIEVAL = "needs_retrieval"
    NEEDS_RECOMMENDATION = "needs_recommendation"
    NEEDS_COMPARISON = "needs_comparison"
    NEEDS_CLARIFICATION = "needs_clarification"
    
    # Processing states
    RETRIEVING = "retrieving"
    RECOMMENDING = "recommending"
    COMPARING = "comparing"
    
    # Final states
    GENERATING_RESPONSE = "generating_response"
    VALIDATING_OUTPUT = "validating_output"
    COMPLETED = "completed"
    
    # Error states
    BLOCKED = "blocked"
    FAILED = "failed"
