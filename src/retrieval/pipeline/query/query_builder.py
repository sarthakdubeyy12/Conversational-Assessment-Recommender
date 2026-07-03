"""
Production query builder.

Transforms conversation state into optimized semantic search queries.
"""

from typing import List
from src.conversation.state.domain.conversation_state import ConversationState
from src.conversation.intent.domain.intent_result import IntentResult
from src.conversation.intent.domain.intent_types import IntentType
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ProductionQueryBuilder:
    """
    Build optimized semantic search queries.
    
    Responsibilities:
    - Extract key information from state
    - Generate targeted search queries
    - Normalize and clean queries
    - Prioritize important fields
    
    Design:
    - Intent-aware query generation
    - State-driven query construction
    - Multiple query support
    - Noise removal
    """
    
    def build_queries(
        self,
        state: ConversationState,
        intent: IntentResult,
    ) -> List[str]:
        """
        Build search queries from conversation state.
        
        Args:
            state: Conversation state
            intent: Intent result
        
        Returns:
            List of optimized search queries
        """
        logger.debug("Building search queries from state")
        
        hiring_ctx = state.hiring_context
        queries = []
        
        # Primary query: Role + skills
        primary = self._build_primary_query(hiring_ctx)
        if primary:
            queries.append(primary)
        
        # Secondary query: Assessment types (if specified)
        if hiring_ctx.assessment_types_requested:
            assessment_query = self._build_assessment_type_query(hiring_ctx)
            if assessment_query:
                queries.append(assessment_query)
        
        # Tertiary query: Competencies + skills
        if hiring_ctx.required_skills or hiring_ctx.technical_skills:
            skills_query = self._build_skills_query(hiring_ctx)
            if skills_query:
                queries.append(skills_query)
        
        # Fallback: Use job description if available
        if not queries and hiring_ctx.job_description:
            queries.append(self._normalize_text(hiring_ctx.job_description))
        
        # Ultimate fallback
        if not queries:
            queries.append("assessment for hiring")
        
        logger.info(f"Generated {len(queries)} search queries")
        return queries
    
    def _build_primary_query(self, hiring_ctx) -> str:
        """Build primary query from role and core requirements."""
        parts = []
        
        # Role title
        if hiring_ctx.role_title:
            parts.append(hiring_ctx.role_title)
        
        # Seniority
        if hiring_ctx.seniority:
            parts.append(hiring_ctx.seniority)
        
        # Key skills (top 3)
        all_skills = hiring_ctx.required_skills + hiring_ctx.technical_skills
        if all_skills:
            top_skills = all_skills[:3]
            parts.extend(top_skills)
        
        # Industry context
        if hiring_ctx.industry:
            parts.append(hiring_ctx.industry)
        
        query = " ".join(parts)
        return self._normalize_text(query)
    
    def _build_assessment_type_query(self, hiring_ctx) -> str:
        """Build query focused on assessment types."""
        parts = []
        
        if hiring_ctx.assessment_types_requested:
            parts.extend(hiring_ctx.assessment_types_requested)
        
        if hiring_ctx.role_title:
            parts.append(hiring_ctx.role_title)
        
        query = " ".join(parts)
        return self._normalize_text(query)
    
    def _build_skills_query(self, hiring_ctx) -> str:
        """Build query focused on skills and competencies."""
        parts = []
        
        # Combine all skills
        all_skills = (
            hiring_ctx.required_skills +
            hiring_ctx.technical_skills +
            hiring_ctx.soft_skills
        )
        
        # Take top 5 skills
        if all_skills:
            parts.extend(all_skills[:5])
        
        # Add role for context
        if hiring_ctx.role_title:
            parts.append(hiring_ctx.role_title)
        
        query = " ".join(parts)
        return self._normalize_text(query)
    
    def _normalize_text(self, text: str) -> str:
        """Normalize query text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        normalized = " ".join(text.split())
        
        # Remove special characters that don't add value
        normalized = normalized.replace("_", " ")
        normalized = normalized.replace("-", " ")
        
        # Final cleanup
        normalized = " ".join(normalized.split())
        
        return normalized.strip()
