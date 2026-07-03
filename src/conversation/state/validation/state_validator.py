"""
State validator.

Validates conversation state quality and completeness.
"""

from typing import List, Tuple
from src.conversation.state.domain.conversation_state import (
    ConversationState,
    HiringContext,
)
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class StateValidator:
    """
    Validates conversation state.
    
    Responsibilities:
    - Check required fields
    - Validate field values
    - Detect invalid states
    - Generate validation errors
    
    Design:
    - Rule-based validation
    - Incremental validation
    - Clear error messages
    """
    
    def __init__(self) -> None:
        """Initialize validator."""
        self._critical_fields = [
            "role_title",
        ]
        
        self._important_fields = [
            "seniority",
            "years_of_experience",
            "required_skills",
            "technical_skills",
        ]
    
    def validate(
        self,
        state: ConversationState,
    ) -> Tuple[bool, List[str]]:
        """
        Validate conversation state.
        
        Args:
            state: Conversation state to validate
        
        Returns:
            (is_valid, list of errors)
        """
        errors = []
        
        # Validate hiring context
        context_errors = self._validate_context(state.hiring_context)
        errors.extend(context_errors)
        
        # Validate metadata
        metadata_errors = self._validate_metadata(state)
        errors.extend(metadata_errors)
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            logger.debug(f"Validation failed: {len(errors)} errors")
        
        return is_valid, errors
    
    def _validate_context(
        self,
        context: HiringContext,
    ) -> List[str]:
        """Validate hiring context."""
        errors = []
        
        # Check critical fields
        if not context.role_title:
            errors.append("Missing critical field: role_title")
        
        # Validate years of experience
        if context.years_of_experience is not None:
            if context.years_of_experience < 0:
                errors.append("Invalid years_of_experience: must be >= 0")
            if context.years_of_experience > 50:
                errors.append("Invalid years_of_experience: seems too high")
        
        # Validate seniority
        if context.seniority:
            valid_levels = ["junior", "mid", "senior", "executive"]
            if context.seniority not in valid_levels:
                errors.append(
                    f"Invalid seniority: {context.seniority} "
                    f"(must be one of {valid_levels})"
                )
        
        return errors
    
    def _validate_metadata(
        self,
        state: ConversationState,
    ) -> List[str]:
        """Validate state metadata."""
        errors = []
        
        # Check confidence score
        if state.metadata.confidence_score < 0 or state.metadata.confidence_score > 1:
            errors.append("Invalid confidence_score: must be between 0 and 1")
        
        # Check completion percentage
        if (state.metadata.completion_percentage < 0
            or state.metadata.completion_percentage > 1):
            errors.append("Invalid completion_percentage: must be between 0 and 1")
        
        return errors
