"""
Recommendation ranker.

Ranks assessment candidates for recommendations.
"""

from typing import List, Tuple
from src.retrieval.pipeline.pipeline_result import RankedDocument
from src.conversation.state.domain.conversation_state import ConversationState
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class RecommendationRanker:
    """
    Rank assessment recommendations.
    
    Responsibilities:
    - Apply final ranking adjustments
    - Boost relevant categories
    - Apply diversity weighting
    - Enforce ranking limits
    
    Design:
    - Reuses retrieval ranking as base
    - Applies recommendation-specific boosts
    - Configurable weights
    - Preserves score transparency
    """
    
    def __init__(
        self,
        category_boost: float = 0.1,
        diversity_weight: float = 0.05,
        max_recommendations: int = 10,
    ) -> None:
        """
        Initialize ranker.
        
        Args:
            category_boost: Boost for matching category
            diversity_weight: Weight for diversity
            max_recommendations: Maximum recommendations to return
        """
        self._category_boost = category_boost
        self._diversity_weight = diversity_weight
        self._max_recommendations = max_recommendations
    
    def rank(
        self,
        candidates: List[RankedDocument],
        state: ConversationState,
    ) -> List[Tuple[RankedDocument, float]]:
        """
        Rank candidates for recommendations.
        
        Args:
            candidates: Candidate documents
            state: Conversation state
        
        Returns:
            List of (document, final_score) tuples
        """
        logger.debug(f"Ranking {len(candidates)} candidates")
        
        ranked = []
        seen_categories = set()
        
        for doc in candidates:
            # Start with retrieval ranking score
            score = doc.ranking_score
            
            # Apply category boost
            if self._should_boost_category(doc, state):
                score += self._category_boost
            
            # Apply diversity boost (first of each category)
            category = doc.result.category or "unknown"
            if category not in seen_categories:
                score += self._diversity_weight
                seen_categories.add(category)
            
            ranked.append((doc, score))
        
        # Sort by final score
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        # Limit to max recommendations
        ranked = ranked[:self._max_recommendations]
        
        logger.info(f"Final ranking: {len(ranked)} recommendations")
        
        return ranked
    
    def _should_boost_category(
        self,
        doc: RankedDocument,
        state: ConversationState,
    ) -> bool:
        """Check if category should be boosted."""
        hiring_ctx = state.hiring_context
        category = doc.result.category
        
        if not category:
            return False
        
        # Boost cognitive if requested
        if hiring_ctx.cognitive_required and category == "Cognitive":
            return True
        
        # Boost personality if requested
        if hiring_ctx.personality_required and category == "Personality":
            return True
        
        # Boost technical/coding if requested
        if hiring_ctx.coding_required and category in ["Technical", "Coding"]:
            return True
        
        return False
