"""
Orchestrator dependency.

Provides configured orchestrator instance via dependency injection.
"""

import asyncio
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


async def _init_orchestrator_async() -> ConversationOrchestrator:
    """
    Initialize orchestrator with async operations.
    
    All dependencies are created and wired up here.
    
    Returns:
        Configured ConversationOrchestrator
    """
    settings = get_settings()
    
    logger.info("Creating orchestrator dependencies")
    
    # Embedding Provider
    embedding_provider = SentenceTransformerProvider(
        model_name=settings.embedding_model,
    )
    
    # Vector Store
    vector_store = ChromaVectorStore(
        persist_directory=settings.chroma_persist_directory,
        collection_name=settings.chroma_collection_name,
    )
    
    # Initialize the collection (connect to existing data)
    await vector_store.create_collection(
        name=settings.chroma_collection_name,
        dimension=embedding_provider.get_dimension()
    )
    
    # State Engine
    state_engine = ConversationStateEngine()
    
    # Intent Engine
    intent_engine = IntentEngine()
    
    # Guardrails Engine (without catalog_ids - not needed for operation)
    guardrails_engine = GuardrailsEngineFactory.create_production_engine(
        catalog_ids=[]
    )
    
    # Retrieval Pipeline
    retrieval_pipeline = PipelineFactory.create_production_pipeline(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )
    
    # Recommendation Engine
    recommendation_engine = RecommendationEngineFactory.create_production_engine()
    
    # Comparison Engine
    comparison_engine = ComparisonEngineFactory.create_production_engine()
    
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


def _init_orchestrator_sync() -> ConversationOrchestrator:
    """
    Synchronous wrapper for async orchestrator initialization.
    
    Uses asyncio.run() to execute async initialization.
    
    Returns:
        Configured ConversationOrchestrator
    """
    try:
        # Check if there's already an event loop running
        try:
            loop = asyncio.get_running_loop()
            # If we're already in an async context, create a task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, _init_orchestrator_async())
                return future.result()
        except RuntimeError:
            # No event loop running, safe to use asyncio.run()
            return asyncio.run(_init_orchestrator_async())
    except Exception as e:
        logger.error(f"Failed to create orchestrator: {e}", exc_info=True)
        raise RuntimeError(f"Failed to initialize orchestrator: {e}")


@lru_cache
def get_orchestrator() -> ConversationOrchestrator:
    """
    Get configured orchestrator instance.
    
    Uses lru_cache to ensure singleton pattern.
    
    Returns:
        Configured ConversationOrchestrator
    """
    return _init_orchestrator_sync()
