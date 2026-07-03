"""
Pipeline executor.

Executes individual pipeline stages.
"""

import asyncio
from typing import Any, Optional
from src.orchestrator.domain.execution_context import ExecutionContext
from src.orchestrator.domain.execution_trace import ExecutionTrace
from src.orchestrator.domain.pipeline_stage import PipelineStage
from src.orchestrator.execution.error_handler import ErrorHandler, ExecutionError
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class PipelineExecutor:
    """
    Execute pipeline stages.
    
    Responsibilities:
    - Execute individual stages
    - Handle errors gracefully
    - Track execution metrics
    - Update execution context
    
    Design:
    - Delegate to components
    - No business logic
    - Error recovery
    - Metrics collection
    """
    
    def __init__(
        self,
        state_engine: Any,
        intent_engine: Any,
        guardrails_engine: Any,
        retrieval_pipeline: Any,
        recommendation_engine: Any,
        comparison_engine: Any,
        error_handler: ErrorHandler,
    ) -> None:
        """
        Initialize executor.
        
        Args:
            state_engine: Conversation state engine
            intent_engine: Intent detection engine
            guardrails_engine: Guardrails engine
            retrieval_pipeline: Retrieval pipeline
            recommendation_engine: Recommendation engine
            comparison_engine: Comparison engine
            error_handler: Error handler
        """
        self._state_engine = state_engine
        self._intent_engine = intent_engine
        self._guardrails = guardrails_engine
        self._retrieval = retrieval_pipeline
        self._recommendation = recommendation_engine
        self._comparison = comparison_engine
        self._error_handler = error_handler
    
    def execute_state_reconstruction(
        self,
        context: ExecutionContext,
        trace: ExecutionTrace,
    ) -> None:
        """
        Execute state reconstruction.
        
        Args:
            context: Execution context
            trace: Execution trace
        """
        stage = PipelineStage.STATE_RECONSTRUCTION
        trace.start_stage(stage)
        
        try:
            # Reconstruct conversation state
            state = self._state_engine.reconstruct_state(
                context.conversation_history
            )
            context.conversation_state = state
            
            trace.complete_stage(stage, {
                "status": state.status.value if hasattr(state, 'status') else "unknown",
            })
            
            logger.info("State reconstruction completed")
            
        except Exception as e:
            trace.fail_stage(stage, str(e))
            raise ExecutionError(
                f"State reconstruction failed: {e}",
                stage="state_reconstruction",
                recoverable=False,
            )
    
    def execute_intent_detection(
        self,
        context: ExecutionContext,
        trace: ExecutionTrace,
    ) -> None:
        """
        Execute intent detection.
        
        Args:
            context: Execution context
            trace: Execution trace
        """
        stage = PipelineStage.INTENT_DETECTION
        trace.start_stage(stage)
        
        try:
            # Detect intent
            intent = self._intent_engine.detect_intent(
                context.user_message,
                context.conversation_state,
            )
            context.intent_result = intent
            
            trace.complete_stage(stage, {
                "intent": intent.primary_intent.value,
                "confidence": intent.confidence_level.value,
            })
            
            logger.info(f"Intent detected: {intent.primary_intent.value}")
            
        except Exception as e:
            trace.fail_stage(stage, str(e))
            raise ExecutionError(
                f"Intent detection failed: {e}",
                stage="intent_detection",
                recoverable=True,
            )
    
    def execute_guardrails_input(
        self,
        context: ExecutionContext,
        trace: ExecutionTrace,
    ) -> None:
        """
        Execute input guardrails.
        
        Args:
            context: Execution context
            trace: Execution trace
        """
        stage = PipelineStage.GUARDRAILS_INPUT
        trace.start_stage(stage)
        
        try:
            # Validate input
            result = self._guardrails.validate_input(context.user_message)
            context.guardrail_input_result = result
            
            trace.complete_stage(stage, {
                "allow_processing": result.allow_processing,
                "violation_type": result.violation_type.value,
                "risk_level": result.risk_level.value,
            })
            
            if result.should_block():
                logger.warning("Input blocked by guardrails")
            
        except Exception as e:
            trace.fail_stage(stage, str(e))
            # Guardrails failure is critical
            raise ExecutionError(
                f"Guardrails check failed: {e}",
                stage="guardrails",
                recoverable=False,
            )
    
    async def execute_retrieval(
        self,
        context: ExecutionContext,
        trace: ExecutionTrace,
    ) -> None:
        """
        Execute retrieval pipeline.
        
        Args:
            context: Execution context
            trace: Execution trace
        """
        stage = PipelineStage.RETRIEVAL
        trace.start_stage(stage)
        
        try:
            # Execute retrieval
            result = await self._retrieval.execute(
                context.conversation_state,
                context.intent_result,
            )
            context.retrieval_result = result
            
            trace.complete_stage(stage, {
                "documents_retrieved": len(result.ranked_documents),
                "assessments_found": result.statistics.assessments_final if hasattr(result, 'statistics') else 0,
            })
            
            logger.info(f"Retrieved {len(result.ranked_documents)} documents")
            
        except Exception as e:
            trace.fail_stage(stage, str(e))
            raise ExecutionError(
                f"Retrieval failed: {e}",
                stage="retrieval",
                recoverable=True,
            )
    
    def execute_recommendation(
        self,
        context: ExecutionContext,
        trace: ExecutionTrace,
    ) -> None:
        """
        Execute recommendation engine.
        
        Args:
            context: Execution context
            trace: Execution trace
        """
        stage = PipelineStage.RECOMMENDATION
        trace.start_stage(stage)
        
        try:
            # Generate recommendations
            result = self._recommendation.generate_recommendations(
                context.retrieval_result,
                context.conversation_state,
                context.intent_result,
            )
            context.recommendation_result = result
            
            trace.complete_stage(stage, {
                "recommendations_count": len(result.recommendations),
                "confidence": result.confidence,
            })
            
            logger.info(f"Generated {len(result.recommendations)} recommendations")
            
        except Exception as e:
            trace.fail_stage(stage, str(e))
            raise ExecutionError(
                f"Recommendation failed: {e}",
                stage="recommendation",
                recoverable=True,
            )
    
    def execute_comparison(
        self,
        context: ExecutionContext,
        trace: ExecutionTrace,
    ) -> None:
        """
        Execute comparison engine.
        
        Args:
            context: Execution context
            trace: Execution trace
        """
        stage = PipelineStage.COMPARISON
        trace.start_stage(stage)
        
        try:
            # Compare assessments
            result = self._comparison.compare_assessments(
                context.user_message,
                context.retrieval_result,
                context.conversation_state,
                context.intent_result,
            )
            context.comparison_result = result
            
            if result:
                trace.complete_stage(stage, {
                    "assessment_a": result.assessment_a.assessment_name,
                    "assessment_b": result.assessment_b.assessment_name,
                    "confidence": result.confidence.value,
                })
                logger.info("Comparison completed")
            else:
                trace.complete_stage(stage, {"status": "no_comparison"})
                logger.warning("Comparison returned no result")
            
        except Exception as e:
            trace.fail_stage(stage, str(e))
            raise ExecutionError(
                f"Comparison failed: {e}",
                stage="comparison",
                recoverable=True,
            )
