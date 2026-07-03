"""
Completeness checker.

Determines what information is still needed.
"""

from typing import List
from src.conversation.state.domain.conversation_state import HiringContext
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class CompletenessChecker:
    """
    Checks conversation completeness.
    
    Responsibilities:
    - Identify missing information
    - Prioritize missing fields
    - Calculate completion percentage
    - Determine if ready for recommendations
    
    Design:
    - Weighted field importance
    - Progressive disclosure
    - Context-aware requirements
    """
    
    def __init__(self) -> None:
        """Initialize checker."""
        # Field weights (importance)
        self._field_weights = {
            "role_title": 10,
            "seniority": 5,
            "years_of_experience": 3,
            "required_skills": 5,
            "technical_skills": 4,
            "assessment_types_requested": 3,
            "leadership_required": 2,
            "cognitive_required": 2,
            "personality_required": 2,
            "industry": 2,
        }
    
    def check_completeness(
        self,
        context: HiringContext,
    ) -> tuple[List[str], float]:
        """
        Check context completeness.
        
        Args:
            context: Hiring context
        
        Returns:
            (List of missing fields, completion percentage)
        """
        missing = []
        total_weight = 0
        completed_weight = 0
        
        # Check each field
        for field, weight in self._field_weights.items():
            total_weight += weight
            
            value = getattr(context, field, None)
            
            if self._is_field_complete(value):
                completed_weight += weight
            else:
                missing.append(field)
        
        # Calculate completion percentage
        completion = completed_weight / total_weight if total_weight > 0 else 0.0
        
        # Prioritize missing fields by weight
        missing_prioritized = sorted(
            missing,
            key=lambda f: self._field_weights.get(f, 0),
            reverse=True,
        )
        
        logger.debug(
            f"Completeness: {completion:.1%}, "
            f"missing {len(missing_prioritized)} fields"
        )
        
        return missing_prioritized, completion
    
    def _is_field_complete(self, value: any) -> bool:
        """Check if field has a complete value."""
        if value is None:
            return False
        
        if isinstance(value, str):
            return len(value.strip()) > 0
        
        if isinstance(value, list):
            return len(value) > 0
        
        if isinstance(value, bool):
            return True
        
        return value is not None
    
    def get_next_required_field(
        self,
        missing_fields: List[str],
    ) -> str | None:
        """
        Get next field to ask about.
        
        Args:
            missing_fields: List of missing fields (prioritized)
        
        Returns:
            Next field to ask about
        """
        if not missing_fields:
            return None
        
        # Return highest priority missing field
        return missing_fields[0]
