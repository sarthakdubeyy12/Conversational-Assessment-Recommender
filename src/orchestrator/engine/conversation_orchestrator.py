"""
Conversation orchestrator.

Central workflow engine coordinating all components.
"""

import uuid
from datetime import datetime
from src.orchestrator.domain.execution_context import ExecutionContext
from src.orchestrator.domain.execution_trace import ExecutionTrace
from src.orchestrator.domain.orchestration_result import (
    OrchestrationResult,
    OrchestrationStatistics,
)
from src.orchestrator.domain.pipeline_stage import PipelineStage
from src.orchestrator.workflow.workflow_state import WorkflowState
from src.orchestrator.workflow.decision_router import DecisionRouter
from src.orchestrator.execution.pipeline_executor import PipelineExecutor
from src.orchestrator.execution.error_handler import ErrorHandler, ExecutionError
from src.orchestrator.response.response_builder import ResponseBuilder
from src.conversation.intent.domain.intent_types import IntentType
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ConversationOrchestrator:
    """
    Production conversation orchestrator.
    
    Central workflow engine that coordinates:
    - Conversation State Engine
    - Intent Detection Engine
    - Guardrails Engine
    - Retrieval Pipeline
    - Recommendation Engine
    - Comparison Engine
    - Response Generation
    
    Responsibilities:
    - Execute workflow state machine
    - Coordinate all components
    - Handle errors gracefully
    - Track execution metrics
    - Generate final responses
    
    Design:
    - Stateless execution
    - Pure coordination
    - No business logic
    - Dependency injection
    - Error recovery
    """
    
    def __init__(
        self,
        executor: PipelineExecutor,
        router: DecisionRouter,
        response_builder: ResponseBuilder,
        error_handler: ErrorHandler,
    ) -> None:
        """
        Initialize orchestrator.
        
        Args:
            executor: Pipeline executor
            router: Decision router
            response_builder: Response builder
            error_handler: Error handler
        """
        self._executor = executor
        self._router = router
        self._response_builder = response_builder
        self._error_handler = error_handler
        
        logger.info("ConversationOrchestrator initialized")
    
    async def execute(
        self,
        user_message: str,
        conversation_history: list = None,
        session_id: str = "",
    ) -> OrchestrationResult:
        """
        Execute complete orchestration workflow.
        
        Args:
            user_message: User's message
            conversation_history: Previous conversation messages
            session_id: Session identifier
        
        Returns:
            OrchestrationResult with complete execution data
        """
        # Initialize context and trace
        execution_id = str(uuid.uuid4())
        context = ExecutionContext(
            user_message=user_message,
            conversation_history=conversation_history or [],
            session_id=session_id or execution_id,
        )
        trace = ExecutionTrace(execution_id=execution_id)
        
        logger.info(f"Starting orchestration: {execution_id}")
        
        try:
            # Execute workflow state machine
            await self._execute_workflow(context, trace)
            
            # Build final response
            response = self._build_response(context)
            context.final_response = response
            
            # Create result
            trace.finalize()
            result = self._create_result(context, trace, success=True)
            
            logger.info(f"Orchestration completed: {execution_id} ({trace.total_duration_ms:.1f}ms)")
            return result
            
        except Exception as e:
            logger.error(f"Orchestration failed: {e}", exc_info=True)
            
            # Handle error and generate fallback
            is_recoverable, fallback_message = self._error_handler.handle_error(
                e, "orchestration"
            )
            
            context.final_response = fallback_message
            trace.finalize()
            
            result = self._create_result(context, trace, success=False)
            return result
    
    async def _execute_workflow(
        self,
        context: ExecutionContext,
        trace: ExecutionTrace,
    ) -> None:
        """Execute workflow state machine."""
        current_state = WorkflowState.START
        
        while current_state not in [
            WorkflowState.COMPLETED,
            WorkflowState.BLOCKED,
            WorkflowState.FAILED,
        ]:
            logger.debug(f"Workflow state: {current_state.value}")
            context.current_stage = current_state.value
            
            # Execute based on current state
            if current_state == WorkflowState.START:
                current_state = WorkflowState.STATE_RECONSTRUCTION
            
            elif current_state == WorkflowState.STATE_RECONSTRUCTION:
                self._executor.execute_state_reconstruction(context, trace)
                current_state = WorkflowState.INTENT_DETECTION
            
            elif current_state == WorkflowState.INTENT_DETECTION:
                self._executor.execute_intent_detection(context, trace)
                current_state = WorkflowState.GUARDRAILS_CHECK
            
            elif current_state == WorkflowState.GUARDRAILS_CHECK:
                self._executor.execute_guardrails_input(context, trace)
                current_state = self._router.route_after_guardrails(
                    context.guardrail_input_result
                )
            
            elif current_state == WorkflowState.NEEDS_RETRIEVAL:
                await self._executor.execute_retrieval(context, trace)
                current_state = self._router.route_after_retrieval(
                    context.intent_result,
                    context.retrieval_result,
                )
            
            elif current_state == WorkflowState.NEEDS_RECOMMENDATION:
                self._executor.execute_recommendation(context, trace)
                current_state = WorkflowState.GENERATING_RESPONSE
            
            elif current_state == WorkflowState.NEEDS_COMPARISON:
                self._executor.execute_comparison(context, trace)
                current_state = WorkflowState.GENERATING_RESPONSE
            
            elif current_state == WorkflowState.NEEDS_CLARIFICATION:
                current_state = WorkflowState.GENERATING_RESPONSE
            
            elif current_state == WorkflowState.GENERATING_RESPONSE:
                current_state = WorkflowState.COMPLETED
            
            elif current_state == WorkflowState.BLOCKED:
                # Blocked by guardrails
                break
            
            else:
                # Unknown state - fail safely
                logger.error(f"Unknown workflow state: {current_state}")
                current_state = WorkflowState.FAILED
                break
    
    def _build_response(self, context: ExecutionContext) -> str:
        """Build final response based on execution results."""
        # Check if blocked
        if context.guardrail_input_result and context.guardrail_input_result.should_block():
            return self._response_builder.build_refusal_response(context)
        
        # Check intent
        if not context.intent_result:
            return self._response_builder.build_clarification_response(context)
        
        intent = context.intent_result.primary_intent
        
        # Greeting
        if intent == IntentType.GREETING:
            return self._response_builder.build_greeting_response()
        
        # Recommendation
        if intent == IntentType.RECOMMENDATION and context.recommendation_result:
            return self._response_builder.build_recommendation_response(context)
        
        # Comparison
        if intent == IntentType.COMPARISON and context.comparison_result:
            return self._response_builder.build_comparison_response(context)
        
        # Clarification needed
        if intent == IntentType.CLARIFICATION:
            return self._response_builder.build_clarification_response(context)
        
        # Completion
        if intent == IntentType.COMPLETION:
            return "You're welcome! Let me know if you need help with anything else."
        
        # Default: clarification
        return self._response_builder.build_clarification_response(context)
    
    def _create_result(
        self,
        context: ExecutionContext,
        trace: ExecutionTrace,
        success: bool,
    ) -> OrchestrationResult:
        """Create orchestration result."""
        # Calculate stage durations
        stage_durations = {
            stage_trace.stage.value: stage_trace.duration_ms
            for stage_trace in trace.stages
        }
        
        statistics = OrchestrationStatistics(
            total_duration_ms=trace.total_duration_ms,
            state_reconstruction_ms=stage_durations.get("state_reconstruction", 0.0),
            intent_detection_ms=stage_durations.get("intent_detection", 0.0),
            guardrails_input_ms=stage_durations.get("guardrails_input", 0.0),
            retrieval_ms=stage_durations.get("retrieval", 0.0),
            recommendation_ms=stage_durations.get("recommendation", 0.0),
            comparison_ms=stage_durations.get("comparison", 0.0),
            stages_executed=trace.stages_completed,
            stages_skipped=trace.stages_skipped,
            stages_failed=trace.stages_failed,
        )
        
        return OrchestrationResult(
            response=context.final_response,
            success=success,
            execution_trace=trace,
            statistics=statistics,
            conversation_state=context.conversation_state,
            intent_result=context.intent_result,
            guardrail_input_result=context.guardrail_input_result,
            retrieval_result=context.retrieval_result,
            recommendation_result=context.recommendation_result,
            comparison_result=context.comparison_result,
            session_id=context.session_id,
        )
