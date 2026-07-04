"""
Prompt service.

Main entry point for prompt engineering and LLM invocation.
Coordinates all prompt builders, optimization, and provider execution.
"""

from typing import Any, Optional, Dict
from src.prompting.builders.system_prompt_builder import SystemPromptBuilder
from src.prompting.builders.recommendation_prompt_builder import RecommendationPromptBuilder
from src.prompting.builders.comparison_prompt_builder import ComparisonPromptBuilder
from src.prompting.builders.clarification_prompt_builder import ClarificationPromptBuilder
from src.prompting.builders.refusal_prompt_builder import RefusalPromptBuilder
from src.prompting.builders.fallback_prompt_builder import FallbackPromptBuilder
from src.prompting.optimization.token_estimator import TokenEstimator
from src.prompting.providers.provider_factory import ProviderFactory
from src.prompting.models.prompt_package import PromptPackage
from src.prompting.models.provider_response import ProviderResponse
from src.conversation.intent.domain.intent_types import IntentType
from src.shared.config.settings import get_settings
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class PromptService:
    """
    Prompt Engineering & LLM Integration Service.
    
    Central service for:
    - Building prompts from structured data
    - Estimating and optimizing tokens
    - Invoking LLM providers
    - Parsing responses
    
    Design:
    - Delegates to specialized builders
    - Provider-agnostic
    - Optimizes token usage
    - Handles retries and fallbacks
    
    DOES NOT:
    - Perform business logic
    - Make recommendations
    - Detect intents
    - Run guardrails
    """
    
    def __init__(
        self,
        catalog_count: Optional[int] = None,
    ) -> None:
        """
        Initialize prompt service.
        
        Args:
            catalog_count: Number of assessments in catalog
        """
        self._settings = get_settings()
        
        # Initialize builders
        self._system_builder = SystemPromptBuilder(catalog_count=catalog_count)
        self._recommendation_builder = RecommendationPromptBuilder()
        self._comparison_builder = ComparisonPromptBuilder()
        self._clarification_builder = ClarificationPromptBuilder()
        self._refusal_builder = RefusalPromptBuilder()
        self._fallback_builder = FallbackPromptBuilder()
        
        # Initialize optimizer
        self._token_estimator = TokenEstimator()
        
        # Initialize provider
        self._provider = ProviderFactory.create_provider()
        
        logger.info("PromptService initialized")
    
    async def generate_response(
        self,
        orchestration_result: Any,
    ) -> str:
        """
        Generate natural language response from orchestration result.
        
        This is the main entry point for response generation.
        
        Args:
            orchestration_result: Result from conversation orchestrator
        
        Returns:
            Natural language response string
        """
        try:
            # Build prompt package based on result type
            prompt_package = self._build_prompt_package(orchestration_result)
            
            # Invoke LLM provider
            provider_response = await self._provider.generate(prompt_package)
            
            # Log metrics
            logger.info(
                f"LLM generation: {provider_response.provider}, "
                f"{provider_response.latency_ms:.0f}ms, "
                f"{provider_response.total_tokens} tokens"
            )
            
            # Return content or fallback
            if provider_response.success and provider_response.content:
                return provider_response.content
            else:
                logger.error(f"LLM generation failed: {provider_response.error}")
                return self._get_fallback_response(orchestration_result)
                
        except Exception as e:
            logger.error(f"Prompt service error: {e}", exc_info=True)
            return "I apologize, but I'm having trouble generating a response. Please try again."
    
    def _build_prompt_package(
        self,
        orchestration_result: Any,
    ) -> PromptPackage:
        """Build prompt package from orchestration result."""
        # Build system prompt (same for all)
        system_prompt = self._system_builder.build()
        
        # Determine prompt type and build user prompt
        prompt_type, user_prompt = self._build_user_prompt(orchestration_result)
        
        # Estimate tokens
        input_tokens, output_tokens = self._token_estimator.estimate_prompt_package_tokens(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
        
        # Create package
        package = PromptPackage(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            prompt_type=prompt_type,
            estimated_input_tokens=input_tokens,
            estimated_output_tokens=output_tokens,
            temperature=self._settings.llm_temperature,
            max_tokens=min(
                self._settings.llm_max_tokens,
                self._token_estimator.get_max_output_tokens(
                    input_tokens,
                    self._provider.get_provider_name(),
                    self._provider.get_model(),
                ),
            ),
        )
        
        logger.debug(f"Built prompt package: {package.to_dict()}")
        return package
    
    def _build_user_prompt(
        self,
        result: Any,
    ) -> tuple:
        """
        Build user prompt based on orchestration result.
        
        Returns:
            Tuple of (prompt_type, user_prompt)
        """
        # Get user message from execution context (if available)
        user_message = ""
        hiring_context = None
        
        if hasattr(result, 'conversation_state') and result.conversation_state:
            if hasattr(result.conversation_state, 'hiring_context'):
                hiring_context = result.conversation_state.hiring_context
        
        # Try to get original message
        if hasattr(result, 'execution_trace') and result.execution_trace:
            # Would need to store original message in trace - for now use fallback
            user_message = "User request"
        
        # Check if blocked by guardrails
        if result.guardrail_input_result and result.guardrail_input_result.should_block():
            violation_type = result.guardrail_input_result.violation_type or "unknown"
            refusal_reason = result.guardrail_input_result.refusal_message or "Request blocked"
            user_prompt = self._refusal_builder.build(
                user_message=user_message,
                refusal_reason=refusal_reason,
                violation_type=violation_type,
            )
            return "refusal", user_prompt
        
        # Check intent and route to appropriate builder
        if result.intent_result:
            intent = result.intent_result.primary_intent
            
            if intent == IntentType.RECOMMENDATION and result.recommendation_result:
                user_prompt = self._recommendation_builder.build(
                    user_message=user_message,
                    recommendation_result=result.recommendation_result,
                    hiring_context=hiring_context,
                )
                return "recommendation", user_prompt
            
            elif intent == IntentType.COMPARISON and result.comparison_result:
                user_prompt = self._comparison_builder.build(
                    user_message=user_message,
                    comparison_result=result.comparison_result,
                )
                return "comparison", user_prompt
            
            elif intent == IntentType.CLARIFICATION:
                user_prompt = self._clarification_builder.build(
                    user_message=user_message,
                    hiring_context=hiring_context,
                )
                return "clarification", user_prompt
        
        # Fallback
        user_prompt = self._fallback_builder.build(
            user_message=user_message,
            failure_type="unknown",
        )
        return "fallback", user_prompt
    
    def _get_fallback_response(self, result: Any) -> str:
        """Get simple fallback response when LLM fails."""
        # Check if blocked
        if result.guardrail_input_result and result.guardrail_input_result.should_block():
            return result.guardrail_input_result.refusal_message or "Request cannot be processed."
        
        # Generic fallback
        return "I apologize, but I'm having trouble generating a response. Please try rephrasing your request or providing more details about the assessment you're looking for."
