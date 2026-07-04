"""
Orchestrator dependency.

Provides configured orchestrator instance via dependency injection.
"""

from functools import lru_cache
from src.orchestrator.engine.conversation_orchestrator import ConversationOrchestrator
from src.orchestrator.engine.orchestrator_factory import OrchestratorFactory
from src.conversation.state.state_engine import ConversationStateEngine
from src.conversation.intent.intent_engine import IntentEngine
from src.guardrails.engine.engine_factory import GuardrailsEngineFactory
from src.retrieval.pipeline.pipeline_factory import PipelineFactory
from src.recommendation.engine.engine_factory import RecommendationEngineFactory
from src.comparison.engine.engine_factory import ComparisonEngineFactory
from src.knowledge_base.embeddings.provider import SentenceTransformerProvider
from src.knowledge_base.vector_store.chroma_client import ChromaVectorStore
from src.shared.config.settings import get_settings
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


@lru_cache
def get_orchestrator() -> ConversationOrchestrator:
    """
    Get configured orchestrator instance.
    
    Uses lru_cache to ensure singleton pattern.
    All dependencies are created and wired up here.
    
    Returns:
        Configured ConversationOrchestrator
    """
    settings = get_settings()
    
    logger.info("Creating orchestrator dependencies")
    
    try:
        # Vector Store
        vector_store = ChromaVectorStore(
            persist_directory=settings.chroma_persist_directory,
            collection_name=settings.chroma_collection_name,
        )
        
        # Embedding Provider
        embedding_provider = SentenceTransformerProvider(
            model_name=settings.embedding_model,
        )
        
        # State Engine
        state_engine = ConversationStateEngine()
        
        # Intent Engine
        intent_engine = IntentEngine()
        
        # Guardrails Engine
        guardrails_engine = GuardrailsEngineFactory.create_production_engine()
        
        # Retrieval Pipeline
        retrieval_pipeline = PipelineFactory.create_production_pipeline(
            knowledge_base=vector_store,
            embedding_provider=embedding_provider,
        )
        
        # Recommendation Engine
        recommendation_engine = RecommendationEngineFactory.create_production_engine(
            vector_store=vector_store,
            embedding_provider=embedding_provider,
        )
        
        # Comparison Engine
        comparison_engine = ComparisonEngineFactory.create_production_engine(
            vector_store=vector_store,
            embedding_provider=embedding_provider,
        )
        
        # Create orchestrator
        orchestrator = OrchestratorFactory.create_production_orchestrator(
            state_engine=state_engine,
            intent_engine=intent_engine,
            guardrails_engine=guardrails_engine,
            retrieval_pipeline=retrieval_pipeline,
            recommendation_engine=recommendation_engine,
            comparison_engine=comparison_engine,
        )
        
        logger.info("Orchestrator created successfully")
        return orchestrator
        
    except Exception as e:
        logger.error(f"Failed to create orchestrator: {e}", exc_info=True)
        raise RuntimeError(f"Failed to initialize orchestrator: {e}")
