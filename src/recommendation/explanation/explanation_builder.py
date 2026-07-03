"""
Explanation builder.

Generates recommendation explanations and reasoning.
"""

from typing import List
from src.retrieval.pipeline.pipeline_result import RankedDocument
from src.conversation.state.domain.conversation_state import ConversationState
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ExplanationBuilder:
    """
    Build recommendation explanations.
    
    Responsibilities:
    - Generate recommendation reasons
    - Extract matching factors
    - Create human-readable explanations
    - Base on catalog metadata only
    
    Design:
    - Metadata-driven explanations
    - No hallucination
    - Transparent reasoning
    - Human-readable
    """
    
    def build_explanation(
        self,
        doc: RankedDocument,
        state: ConversationState,
    ) -> tuple[str, List[str]]:
        """
        Build explanation for recommendation.
        
        Args:
            doc: Ranked document
            state: Conversation state
        
        Returns:
            (recommendation_reason, matching_factors)
        """
        factors = []
        
        # Extract matching factors
        factors.extend(self._extract_skill_matches(doc, state))
        factors.extend(self._extract_competency_matches(doc, state))
        factors.extend(self._extract_category_matches(doc, state))
        factors.extend(self._extract_level_matches(doc, state))
        
        # Build reason from factors
        if factors:
            reason = "; ".join(factors[:3])  # Top 3 factors
        else:
            reason = f"Relevant {doc.result.category or 'assessment'} for your requirements"
        
        return reason, factors
    
    def _extract_skill_matches(
        self,
        doc: RankedDocument,
        state: ConversationState,
    ) -> List[str]:
        """Extract skill matching factors."""
        factors = []
        
        hiring_ctx = state.hiring_context
        required_skills = set(
            skill.lower() for skill in
            hiring_ctx.required_skills + hiring_ctx.technical_skills
        )
        
        assessment_skills = set(
            skill.lower() for skill in doc.result.skills
        )
        
        matches = required_skills.intersection(assessment_skills)
        
        if matches:
            matched_list = list(matches)[:2]  # Top 2
            skills_str = ", ".join(matched_list)
            factors.append(f"Measures {skills_str}")
        
        return factors
    
    def _extract_competency_matches(
        self,
        doc: RankedDocument,
        state: ConversationState,
    ) -> List[str]:
        """Extract competency matching factors."""
        factors = []
        
        if doc.result.competencies:
            comp_str = doc.result.competencies[0]  # First competency
            factors.append(f"Assesses {comp_str}")
        
        return factors
    
    def _extract_category_matches(
        self,
        doc: RankedDocument,
        state: ConversationState,
    ) -> List[str]:
        """Extract category matching factors."""
        factors = []
        
        hiring_ctx = state.hiring_context
        category = doc.result.category
        
        if hiring_ctx.cognitive_required and category == "Cognitive":
            factors.append("Cognitive reasoning assessment")
        
        if hiring_ctx.personality_required and category == "Personality":
            factors.append("Personality assessment")
        
        if hiring_ctx.coding_required and category in ["Technical", "Coding"]:
            factors.append("Technical/coding assessment")
        
        return factors
    
    def _extract_level_matches(
        self,
        doc: RankedDocument,
        state: ConversationState,
    ) -> List[str]:
        """Extract job level matching factors."""
        factors = []
        
        hiring_ctx = state.hiring_context
        
        if hiring_ctx.seniority and doc.result.job_levels:
            seniority_lower = hiring_ctx.seniority.lower()
            levels_lower = [level.lower() for level in doc.result.job_levels]
            
            if "senior" in seniority_lower and any("senior" in level for level in levels_lower):
                factors.append("Suitable for senior roles")
            elif "junior" in seniority_lower and any("junior" in level for level in levels_lower):
                factors.append("Suitable for junior roles")
        
        return factors
