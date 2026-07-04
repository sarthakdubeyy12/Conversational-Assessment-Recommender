"""
Clarification prompt builder.

Builds prompts for generating clarification questions when user intent
or requirements are unclear or incomplete.
"""

from typing import Dict, Any, List, Optional


class ClarificationPromptBuilder:
    """
    Builds clarification prompts.
    
    Responsibilities:
    - Identify missing information
    - Generate targeted clarification questions
    - Guide user toward actionable requirements
    
    Design:
    - Asks only for actually missing information
    - Keeps questions concise and focused
    - Helps user provide structured input
    """
    
    def build(
        self,
        user_message: str,
        hiring_context: Optional[Dict[str, Any]] = None,
        missing_fields: Optional[List[str]] = None,
    ) -> str:
        """
        Build clarification prompt.
        
        Args:
            user_message: Original user message
            hiring_context: Current hiring context from conversation state
            missing_fields: List of missing required fields
        
        Returns:
            Clarification prompt string
        """
        # Analyze what's missing
        has_role = hiring_context and hiring_context.get("role_title")
        has_skills = hiring_context and hiring_context.get("skills")
        has_seniority = hiring_context and hiring_context.get("seniority")
        has_competencies = hiring_context and hiring_context.get("competencies")
        
        # Build context summary
        context_summary = []
        if hiring_context:
            if has_role:
                context_summary.append(f"Role: {hiring_context['role_title']}")
            if has_seniority:
                context_summary.append(f"Seniority: {hiring_context['seniority']}")
            if has_skills:
                context_summary.append(f"Skills: {', '.join(hiring_context['skills'][:5])}")
            if has_competencies:
                context_summary.append(f"Competencies: {', '.join(hiring_context['competencies'][:5])}")
        
        context_text = "\n".join(f"- {item}" for item in context_summary) if context_summary else "- No information provided yet"
        
        # Determine what to ask for
        missing_info = []
        if not has_role:
            missing_info.append("the specific role or job title you're hiring for")
        if not has_skills:
            missing_info.append("the key skills you want to assess")
        if not has_seniority:
            missing_info.append("the seniority level of the position")
        
        missing_text = ", ".join(missing_info) if missing_info else "more specific requirements"
        
        prompt = f"""The user said: "{user_message}"

**Current Information Captured:**
{context_text}

**Missing Information:**
To provide accurate assessment recommendations, I need to know {missing_text}.

**Your Task:**
Generate a friendly, concise clarification question that asks for the missing information.

**Instructions:**
1. Be specific about what information is needed
2. Keep the question conversational and helpful
3. Provide examples if helpful (e.g., "Are you hiring for a Senior Software Engineer, Product Manager, etc.?")
4. Ask for one or two pieces of information at a time - don't overwhelm the user
5. Explain briefly why this information helps with recommendations

**Example Clarification Questions:**
- "To recommend the right assessments, could you tell me what specific role you're hiring for?"
- "What key skills are most important for this position? For example: problem-solving, leadership, technical skills?"
- "What seniority level is this role - entry level, mid-level, or senior?"

Generate an appropriate clarification question based on what's missing."""

        return prompt
