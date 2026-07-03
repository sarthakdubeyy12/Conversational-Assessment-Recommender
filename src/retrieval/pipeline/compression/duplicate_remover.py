"""
Duplicate removal.

Removes duplicate chunks and assessments.
"""

from typing import List, Dict
from src.retrieval.pipeline.pipeline_result import RankedDocument
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class DuplicateRemover:
    """
    Remove duplicate documents.
    
    Responsibilities:
    - Deduplicate by assessment_id
    - Keep highest-ranked chunk per assessment
    - Preserve ranking order
    - Track deduplication metrics
    
    Design:
    - Assessment-level deduplication
    - Score-based selection
    - Preserves best chunk per assessment
    """
    
    def remove_duplicates(
        self,
        ranked_docs: List[RankedDocument],
    ) -> List[RankedDocument]:
        """
        Remove duplicate assessments, keeping highest-ranked.
        
        Args:
            ranked_docs: Ranked documents
        
        Returns:
            Deduplicated documents
        """
        logger.debug(f"Deduplicating {len(ranked_docs)} documents")
        
        # Track best document per assessment
        best_by_assessment: Dict[str, RankedDocument] = {}
        
        for doc in ranked_docs:
            assessment_id = doc.result.assessment_id
            
            # Keep first (highest-ranked) occurrence
            if assessment_id not in best_by_assessment:
                best_by_assessment[assessment_id] = doc
        
        # Return in original ranking order
        deduplicated = []
        seen_assessments = set()
        
        for doc in ranked_docs:
            assessment_id = doc.result.assessment_id
            if assessment_id not in seen_assessments:
                deduplicated.append(doc)
                seen_assessments.add(assessment_id)
        
        logger.info(
            f"Deduplicated {len(ranked_docs)} → {len(deduplicated)} documents "
            f"({len(ranked_docs) - len(deduplicated)} removed)"
        )
        
        return deduplicated
