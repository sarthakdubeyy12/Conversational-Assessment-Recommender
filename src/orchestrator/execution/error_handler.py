"""
Error handler.

Provides graceful error handling and fallback responses.
"""

from typing import Optional
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ExecutionError(Exception):
    """Base execution error."""
    
    def __init__(self, message: str, stage: str, recoverable: bool = True):
        """
        Initialize error.
        
        Args:
            message: Error message
            stage: Stage where error occurred
            recoverable: Whether execution can continue
        """
        super().__init__(message)
        self.message = message
        self.stage = stage
        self.recoverable = recoverable


class ErrorHandler:
    """
    Handle execution errors gracefully.
    
    Responsibilities:
    - Catch and classify errors
    - Generate fallback responses
    - Determine if recovery is possible
    
    Design:
    - Fail gracefully
    - User-friendly messages
    - Preserve debugging info
    """
    
    def __init__(self) -> None:
        """Initialize error handler."""
        # Fallback messages
        self._fallback_messages = {
            "state_reconstruction": (
                "I'm having trouble understanding the conversation context. "
                "Could you rephrase your request?"
            ),
            "intent_detection": (
                "I'm not sure what you're asking for. "
                "Could you clarify whether you need assessment recommendations or comparisons?"
            ),
            "retrieval": (
                "I'm having trouble accessing the assessment catalog. "
                "Please try again in a moment."
            ),
            "recommendation": (
                "I couldn't generate recommendations based on your requirements. "
                "Could you provide more details about the role you're hiring for?"
            ),
            "comparison": (
                "I couldn't compare those assessments. "
                "Could you specify which assessments you'd like to compare?"
            ),
            "llm": (
                "I'm experiencing technical difficulties generating a response. "
                "Please try rephrasing your question."
            ),
            "default": (
                "I encountered an unexpected error. "
                "Please try again or rephrase your question."
            ),
        }
    
    def handle_error(
        self,
        error: Exception,
        stage: str,
    ) -> tuple[bool, str]:
        """
        Handle execution error.
        
        Args:
            error: Exception that occurred
            stage: Stage where error occurred
        
        Returns:
            (is_recoverable, fallback_message)
        """
        logger.error(f"Error in {stage}: {error}", exc_info=True)
        
        # Check if it's our custom error
        if isinstance(error, ExecutionError):
            return error.recoverable, self._get_fallback_message(stage)
        
        # Generic error - try to recover
        return True, self._get_fallback_message(stage)
    
    def _get_fallback_message(self, stage: str) -> str:
        """Get fallback message for stage."""
        return self._fallback_messages.get(
            stage,
            self._fallback_messages["default"]
        )
    
    def should_continue(
        self,
        error: Exception,
        stage: str,
    ) -> bool:
        """
        Determine if pipeline should continue after error.
        
        Args:
            error: Exception that occurred
            stage: Stage where error occurred
        
        Returns:
            True if should continue with fallback
        """
        # Critical stages - cannot continue
        critical_stages = ["state_reconstruction", "guardrails"]
        
        if stage in critical_stages:
            return False
        
        # Check if error is recoverable
        if isinstance(error, ExecutionError):
            return error.recoverable
        
        # Default: try to continue
        return True
