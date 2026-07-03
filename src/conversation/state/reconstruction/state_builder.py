"""
State builder.

Builds conversation state from messages.
"""

from typing import List
from datetime import datetime

from src.conversation.domain.entities import Message
from src.conversation.state.domain.conversation_state import (
    ConversationState,
    ConversationStatus,
    StateMetadata,
)
from src.conversation.state.extraction.requirement_extractor import RequirementExtractor
from src.conversation.state.extraction.correction_handler import CorrectionHandler
from src.conversation.state.inference.context_inferrer import ContextInferrer
from src.conversation.state.validation.state_validator import StateValidator
from src.conversation.state.validation.conflict_detector import ConflictDetector
from src.conversation.state.validation.completeness_checker import CompletenessChecker
from src.shared.logging.logger import get_logger
from src.shared.utils.timing import Stopwatch

logger = get_logger(__name__)


class StateBuilder:
    """
    Builds conversation state from message history.
    
    Orchestrates the complete state reconstruction pipeline:
    1. Extract requirements from messages
    2. Detect and apply corrections
    3. Infer missing context
    4. Validate state
    5. Detect conflicts
    6. Check completeness
    7. Determine conversation status
    
    Responsibilities:
    - Coordinate all state reconstruction components
    - Build complete ConversationState
    - Handle stateless reconstruction
    - Track metadata
    """
    
    def __init__(self) -> None:
        """Initialize builder with all components."""
        self._extractor = RequirementExtractor()
        self._correction_handler = CorrectionHandler()
        self._inferrer = ContextInferrer()
        self._validator = StateValidator()
        self._conflict_detector = ConflictDetector()
        self._completeness_checker = CompletenessChecker()
        
        logger.debug("StateBuilder initialized")
    
    def build_state(
        self,
        messages: List[Message],
    ) -> ConversationState:
        """
        Build complete conversation state from messages.
        
        This is the main entry point for stateless state reconstruction.
        
        Args:
            messages: Full conversation history
        
        Returns:
            Complete conversation state
        """
        timer = Stopwatch()
        timer.start()
        
        logger.info(f"Building state from {len(messages)} messages")
        
        # Step 1: Extract hiring context
        hiring_context = self._extractor.extract_from_messages(messages)
        
        # Step 2: Detect corrections
        corrections = self._correction_handler.detect_corrections(messages)
        if corrections:
            hiring_context = self._correction_handler.apply_corrections(
                hiring_context,
                corrections,
                messages,
            )
        
        # Step 3: Infer missing context
        hiring_context, inferred_fields = self._inferrer.infer_context(
            hiring_context
        )
        
        # Step 4: Check completeness
        missing_fields, completion = self._completeness_checker.check_completeness(
            hiring_context
        )
        
        # Step 5: Detect conflicts
        conflicts = self._conflict_detector.detect_conflicts(hiring_context)
        
        # Step 6: Build metadata
        metadata = StateMetadata(
            message_count=len(messages),
            inferred_fields=inferred_fields,
            explicit_fields=self._get_explicit_fields(hiring_context),
            missing_information=missing_fields,
            completion_percentage=completion,
            confidence_score=self._calculate_confidence(
                hiring_context,
                completion,
                conflicts,
            ),
            detected_conflicts=conflicts,
            clarification_history=corrections,
            last_updated=datetime.utcnow(),
        )
        
        # Step 7: Create state
        state = ConversationState(
            hiring_context=hiring_context,
            metadata=metadata,
            status=self._determine_status(
                hiring_context,
                completion,
                missing_fields,
                conflicts,
            ),
        )
        
        # Step 8: Validate
        is_valid, validation_errors = self._validator.validate(state)
        state.is_valid = is_valid
        state.validation_errors = validation_errors
        
        elapsed = timer.elapsed()
        
        logger.info(
            f"State built: status={state.status.value}, "
            f"completion={completion:.1%}, "
            f"conflicts={len(conflicts)}, "
            f"time={elapsed:.3f}s"
        )
        
        return state
    
    def _get_explicit_fields(self, context) -> set:
        """Get fields that were explicitly provided."""
        explicit = set()
        
        if context.role_title:
            explicit.add("role_title")
        if context.seniority:
            explicit.add("seniority")
        if context.years_of_experience is not None:
            explicit.add("years_of_experience")
        if context.required_skills:
            explicit.add("required_skills")
        if context.technical_skills:
            explicit.add("technical_skills")
        
        return explicit
    
    def _calculate_confidence(
        self,
        context,
        completion: float,
        conflicts: List[str],
    ) -> float:
        """Calculate confidence score."""
        # Start with completion percentage
        confidence = completion
        
        # Penalize for conflicts
        conflict_penalty = len(conflicts) * 0.1
        confidence = max(0.0, confidence - conflict_penalty)
        
        # Bonus for having critical fields
        if context.role_title:
            confidence = min(1.0, confidence + 0.1)
        
        return round(confidence, 2)
    
    def _determine_status(
        self,
        context,
        completion: float,
        missing: List[str],
        conflicts: List[str],
    ) -> ConversationStatus:
        """Determine conversation status."""
        # Initial state
        if not context.role_title:
            return ConversationStatus.INITIAL
        
        # Conflicts need clarification
        if conflicts:
            return ConversationStatus.CLARIFICATION_REQUIRED
        
        # Ready for recommendations
        if completion >= 0.6 and len(missing) <= 2:
            return ConversationStatus.READY_FOR_RECOMMENDATION
        
        # Ready for retrieval (minimum info)
        if completion >= 0.4:
            return ConversationStatus.READY_FOR_RETRIEVAL
        
        # Still gathering information
        return ConversationStatus.GATHERING_INFORMATION
