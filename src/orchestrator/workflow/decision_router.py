"""
Decision router.

Routes workflow based on intent and guardrails.
"""

from typing import Any
from src.conversation.intent.domain.intent_types import IntentType
from src.guardrails.domain.guardrail_result import GuardrailResult
from src.orchestrator.workflow.workflow_state import WorkflowState
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class DecisionRouter:
    """
    Route workflow based on intent and guardrails.
    
    Responsibilities:
    - Determine next workflow state
    - Handle guardrail blocks
    - Route based on intent type
    
    Design:
    - Deterministic routing
    - Clear decision logic
    - No business logic
    """
    
    def __init__(self) -> None:
        """Initialize router."""
        pass
    
    def route_after_guardrails(
        self,
        guardrail_result: GuardrailResult,
    ) -> WorkflowState:
        """
        Route after guardrails check.
        
        Args:
            guardrail_result: Guardrail validation result
        
        Returns:
            Next workflow state
        """
        if guardrail_result.should_block():
            logger.warning("Request blocked by guardrails")
            return WorkflowState.BLOCKED
        
        # Safe to continue
        return WorkflowState.NEEDS_RETRIEVAL
    
    def route_after_intent(
        self,
        intent_result: Any,
    ) -> WorkflowState:
        """
        Route based on detected intent.
        
        Args:
            intent_result: Intent detection result
        
        Returns:
            Next workflow state
        """
        intent = intent_result.primary_intent
        
        # Recommendation intent
        if intent == IntentType.RECOMMENDATION:
            if intent_result.requires_retrieval:
                return WorkflowState.NEEDS_RETRIEVAL
            else:
                return WorkflowState.NEEDS_CLARIFICATION
        
        # Comparison intent
        elif intent == IntentType.COMPARISON:
            if intent_result.requires_retrieval:
                return WorkflowState.NEEDS_RETRIEVAL
            else:
                return WorkflowState.NEEDS_CLARIFICATION
        
        # Clarification
        elif intent == IntentType.CLARIFICATION:
            return WorkflowState.NEEDS_CLARIFICATION
        
        # Greeting
        elif intent == IntentType.GREETING:
            return WorkflowState.GENERATING_RESPONSE
        
        # Refinement
        elif intent == IntentType.REFINEMENT:
            return WorkflowState.NEEDS_RETRIEVAL
        
        # Completion
        elif intent == IntentType.COMPLETION:
            return WorkflowState.COMPLETED
        
        # Refusal/Injection
        elif intent in [IntentType.REFUSAL, IntentType.PROMPT_INJECTION]:
            return WorkflowState.BLOCKED
        
        # Unknown - ask for clarification
        else:
            return WorkflowState.NEEDS_CLARIFICATION
    
    def route_after_retrieval(
        self,
        intent_result: Any,
        retrieval_result: Any,
    ) -> WorkflowState:
        """
        Route after retrieval completion.
        
        Args:
            intent_result: Intent detection result
            retrieval_result: Retrieval pipeline result
        
        Returns:
            Next workflow state
        """
        intent = intent_result.primary_intent
        
        # Check if retrieval was successful
        if not retrieval_result or len(retrieval_result.ranked_documents) == 0:
            logger.warning("No retrieval results, requesting clarification")
            return WorkflowState.NEEDS_CLARIFICATION
        
        # Route based on intent
        if intent == IntentType.COMPARISON or intent_result.requires_comparison:
            return WorkflowState.NEEDS_COMPARISON
        
        if intent == IntentType.RECOMMENDATION or intent_result.requires_recommendation:
            return WorkflowState.NEEDS_RECOMMENDATION
        
        # Default: generate response
        return WorkflowState.GENERATING_RESPONSE
