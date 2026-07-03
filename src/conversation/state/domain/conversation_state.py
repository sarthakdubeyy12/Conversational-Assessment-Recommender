"""
Conversation State entity.

Represents the complete reconstructed hiring context from conversation history.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from enum import Enum


class ConversationStatus(str, Enum):
    """Conversation stage."""
    INITIAL = "initial"
    GATHERING_INFORMATION = "gathering_information"
    CLARIFICATION_REQUIRED = "clarification_required"
    READY_FOR_RETRIEVAL = "ready_for_retrieval"
    READY_FOR_RECOMMENDATION = "ready_for_recommendation"
    REFINEMENT = "refinement"
    COMPARISON = "comparison"
    COMPLETED = "completed"


@dataclass
class HiringContext:
    """
    Hiring requirement context.
    
    Contains all extracted and inferred information about the hiring need.
    """
    
    # Core requirements
    role_title: Optional[str] = None
    seniority: Optional[str] = None
    years_of_experience: Optional[int] = None
    industry: Optional[str] = None
    employment_type: Optional[str] = None
    
    # Skills
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    technical_skills: List[str] = field(default_factory=list)
    soft_skills: List[str] = field(default_factory=list)
    
    # Assessment preferences
    assessment_types_requested: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    remote_requirement: Optional[bool] = None
    
    # Specific requirements
    leadership_required: Optional[bool] = None
    personality_required: Optional[bool] = None
    cognitive_required: Optional[bool] = None
    coding_required: Optional[bool] = None
    
    # Constraints
    must_have: List[str] = field(default_factory=list)
    nice_to_have: List[str] = field(default_factory=list)
    
    # Free-form
    job_description: Optional[str] = None
    user_goals: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "role_title": self.role_title,
            "seniority": self.seniority,
            "years_of_experience": self.years_of_experience,
            "industry": self.industry,
            "employment_type": self.employment_type,
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "technical_skills": self.technical_skills,
            "soft_skills": self.soft_skills,
            "assessment_types_requested": self.assessment_types_requested,
            "languages": self.languages,
            "remote_requirement": self.remote_requirement,
            "leadership_required": self.leadership_required,
            "personality_required": self.personality_required,
            "cognitive_required": self.cognitive_required,
            "coding_required": self.coding_required,
            "must_have": self.must_have,
            "nice_to_have": self.nice_to_have,
            "job_description": self.job_description,
            "user_goals": self.user_goals,
        }


@dataclass
class StateMetadata:
    """
    State metadata for tracking and validation.
    """
    
    # Tracking
    conversation_id: Optional[str] = None
    message_count: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    # Inference tracking
    inferred_fields: Set[str] = field(default_factory=set)
    explicit_fields: Set[str] = field(default_factory=set)
    
    # Quality metrics
    confidence_score: float = 0.0
    completion_percentage: float = 0.0
    
    # Missing information
    missing_information: List[str] = field(default_factory=list)
    
    # Corrections history
    clarification_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Conflicts
    detected_conflicts: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "conversation_id": self.conversation_id,
            "message_count": self.message_count,
            "last_updated": self.last_updated.isoformat(),
            "inferred_fields": list(self.inferred_fields),
            "explicit_fields": list(self.explicit_fields),
            "confidence_score": self.confidence_score,
            "completion_percentage": self.completion_percentage,
            "missing_information": self.missing_information,
            "clarification_history": self.clarification_history,
            "detected_conflicts": self.detected_conflicts,
        }


@dataclass
class ConversationState:
    """
    Complete conversation state.
    
    Single source of truth for all downstream modules.
    Reconstructed entirely from conversation history (stateless).
    """
    
    # Core context
    hiring_context: HiringContext = field(default_factory=HiringContext)
    
    # Status
    status: ConversationStatus = ConversationStatus.INITIAL
    
    # Metadata
    metadata: StateMetadata = field(default_factory=StateMetadata)
    
    # Validation results
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "hiring_context": self.hiring_context.to_dict(),
            "status": self.status.value,
            "metadata": self.metadata.to_dict(),
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors,
        }
    
    def is_ready_for_recommendation(self) -> bool:
        """Check if state has sufficient information for recommendations."""
        return (
            self.hiring_context.role_title is not None
            and len(self.metadata.missing_information) <= 2
            and self.metadata.completion_percentage >= 0.6
        )
    
    def needs_clarification(self) -> bool:
        """Check if clarification is needed."""
        return (
            len(self.metadata.missing_information) > 0
            or len(self.metadata.detected_conflicts) > 0
        )
    
    def get_missing_fields(self) -> List[str]:
        """Get list of missing critical fields."""
        return self.metadata.missing_information
    
    def get_conflicts(self) -> List[str]:
        """Get list of detected conflicts."""
        return self.metadata.detected_conflicts
