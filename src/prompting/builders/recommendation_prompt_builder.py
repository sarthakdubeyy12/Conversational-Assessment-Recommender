"""
Recommendation prompt builder.

Builds prompts for generating natural language recommendation responses
based on structured recommendation results.
"""

from typing import Any, List, Dict, Optional


class RecommendationPromptBuilder:
    """
    Builds recommendation prompts from structured recommendation results.
    
    Responsibilities:
    - Convert RecommendationResult into LLM prompt
    - Include only retrieved assessment data
    - Format requirements and context
    - Ensure catalog grounding
    
    Design:
    - Uses structured data only
    - Never invents assessments
    - Clear formatting instructions
    """
    
    def build(
        self,
        user_message: str,
        recommendation_result: Any,
        hiring_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Build recommendation prompt.
        
        Args:
            user_message: Original user message
            recommendation_result: Structured recommendation result
            hiring_context: Optional hiring context from conversation state
        
        Returns:
            Recommendation prompt string
        """
        # Extract recommendations
        recommendations = recommendation_result.recommendations if recommendation_result else []
        
        if not recommendations:
            return self._build_no_recommendations_prompt(user_message, hiring_context)
        
        # Build assessment list
        assessment_details = []
        for idx, rec in enumerate(recommendations[:10], 1):  # Max 10
            assessment = rec.assessment
            explanation = rec.explanation
            
            detail = f"""
Assessment {idx}: {assessment.name}
- URL: {assessment.url}
- Category: {assessment.category}
- Description: {assessment.description}
- Competencies: {', '.join(assessment.competencies) if assessment.competencies else 'Not specified'}
- Skills: {', '.join(assessment.skills) if assessment.skills else 'Not specified'}
- Duration: {assessment.duration if assessment.duration else 'Not specified'}
- Languages: {', '.join(assessment.languages) if assessment.languages else 'Not specified'}
- Seniority Levels: {', '.join(assessment.seniority_levels) if assessment.seniority_levels else 'Not specified'}
- Recommendation Reason: {explanation}
"""
            assessment_details.append(detail.strip())
        
        # Build context section
        context_section = ""
        if hiring_context:
            context_parts = []
            if hiring_context.get("role_title"):
                context_parts.append(f"Role: {hiring_context['role_title']}")
            if hiring_context.get("seniority"):
                context_parts.append(f"Seniority: {hiring_context['seniority']}")
            if hiring_context.get("skills"):
                context_parts.append(f"Required Skills: {', '.join(hiring_context['skills'])}")
            if hiring_context.get("competencies"):
                context_parts.append(f"Required Competencies: {', '.join(hiring_context['competencies'])}")
            
            if context_parts:
                context_section = "\n**User Requirements:**\n" + "\n".join(f"- {part}" for part in context_parts)
        
        prompt = f"""The user asked: "{user_message}"
{context_section}

**Retrieved Assessments from Catalog:**

{chr(10).join(assessment_details)}

**Your Task:**
Generate a helpful, natural language response recommending these assessments to the user.

**Instructions:**
1. Start with a brief, friendly introduction
2. List each assessment with its title, URL, and why it matches their needs
3. Use ONLY the information provided above - do not add assessments or URLs not listed
4. Highlight key competencies and skills that match their requirements
5. Keep the response professional but conversational
6. Limit to the top {len(recommendations)} most relevant assessments
7. Include the URL for each assessment
8. If any information (duration, languages) is "Not specified", do not mention it

**Critical:** Only recommend the assessments listed above. Do not invent or suggest any other assessments."""

        return prompt
    
    def _build_no_recommendations_prompt(
        self,
        user_message: str,
        hiring_context: Optional[Dict[str, Any]],
    ) -> str:
        """Build prompt when no recommendations are available."""
        prompt = f"""The user asked: "{user_message}"

**Situation:**
No assessments were found in the catalog that match the user's requirements.

**Your Task:**
Politely inform the user that no matching assessments were found in the current catalog.
Ask clarifying questions to better understand their needs, such as:
- What specific role are they hiring for?
- What key skills or competencies are they looking to assess?
- What seniority level is the position?
- Are they looking for cognitive, personality, or skill-based assessments?

Keep the response helpful and guide them toward providing more specific requirements."""

        return prompt
