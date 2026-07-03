"""
Retrieval validation.

Validates retrieval quality and detects issues.
"""

from typing import List, Tuple
from src.retrieval.pipeline.pipeline_result import RankedDocument
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class RetrievalValidator:
    """
    Validate retrieval results.
    
    Responsibilities:
    - Check result quality
    - Detect empty results
    - Validate similarity scores
    - Check metadata completeness
    - Generate warnings
    
    Design:
    - Quality-focused validation
    - Non-blocking warnings
    - Diagnostic information
    """
    
    def __init__(
        self,
        min_similarity: float = 0.3,
        min_results: int = 1,
    ) -> None:
        """
        Initialize validator.
        
        Args:
            min_similarity: Minimum acceptable similarity score
            min_results: Minimum expected results
        """
        self._min_similarity = min_similarity
        self._min_results = min_results
    
    def validate(
        self,
        ranked_docs: List[RankedDocument],
    ) -> Tuple[bool, List[str]]:
        """
        Validate retrieval results.
        
        Args:
            ranked_docs: Ranked documents
        
        Returns:
            (is_valid, warnings)
        """
        logger.debug(f"Validating {len(ranked_docs)} results")
        
        warnings = []
        is_valid = True
        
        # Check if empty
        if len(ranked_docs) == 0:
            warnings.append("No results retrieved")
            is_valid = False
            return is_valid, warnings
        
        # Check minimum results
        if len(ranked_docs) < self._min_results:
            warnings.append(
                f"Only {len(ranked_docs)} results (expected >= {self._min_results})"
            )
        
        # Check similarity scores
        low_sim_count = sum(
            1 for doc in ranked_docs
            if doc.result.similarity_score < self._min_similarity
        )
        
        if low_sim_count > 0:
            warnings.append(
                f"{low_sim_count} results below similarity threshold "
                f"({self._min_similarity})"
            )
        
        # Check metadata completeness
        missing_metadata_count = sum(
            1 for doc in ranked_docs
            if not doc.result.category or not doc.result.test_type
        )
        
        if missing_metadata_count > 0:
            warnings.append(
                f"{missing_metadata_count} results missing category/test_type"
            )
        
        # Check for broken URLs
        broken_url_count = sum(
            1 for doc in ranked_docs
            if not doc.result.url or not doc.result.url.startswith("http")
        )
        
        if broken_url_count > 0:
            warnings.append(f"{broken_url_count} results with invalid URLs")
        
        logger.info(
            f"Validation: valid={is_valid}, warnings={len(warnings)}"
        )
        
        return is_valid, warnings
