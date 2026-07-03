"""
Candidate selector.

Filters and selects viable recommendation candidates.
"""

from typing import List
from src.retrieval.pipeline.pipeline_result import RankedDocument
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class CandidateSelector:
    """
    Select viable recommendation candidates.
    
    Responsibilities:
    - Filter low-quality results
    - Remove incomplete entries
    - Apply quality thresholds
    - Prepare for ranking
    
    Design:
    - Quality-focused filtering
    - Configurable thresholds
    - Preserves ranking order
    """
    
    def __init__(
        self,
        min_similarity: float = 0.0,
        require_url: bool = True,
        require_category: bool = False,
    ) -> None:
        """
        Initialize selector.
        
        Args:
            min_similarity: Minimum similarity threshold
            require_url: Require valid URL
            require_category: Require category metadata
        """
        self._min_similarity = min_similarity
        self._require_url = require_url
        self._require_category = require_category
    
    def select_candidates(
        self,
        ranked_docs: List[RankedDocument],
    ) -> List[RankedDocument]:
        """
        Select viable candidates from ranked documents.
        
        Args:
            ranked_docs: Ranked documents from retrieval
        
        Returns:
            Filtered list of candidates
        """
        logger.debug(f"Selecting candidates from {len(ranked_docs)} documents")
        
        candidates = []
        filtered_count = 0
        
        for doc in ranked_docs:
            # Check similarity threshold
            if doc.result.similarity_score < self._min_similarity:
                filtered_count += 1
                continue
            
            # Check URL requirement
            if self._require_url and not self._is_valid_url(doc.result.url):
                filtered_count += 1
                continue
            
            # Check category requirement
            if self._require_category and not doc.result.category:
                filtered_count += 1
                continue
            
            # Check name exists
            if not doc.result.assessment_name:
                filtered_count += 1
                continue
            
            candidates.append(doc)
        
        logger.info(
            f"Selected {len(candidates)} candidates "
            f"(filtered {filtered_count})"
        )
        
        return candidates
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid."""
        if not url:
            return False
        
        # Must be HTTPS URL from shl.com domain
        return url.startswith("https://") and "shl.com" in url
