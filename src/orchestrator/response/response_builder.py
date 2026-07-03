"""
Response builder.

Assembles final responses from pipeline results.
"""

from typing import Optional
from src.orchestrator.domain.execution_context import ExecutionContext
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ResponseBuilder:
    """
    Build final responses.
    
    Responsibilities:
    - Format recommendation responses
    - Format comparison responses
    - Format clarification responses
    - Format refusal responses
    
    Design:
    - Simple formatting
    - User-friendly output
    - No business logic
    """
    
    def __init__(self) -> None:
        """Initialize builder."""
        pass
    
    def build_recommendation_response(
        self,
        context: ExecutionContext,
    ) -> str:
        """
        Build recommendation response.
        
        Args:
            context: Execution context with recommendation result
        
        Returns:
            Formatted response text
        """
        result = context.recommendation_result
        
        if not result or not result.recommendations:
            return (
                "I couldn't find suitable assessments based on your requirements. "
                "Could you provide more details about the role and skills you're looking for?"
            )
        
        # Build response
        lines = []
        lines.append(
            f"Based on your requirements, I recommend {len(result.recommendations)} "
            f"SHL assessment{'s' if len(result.recommendations) > 1 else ''}:\n"
        )
        
        for idx, rec in enumerate(result.recommendations[:5], 1):
            lines.append(f"\n{idx}. **{rec.assessment_name}**")
            lines.append(f"   - Category: {rec.category}")
            lines.append(f"   - Type: {rec.test_type}")
            if rec.matching_skills:
                lines.append(f"   - Measures: {', '.join(rec.matching_skills[:3])}")
            if rec.duration_minutes:
                lines.append(f"   - Duration: {rec.duration_minutes} minutes")
            lines.append(f"   - URL: {rec.official_url}")
            if rec.recommendation_reason:
                lines.append(f"   - Why: {rec.recommendation_reason}")
        
        if len(result.recommendations) > 5:
            lines.append(f"\n... and {len(result.recommendations) - 5} more assessments")
        
        return "\n".join(lines)
    
    def build_comparison_response(
        self,
        context: ExecutionContext,
    ) -> str:
        """
        Build comparison response.
        
        Args:
            context: Execution context with comparison result
        
        Returns:
            Formatted response text
        """
        result = context.comparison_result
        
        if not result:
            return (
                "I couldn't compare those assessments. "
                "Please specify which two assessments you'd like to compare."
            )
        
        # Build response
        lines = []
        lines.append(
            f"Here's a comparison of **{result.assessment_a.assessment_name}** "
            f"and **{result.assessment_b.assessment_name}**:\n"
        )
        
        # Similarities
        if result.similarities:
            lines.append("\n**Similarities:**")
            for sim in result.similarities[:5]:
                lines.append(f"- {sim}")
        
        # Differences
        if result.differences:
            lines.append("\n**Differences:**")
            for diff in result.differences[:5]:
                lines.append(f"- {diff}")
        
        # Unique strengths
        if result.unique_strengths_a:
            lines.append(f"\n**{result.assessment_a.assessment_name} strengths:**")
            for strength in result.unique_strengths_a[:3]:
                lines.append(f"- {strength}")
        
        if result.unique_strengths_b:
            lines.append(f"\n**{result.assessment_b.assessment_name} strengths:**")
            for strength in result.unique_strengths_b[:3]:
                lines.append(f"- {strength}")
        
        # URLs
        lines.append(f"\n**More Information:**")
        lines.append(f"- {result.assessment_a.assessment_name}: {result.assessment_a.official_url}")
        lines.append(f"- {result.assessment_b.assessment_name}: {result.assessment_b.official_url}")
        
        return "\n".join(lines)
    
    def build_clarification_response(
        self,
        context: ExecutionContext,
    ) -> str:
        """
        Build clarification request response.
        
        Args:
            context: Execution context
        
        Returns:
            Clarification message
        """
        state = context.conversation_state
        
        # Check what information is missing
        if state and hasattr(state, 'metadata'):
            missing = state.metadata.missing_information
            if missing:
                return (
                    f"To recommend the right assessments, I need more information. "
                    f"Could you tell me about: {', '.join(missing[:3])}?"
                )
        
        # Generic clarification
        return (
            "I'd like to help you find the right SHL assessments. "
            "Could you tell me more about the role you're hiring for and the skills you need to assess?"
        )
    
    def build_greeting_response(self) -> str:
        """Build greeting response."""
        return (
            "Hello! I'm here to help you find the right SHL assessments for your hiring needs. "
            "What role are you looking to fill, or which skills would you like to assess?"
        )
    
    def build_refusal_response(
        self,
        context: ExecutionContext,
    ) -> str:
        """
        Build refusal response.
        
        Args:
            context: Execution context with guardrail result
        
        Returns:
            Refusal message
        """
        if context.guardrail_input_result:
            return context.guardrail_input_result.refusal_reason
        
        return (
            "I can only help with SHL assessment recommendations. "
            "Please ask about assessments for your hiring needs."
        )
    
    def build_fallback_response(
        self,
        error_message: str,
    ) -> str:
        """
        Build fallback response for errors.
        
        Args:
            error_message: Error message from error handler
        
        Returns:
            User-friendly error message
        """
        return error_message
