"""
Conversation State Engine.

Main orchestrator for stateless state reconstruction.
"""

from typing import List
from src.conversation.domain.entities import Message
from src.conversation.state.domain.conversation_state import ConversationState
from src.conversation.state.reconstruction.state_builder import StateBuilder
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ConversationStateEngine:
    """
    Conversation State Engine.
    
    Single entry point for stateless conversation state reconstruction.
    
    Responsibilities:
    - Reconstruct complete state from messages
    - Provide consistent state interface
    - Hide implementation details
    - Enable future extensions
    
    Design:
    - Stateless (no server-side memory)
    - Deterministic (same messages → same state)
    - Pure function (no side effects)
    - Fast reconstruction (<100ms typical)
    
    Usage:
        engine = ConversationStateEngine()
        messages = [Message(role="user", content="Hiring Java developer")]
        state = engine.reconstruct_state(messages)
        
        # State contains:
        # - hiring_context (role, skills, requirements)
        # - status (conversation stage)
        # - metadata (completeness, conflicts, missing info)
        # - validation results
    """
    
    def __init__(self) -> None:
        """Initialize state engine."""
        self._builder = StateBuilder()
        logger.info("ConversationStateEngine initialized")
    
    def reconstruct_state(
        self,
        messages: List[Message],
    ) -> ConversationState:
        """
        Reconstruct conversation state from messages.
        
        This is the main API for state reconstruction.
        Called on every request with full conversation history.
        
        Args:
            messages: Full conversation history (user + assistant messages)
        
        Returns:
            Complete conversation state
        
        Examples:
            # Single message
            messages = [Message(role="user", content="Need senior Java developer")]
            state = engine.reconstruct_state(messages)
            assert state.hiring_context.role_title == "Senior Java Developer"
            assert state.hiring_context.seniority == "senior"
            
            # Multiple messages with corrections
            messages = [
                Message(role="user", content="Hiring Java developer"),
                Message(role="assistant", content="Great! ..."),
                Message(role="user", content="Actually, make that Python developer"),
            ]
            state = engine.reconstruct_state(messages)
            assert state.hiring_context.role_title == "Python Developer"
            
            # Ready for recommendations
            messages = [
                Message(role="user", content="Senior Backend Engineer, 5 years exp"),
                Message(role="assistant", content="What skills?"),
                Message(role="user", content="Python, Kubernetes, leadership"),
            ]
            state = engine.reconstruct_state(messages)
            assert state.status == ConversationStatus.READY_FOR_RECOMMENDATION
        """
        logger.debug(f"Reconstructing state from {len(messages)} messages")
        
        # Handle empty messages
        if not messages:
            return self._create_empty_state()
        
        # Build state from messages
        state = self._builder.build_state(messages)
        
        return state
    
    def _create_empty_state(self) -> ConversationState:
        """Create empty initial state."""
        return ConversationState()
