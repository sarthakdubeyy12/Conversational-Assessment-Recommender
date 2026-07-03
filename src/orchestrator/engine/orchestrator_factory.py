"""
Orchestrator factory.

Creates configured orchestrator instances with all dependencies.
"""

from typing import List
from src.orchestrator.engine.conversation_orchestrator import ConversationOrchestrator
from src.orchestrator.workflow.decision_router import DecisionRouter
from src.orchestrator.execution.pipeline_executor import PipelineExecutor
from src.orchestrator.execution.error_handler import ErrorHandler
from src.orchestrator.response.response_builder import ResponseBuilder
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class OrchestratorFactory:
    """
    Factory for conversation orchestrator.
    
    Responsibilities:
    - Wire up all dependencies
    - Configure components
    - Provide production instances
    
    Design:
    - Dependency injection
    - Single point of creation
    - Configuration management
    """
    
    @staticmethod
    def create_production_orchestrator(
        state_engine: any,
        intent_engine: any,
        guardrails_engine: any,
        retrieval_pipeline: any,
        recommendation_engine: any,
        comparison_engine: any,
    ) -> ConversationOrchestrator:
        """
        Create production orchestrator.
        
        Args:
            state_engine: Conversation state engine
            intent_engine: Intent detection engine
            guardrails_engine: Guardrails engine
            retrieval_pipeline: Retrieval pipeline
            recommendation_engine: Recommendation engine
            comparison_engine: Comparison engine
        
        Returns:
            Configured conversation orchestrator
        """
        logger.info("Creating production conversation orchestrator")
        
        # Create error handler
        error_handler = ErrorHandler()
        
        # Create pipeline executor
        executor = PipelineExecutor(
            state_engine=state_engine,
            intent_engine=intent_engine,
            guardrails_engine=guardrails_engine,
            retrieval_pipeline=retrieval_pipeline,
            recommendation_engine=recommendation_engine,
            comparison_engine=comparison_engine,
            error_handler=error_handler,
        )
        
        # Create decision router
        router = DecisionRouter()
        
        # Create response builder
        response_builder = ResponseBuilder()
        
        # Assemble orchestrator
        orchestrator = ConversationOrchestrator(
            executor=executor,
            router=router,
            response_builder=response_builder,
            error_handler=error_handler,
        )
        
        logger.info("Production conversation orchestrator created")
        return orchestrator
