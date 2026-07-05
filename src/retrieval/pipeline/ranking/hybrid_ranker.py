"""
Hybrid ranking engine.

Combines semantic similarity with metadata relevance.
"""

from typing import List, Dict, Any
from src.retrieval.domain.entities import RetrievalResult
from src.retrieval.pipeline.pipeline_result import RankedDocument
from src.conversation.state.domain.conversation_state import ConversationState
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class HybridRanker:
    """
    Hybrid ranking engine.
    
    Responsibilities:
    - Combine semantic similarity with metadata
    - Calculate skill overlap scores
    - Apply field-specific boosts
    - Produce normalized ranking scores
    
    Design:
    - Weighted scoring
    - Configurable weights
    - Normalized output (0-1)
    - Explainable ranking factors
    """
    
    def __init__(
        self,
        semantic_weight: float = 0.5,
        metadata_weight: float = 0.3,
        skill_weight: float = 0.2,
    ) -> None:
        """
        Initialize ranker with weights.
        
        Args:
            semantic_weight: Weight for semantic similarity
            metadata_weight: Weight for metadata match
            skill_weight: Weight for skill overlap
        """
        self._semantic_weight = semantic_weight
        self._metadata_weight = metadata_weight
        self._skill_weight = skill_weight
    
    def rank(
        self,
        results: List[RetrievalResult],
        state: ConversationState,
    ) -> List[RankedDocument]:
        """
        Rank retrieval results.
        
        Args:
            results: Retrieved results
            state: Conversation state
        
        Returns:
            Ranked documents with scores
        """
        if not results:
            logger.info("No results to rank")
            return []
        
        logger.info(f"Ranking {len(results)} results")
        
        ranked_docs = []
        
        for result in results:
            # Calculate individual scores
            semantic_score = result.similarity_score
            metadata_score = self._calculate_metadata_score(result, state)
            skill_score = self._calculate_skill_score(result, state)
            
            # Weighted combination
            final_score = (
                self._semantic_weight * semantic_score +
                self._metadata_weight * metadata_score +
                self._skill_weight * skill_score
            )
            
            ranking_factors = {
                "semantic": semantic_score,
                "metadata": metadata_score,
                "skill": skill_score,
            }
            
            ranked_doc = RankedDocument(
                result=result,
                ranking_score=final_score,
                ranking_factors=ranking_factors,
            )
            ranked_docs.append(ranked_doc)
        
        # Sort by ranking score (descending)
        ranked_docs.sort(key=lambda x: x.ranking_score, reverse=True)
        
        logger.info(f"Ranked {len(ranked_docs)} documents successfully")
        return ranked_docs
    
    def _calculate_metadata_score(
        self,
        result: RetrievalResult,
        state: ConversationState,
    ) -> float:
        """Calculate metadata relevance score."""
        score = 0.0
        factors = 0
        
        hiring_ctx = state.hiring_context
        
        # Assessment type match
        if hiring_ctx.assessment_types_requested:
            if result.test_type in hiring_ctx.assessment_types_requested:
                score += 1.0
            factors += 1
        
        # Language match
        if hiring_ctx.languages:
            if any(lang in result.languages for lang in hiring_ctx.languages):
                score += 1.0
            factors += 1
        
        # Job level match
        if hiring_ctx.seniority:
            seniority_lower = hiring_ctx.seniority.lower()
            result_levels_lower = [level.lower() for level in result.job_levels]
            
            if "senior" in seniority_lower and any("senior" in level for level in result_levels_lower):
                score += 1.0
            elif "junior" in seniority_lower and any("junior" in level for level in result_levels_lower):
                score += 1.0
            factors += 1
        
        # Industry match
        if hiring_ctx.industry:
            if hiring_ctx.industry.lower() in [ind.lower() for ind in result.industries]:
                score += 1.0
            factors += 1
        
        # Normalize
        if factors > 0:
            return score / factors
        return 0.0
    
    def _calculate_skill_score(
        self,
        result: RetrievalResult,
        state: ConversationState,
    ) -> float:
        """Calculate skill overlap score."""
        hiring_ctx = state.hiring_context
        
        # Gather all required skills
        required_skills = set(
            skill.lower() for skill in
            hiring_ctx.required_skills +
            hiring_ctx.technical_skills +
            hiring_ctx.soft_skills
        )
        
        if not required_skills:
            return 0.0
        
        # Gather assessment skills
        assessment_skills = set(
            skill.lower() for skill in
            result.skills + result.competencies
        )
        
        if not assessment_skills:
            return 0.0
        
        # Calculate overlap
        overlap = required_skills.intersection(assessment_skills)
        score = len(overlap) / len(required_skills)
        
        return min(score, 1.0)
