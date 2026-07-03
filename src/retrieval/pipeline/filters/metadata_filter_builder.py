"""
Metadata filter builder.

Constructs metadata filters from conversation state.
"""

from typing import Dict, Any, List
from src.conversation.state.domain.conversation_state import ConversationState
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class MetadataFilterBuilder:
    """
    Build metadata filters for retrieval.
    
    Responsibilities:
    - Extract filter criteria from state
    - Convert to ChromaDB filter format
    - Apply constraint logic
    - Support future filter expansion
    
    Design:
    - State-driven filter construction
    - ChromaDB-compatible format
    - Flexible filter combinations
    - Future-proof architecture
    """
    
    def build_filters(self, state: ConversationState) -> Dict[str, Any]:
        """
        Build metadata filters from conversation state.
        
        Args:
            state: Conversation state
        
        Returns:
            ChromaDB-compatible filter dict
        """
        logger.debug("Building metadata filters")
        
        hiring_ctx = state.hiring_context
        conditions = []
        
        # Assessment type filter (if specified)
        if hiring_ctx.assessment_types_requested:
            conditions.append({
                "test_type": {"$in": hiring_ctx.assessment_types_requested}
            })
        
        # Language filter
        if hiring_ctx.languages:
            conditions.append({
                "languages": {"$in": hiring_ctx.languages}
            })
        
        # Category filter (if specific assessment requested)
        if hiring_ctx.cognitive_required is True:
            conditions.append({"category": "Cognitive"})
        elif hiring_ctx.personality_required is True:
            conditions.append({"category": "Personality"})
        elif hiring_ctx.coding_required is True:
            conditions.append({
                "test_type": {"$in": ["Coding", "Technical"]}
            })
        
        # Job level filter
        if hiring_ctx.seniority:
            # Map seniority to job levels
            job_level = self._map_seniority_to_level(hiring_ctx.seniority)
            if job_level:
                conditions.append({
                    "job_levels": {"$contains": job_level}
                })
        
        # Combine conditions with $and if multiple
        if len(conditions) == 0:
            return {}
        elif len(conditions) == 1:
            return conditions[0]
        else:
            return {"$and": conditions}
        
        logger.info(f"Built filters with {len(conditions)} conditions")
    
    def _map_seniority_to_level(self, seniority: str) -> str:
        """Map seniority level to job level."""
        seniority_lower = seniority.lower()
        
        if "senior" in seniority_lower or "lead" in seniority_lower:
            return "Senior"
        elif "junior" in seniority_lower or "entry" in seniority_lower:
            return "Junior"
        elif "mid" in seniority_lower or "intermediate" in seniority_lower:
            return "Mid-level"
        elif "executive" in seniority_lower or "director" in seniority_lower:
            return "Executive"
        
        return ""
