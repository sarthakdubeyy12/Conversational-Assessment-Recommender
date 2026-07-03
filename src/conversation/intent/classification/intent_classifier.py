"""
Intent classifier.

Main classification engine using multi-stage pipeline.
"""

import re
from typing import List
from src.conversation.state.domain.conversation_state import ConversationState, ConversationStatus
from src.conversation.intent.domain.intent_types import IntentType, ConfidenceLevel, RoutingTarget
from src.conversation.intent.domain.intent_result import IntentResult
from src.conversation.intent.detection.pattern_matcher import PatternMatcher
from src.conversation.intent.detection.guardrails.prompt_injection_detector import PromptInjectionDetector
from src.conversation.intent.detection.guardrails.refusal_detector import RefusalDetector
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class IntentClassifier:
    """
    Multi-stage intent classifier.
    
    Pipeline:
    1. Guardrails (prompt injection, refusal)
    2. Simple patterns (greeting, completion)
    3. Conversation state analysis
    4. Pattern matching (comparison, refinement)
    5. Default fallback
    
    Responsibilities:
    - Classify user intent
    - Generate confidence scores
    - Provide classification reasoning
    
    Design:
    - Deterministic classification
    - State-aware decisions
    - Security-first (guardrails first)
    - Clear decision trail
    """
    
    def __init__(self) -> None:
        """Initialize classifier with detectors."""
        self._pattern_matcher = PatternMatcher()
        self._injection_detector = PromptInjectionDetector()
        self._refusal_detector = RefusalDetector()
        
        logger.debug("IntentClassifier initialized")
    
    def classify(
        self,
        user_message: str,
        conversation_state: ConversationState,
    ) -> IntentResult:
        """
        Classify user intent.
        
        Args:
            user_message: Latest user message
            conversation_state: Current conversation state
        
        Returns:
            IntentResult with classification
        """
        logger.debug(f"Classifying message: '{user_message[:50]}'...")
        
        # Stage 1: Guardrails (highest priority)
        result = self._check_guardrails(user_message)
        if result:
            return result
        
        # Stage 2: Simple patterns
        result = self._check_simple_patterns(user_message)
        if result:
            return result
        
        # Stage 3: Pattern-based classification (before state)
        result = self._check_patterns(user_message)
        if result:
            return result
        
        # Stage 4: State-based classification (fallback)
        result = self._check_state_based(user_message, conversation_state)
        if result:
            return result
        
        # Stage 5: Fallback
        return self._create_unknown_result(user_message)
    
    def _check_guardrails(self, text: str) -> IntentResult | None:
        """Check security guardrails."""
        # Check prompt injection
        is_injection, patterns, confidence = self._injection_detector.detect(text)
        if is_injection:
            logger.warning(f"Prompt injection detected: {patterns}")
            return IntentResult(
                primary_intent=IntentType.PROMPT_INJECTION,
                confidence_level=ConfidenceLevel.HIGH,
                confidence_score=confidence,
                routing_target=RoutingTarget.GUARDRAILS,
                requires_guardrails=True,
                matched_patterns=patterns,
                decision_reason="Prompt injection attempt detected",
            )
        
        # Check refusal
        is_off_topic, keywords, confidence = self._refusal_detector.detect(text)
        if is_off_topic:
            logger.info(f"Off-topic request detected: {keywords}")
            return IntentResult(
                primary_intent=IntentType.REFUSAL,
                confidence_level=ConfidenceLevel.HIGH,
                confidence_score=confidence,
                routing_target=RoutingTarget.GUARDRAILS,
                requires_guardrails=True,
                matched_keywords=keywords,
                decision_reason="Request outside project scope",
            )
        
        return None
    
    def _check_simple_patterns(self, text: str) -> IntentResult | None:
        """Check simple patterns (greeting, completion)."""
        # Greeting
        is_greeting, patterns = self._pattern_matcher.match_greeting(text)
        if is_greeting:
            return IntentResult(
                primary_intent=IntentType.GREETING,
                confidence_level=ConfidenceLevel.HIGH,
                confidence_score=0.95,
                routing_target=RoutingTarget.RESPONSE_FORMATTER,
                matched_patterns=patterns,
                decision_reason="Greeting detected",
            )
        
        # Completion
        is_completion, patterns = self._pattern_matcher.match_completion(text)
        if is_completion:
            return IntentResult(
                primary_intent=IntentType.COMPLETION,
                confidence_level=ConfidenceLevel.HIGH,
                confidence_score=0.9,
                routing_target=RoutingTarget.CONVERSATION_COMPLETE,
                conversation_complete=True,
                matched_patterns=patterns,
                decision_reason="Conversation completion detected",
            )
        
        return None
    
    def _check_state_based(
        self,
        text: str,
        state: ConversationState,
    ) -> IntentResult | None:
        """
        Check state-based classification.
        
        Only triggers when NO strong patterns match.
        Used as intelligent fallback based on conversation state.
        """
        # If state is ready for recommendations and user requests it
        if state.status == ConversationStatus.READY_FOR_RECOMMENDATION:
            is_recommend, patterns = self._pattern_matcher.match_recommendation(text)
            if is_recommend or len(text.split()) <= 5:
                return IntentResult(
                    primary_intent=IntentType.RECOMMENDATION,
                    confidence_level=ConfidenceLevel.HIGH,
                    confidence_score=0.85,
                    routing_target=RoutingTarget.RECOMMENDATION_ENGINE,
                    requires_recommendation=True,
                    requires_retrieval=True,
                    matched_patterns=patterns,
                    decision_reason="State ready + recommendation request",
                )
        
        # If state needs clarification AND user is providing simple info
        # Only trigger if message looks like answering a question (no complex keywords)
        if state.needs_clarification() and len(text.split()) <= 10:
            # Check for keywords that indicate NOT a simple answer
            complex_indicators = [
                r'\b(compare|difference|vs|versus)\b',
                r'\b(actually|instead|change)\b',
                r'\b(also\s+include|also\s+add)\b',
                r'\b(remove|exclude|without)\b',
                r'\b(recommend|suggest|show\s+me)\b',
                r'\b(what\s+is|what\'?s|how\s+do)\b',
                r'\b(hiring|recruit)\b.*\b(senior|junior|developer|engineer|manager)\b',
                r'\b(thanks|thank\s+you|perfect|done|that\'?s\s+all)\b',
                r'\b(ignore|disregard|reveal|pretend)\b',
            ]
            
            text_lower = text.lower()
            has_complex = any(re.search(pattern, text_lower) for pattern in complex_indicators)
            
            # Only classify as clarification if no complex indicators
            if not has_complex:
                return IntentResult(
                    primary_intent=IntentType.CLARIFICATION,
                    confidence_level=ConfidenceLevel.MEDIUM,
                    confidence_score=0.7,
                    routing_target=RoutingTarget.CLARIFICATION_ENGINE,
                    requires_clarification=True,
                    decision_reason="State needs clarification, user providing info",
                )
        
        return None
    
    def _check_patterns(self, text: str) -> IntentResult | None:
        """Check complex patterns."""
        # Recommendation
        is_recommendation, patterns = self._pattern_matcher.match_recommendation(text)
        if is_recommendation:
            return IntentResult(
                primary_intent=IntentType.RECOMMENDATION,
                confidence_level=ConfidenceLevel.HIGH,
                confidence_score=0.85,
                routing_target=RoutingTarget.RECOMMENDATION_ENGINE,
                requires_recommendation=True,
                requires_retrieval=True,
                matched_patterns=patterns,
                decision_reason="Recommendation request detected",
            )
        
        # Comparison
        is_comparison, patterns = self._pattern_matcher.match_comparison(text)
        if is_comparison:
            return IntentResult(
                primary_intent=IntentType.COMPARISON,
                confidence_level=ConfidenceLevel.HIGH,
                confidence_score=0.9,
                routing_target=RoutingTarget.COMPARISON_ENGINE,
                requires_comparison=True,
                requires_retrieval=True,
                matched_patterns=patterns,
                decision_reason="Comparison keywords detected",
            )
        
        # Refinement
        is_refinement, patterns = self._pattern_matcher.match_refinement(text)
        if is_refinement:
            return IntentResult(
                primary_intent=IntentType.REFINEMENT,
                confidence_level=ConfidenceLevel.MEDIUM,
                confidence_score=0.75,
                routing_target=RoutingTarget.REFINEMENT_HANDLER,
                requires_refinement=True,
                matched_patterns=patterns,
                decision_reason="Refinement keywords detected",
            )
        
        return None
    
    def _create_unknown_result(self, text: str) -> IntentResult:
        """Create unknown intent result."""
        logger.debug("No intent matched, returning UNKNOWN")
        
        return IntentResult(
            primary_intent=IntentType.UNKNOWN,
            confidence_level=ConfidenceLevel.LOW,
            confidence_score=0.0,
            routing_target=RoutingTarget.CLARIFICATION_ENGINE,
            requires_clarification=True,
            decision_reason="No matching intent pattern found",
        )
