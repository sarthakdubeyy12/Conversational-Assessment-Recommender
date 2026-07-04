"""
Comparison prompt builder.

Builds prompts for generating natural language comparison responses
based on structured comparison results.
"""

from typing import Any


class ComparisonPromptBuilder:
    """
    Builds comparison prompts from structured comparison results.
    
    Responsibilities:
    - Convert ComparisonResult into LLM prompt
    - Format similarities and differences
    - Ensure factual comparison only
    - Include assessment URLs
    
    Design:
    - Uses structured comparison data only
    - No inference or assumptions
    - Clear formatting
    """
    
    def build(
        self,
        user_message: str,
        comparison_result: Any,
    ) -> str:
        """
        Build comparison prompt.
        
        Args:
            user_message: Original user message
            comparison_result: Structured comparison result
        
        Returns:
            Comparison prompt string
        """
        if not comparison_result or not comparison_result.assessments:
            return self._build_no_comparison_prompt(user_message)
        
        # Extract assessments
        assessments = comparison_result.assessments[:2]  # Typically 2 assessments
        
        # Build assessment details
        assessment_details = []
        for idx, assessment in enumerate(assessments, 1):
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
"""
            assessment_details.append(detail.strip())
        
        # Build comparison data
        similarities = comparison_result.similarities or []
        differences = comparison_result.differences or []
        
        similarities_text = "\n".join(f"- {sim}" for sim in similarities) if similarities else "- No specific similarities identified"
        differences_text = "\n".join(f"- {diff}" for diff in differences) if differences else "- No specific differences identified"
        
        prompt = f"""The user asked: "{user_message}"

**Assessments Being Compared:**

{chr(10).join(assessment_details)}

**Identified Similarities:**
{similarities_text}

**Identified Differences:**
{differences_text}

**Your Task:**
Generate a natural, helpful comparison of these two assessments for the user.

**Instructions:**
1. Start with a brief introduction
2. Highlight the key similarities first
3. Then explain the key differences
4. Use ONLY the information provided above
5. Do not infer or assume differences not explicitly listed
6. Include URLs for both assessments
7. Help the user understand which assessment might be better for different scenarios
8. Keep the response structured and easy to read

**Critical:** Base your comparison entirely on the data provided above. Do not add information not present in the assessment details."""

        return prompt
    
    def _build_no_comparison_prompt(self, user_message: str) -> str:
        """Build prompt when no comparison is available."""
        prompt = f"""The user asked: "{user_message}"

**Situation:**
Unable to perform comparison - assessments not found in the catalog or insufficient data.

**Your Task:**
Politely inform the user that a comparison cannot be completed.
Ask them to:
- Specify the exact assessment names they want to compare
- Or describe the types of assessments they want to compare
- Provide more details about their comparison needs

Keep the response helpful and guide them toward a successful comparison request."""

        return prompt
