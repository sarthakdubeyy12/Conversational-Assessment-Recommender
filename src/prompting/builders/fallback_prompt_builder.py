"""
Fallback prompt builder.

Builds prompts for generating fallback responses when errors occur,
retrieval fails, or system cannot process the request normally.
"""

from typing import Optional


class FallbackPromptBuilder:
    """
    Builds fallback prompts for error/failure scenarios.
    
    Responsibilities:
    - Generate graceful fallback responses
    - Maintain user trust during errors
    - Provide actionable next steps
    
    Design:
    - Never exposes technical errors
    - Maintains professional tone
    - Guides user toward recovery
    """
    
    def build(
        self,
        user_message: str,
        failure_type: str,
        context: Optional[str] = None,
    ) -> str:
        """
        Build fallback prompt.
        
        Args:
            user_message: Original user message
            failure_type: Type of failure (retrieval_failure, low_confidence, timeout, etc.)
            context: Optional context about the failure
        
        Returns:
            Fallback prompt string
        """
        if failure_type == "retrieval_failure":
            instruction = """**Situation:**
The retrieval system failed to find relevant assessments in the catalog.

**Your Task:**
Apologize for not finding matching assessments and ask the user to:
1. Rephrase their requirements more specifically
2. Provide different search terms
3. Describe the role and skills they want to assess

**Example Response:**
"I wasn't able to find assessments matching your exact criteria in our catalog. Could you provide more details about the role you're hiring for or the specific skills you want to assess? This will help me find better matches."

Keep it helpful and guide them toward a more specific request."""
        
        elif failure_type == "low_confidence":
            instruction = """**Situation:**
The system found results but with low confidence in their relevance.

**Your Task:**
Acknowledge the search and ask for clarification to improve results.

**Example Response:**
"I found some assessments, but I'd like to make sure I understand your needs correctly. Could you provide more details about the specific competencies or skills you're looking to evaluate?"

Be honest about uncertainty and ask for more information."""
        
        elif failure_type == "timeout" or failure_type == "provider_unavailable":
            instruction = """**Situation:**
A technical issue occurred (LLM timeout or provider unavailable).

**Your Task:**
Apologize for the delay and offer to try again.

**Example Response:**
"I'm experiencing a brief technical delay. Please try your request again, and I'll do my best to help you find the right assessment."

Never mention specific technical details like "LLM timeout" or "provider error"."""
        
        elif failure_type == "empty_catalog":
            instruction = """**Situation:**
The assessment catalog appears to be empty or unavailable.

**Your Task:**
Apologize and explain that recommendations are temporarily unavailable.

**Example Response:**
"I'm unable to access the assessment catalog at the moment. Please try again shortly, or contact support if the issue persists."

Be honest but maintain trust."""
        
        else:
            instruction = f"""**Situation:**
An unexpected issue occurred. Type: {failure_type}

**Your Task:**
Generate a generic, professional fallback response that:
1. Apologizes for the inconvenience
2. Offers to try again
3. Suggests rephrasing or providing more details
4. Does NOT mention technical errors

**Example Response:**
"I'm having trouble processing that request. Could you rephrase it or provide more specific details about the assessment you're looking for?"

Keep it brief and helpful."""
        
        prompt = f"""The user said: "{user_message}"

**Failure Type:** {failure_type}
{f'**Context:** {context}' if context else ''}

{instruction}

Generate an appropriate fallback response that is helpful and maintains user trust."""

        return prompt
