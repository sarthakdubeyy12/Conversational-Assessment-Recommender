"""
Pipeline stages.

Defines orchestration workflow stages.
"""

from enum import Enum


class PipelineStage(str, Enum):
    """
    Orchestration pipeline stages.
    
    Each stage represents a discrete step in the workflow.
    """
    
    # Core stages
    STATE_RECONSTRUCTION = "state_reconstruction"
    INTENT_DETECTION = "intent_detection"
    GUARDRAILS_INPUT = "guardrails_input"
    RETRIEVAL = "retrieval"
    RECOMMENDATION = "recommendation"
    COMPARISON = "comparison"
    GUARDRAILS_OUTPUT = "guardrails_output"
    RESPONSE_GENERATION = "response_generation"
    
    # Terminal stages
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
