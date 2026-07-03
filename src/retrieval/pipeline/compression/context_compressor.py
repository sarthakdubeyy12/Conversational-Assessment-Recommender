"""
Context compression.

Compresses retrieved context for LLM consumption.
"""

from typing import List
from src.retrieval.pipeline.pipeline_result import RankedDocument
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ContextCompressor:
    """
    Compress retrieval context for LLM.
    
    Responsibilities:
    - Merge information from multiple chunks
    - Summarize metadata
    - Remove redundancy
    - Optimize for token budget
    
    Design:
    - Assessment-focused compression
    - Metadata prioritization
    - Token-aware formatting
    - Preserves critical information
    """
    
    def __init__(self, max_assessments: int = 5) -> None:
        """
        Initialize compressor.
        
        Args:
            max_assessments: Maximum assessments to include
        """
        self._max_assessments = max_assessments
    
    def compress(
        self,
        ranked_docs: List[RankedDocument],
    ) -> str:
        """
        Compress context into LLM-ready format.
        
        Args:
            ranked_docs: Ranked and deduplicated documents
        
        Returns:
            Compressed context string
        """
        logger.debug(f"Compressing {len(ranked_docs)} documents")
        
        # Limit to top N assessments
        top_docs = ranked_docs[:self._max_assessments]
        
        # Build compressed context
        context_parts = []
        
        for idx, doc in enumerate(top_docs, 1):
            result = doc.result
            
            # Format assessment entry
            entry = self._format_assessment(idx, result)
            context_parts.append(entry)
        
        compressed = "\n\n".join(context_parts)
        
        logger.info(
            f"Compressed {len(ranked_docs)} → {len(top_docs)} assessments, "
            f"{len(compressed)} chars"
        )
        
        return compressed
    
    def _format_assessment(self, idx: int, result) -> str:
        """Format single assessment for context."""
        lines = [
            f"Assessment {idx}: {result.assessment_name}",
            f"URL: {result.url}",
        ]
        
        # Add key metadata
        if result.category:
            lines.append(f"Category: {result.category}")
        
        if result.test_type:
            lines.append(f"Type: {result.test_type}")
        
        if result.skills:
            skills_str = ", ".join(result.skills[:5])
            lines.append(f"Skills: {skills_str}")
        
        if result.competencies:
            comp_str = ", ".join(result.competencies[:3])
            lines.append(f"Competencies: {comp_str}")
        
        if result.duration_minutes:
            lines.append(f"Duration: {result.duration_minutes} minutes")
        
        if result.job_levels:
            levels_str = ", ".join(result.job_levels)
            lines.append(f"Job Levels: {levels_str}")
        
        # Add text content (truncated)
        text_preview = result.text[:200] + "..." if len(result.text) > 200 else result.text
        lines.append(f"Description: {text_preview}")
        
        return "\n".join(lines)
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token count estimation (4 chars ≈ 1 token)."""
        return len(text) // 4
