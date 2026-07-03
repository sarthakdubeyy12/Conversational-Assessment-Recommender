"""
Assessment resolver.

Identifies and resolves assessment names from user input.
"""

import re
from typing import List, Tuple, Optional
from src.retrieval.pipeline.pipeline_result import PipelineResult
from src.comparison.domain.comparison_result import AssessmentInfo
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class AssessmentResolver:
    """
    Resolve assessment identities from queries.
    
    Responsibilities:
    - Extract assessment names from text
    - Match against retrieved catalog
    - Handle common patterns
    - Support aliases
    
    Design:
    - Pattern-based extraction
    - Fuzzy matching
    - Catalog-grounded only
    - No hallucination
    """
    
    def resolve_assessments(
        self,
        user_message: str,
        retrieval_result: PipelineResult,
    ) -> Tuple[Optional[AssessmentInfo], Optional[AssessmentInfo]]:
        """
        Resolve two assessments from user message and retrieval.
        
        Args:
            user_message: User's comparison request
            retrieval_result: Retrieval pipeline result
        
        Returns:
            (assessment_a, assessment_b) or (None, None) if not found
        """
        logger.debug(f"Resolving assessments from: '{user_message}'")
        
        # Extract assessment mentions from message
        mentions = self._extract_mentions(user_message)
        
        # Get top retrieved assessments
        retrieved = retrieval_result.ranked_documents[:5]  # Top 5
        
        if len(retrieved) < 2:
            logger.warning("Need at least 2 retrieved assessments for comparison")
            return None, None
        
        # Try to match mentions to retrieved assessments
        matched = []
        
        for mention in mentions:
            for doc in retrieved:
                if self._is_match(mention, doc.result.assessment_name):
                    info = self._build_assessment_info(doc)
                    if info not in matched:
                        matched.append(info)
                        break
        
        # If we found 2+ matches, use those
        if len(matched) >= 2:
            logger.info(f"Matched {len(matched)} assessments from mentions")
            return matched[0], matched[1]
        
        # Otherwise, use top 2 retrieved
        logger.info("Using top 2 retrieved assessments")
        assessment_a = self._build_assessment_info(retrieved[0])
        assessment_b = self._build_assessment_info(retrieved[1])
        
        return assessment_a, assessment_b
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract potential assessment mentions from text."""
        mentions = []
        
        # Pattern: "compare X and Y"
        match = re.search(r"compare\s+(.+?)\s+and\s+(.+?)(?:\s|$|[.,?!])", text, re.IGNORECASE)
        if match:
            mentions.append(match.group(1).strip())
            mentions.append(match.group(2).strip())
        
        # Pattern: "X vs Y"
        match = re.search(r"(.+?)\s+vs\.?\s+(.+?)(?:\s|$|[.,?!])", text, re.IGNORECASE)
        if match:
            mentions.append(match.group(1).strip())
            mentions.append(match.group(2).strip())
        
        # Pattern: "difference between X and Y"
        match = re.search(r"difference.+?between\s+(.+?)\s+and\s+(.+?)(?:\s|$|[.,?!])", text, re.IGNORECASE)
        if match:
            mentions.append(match.group(1).strip())
            mentions.append(match.group(2).strip())
        
        return mentions
    
    def _is_match(self, mention: str, assessment_name: str) -> bool:
        """Check if mention matches assessment name."""
        mention_lower = mention.lower().strip()
        name_lower = assessment_name.lower().strip()
        
        # Exact match
        if mention_lower == name_lower:
            return True
        
        # Partial match (mention in name)
        if mention_lower in name_lower:
            return True
        
        # Name starts with mention
        if name_lower.startswith(mention_lower):
            return True
        
        return False
    
    def _build_assessment_info(self, doc) -> AssessmentInfo:
        """Build AssessmentInfo from ranked document."""
        result = doc.result
        
        return AssessmentInfo(
            assessment_id=result.assessment_id,
            assessment_name=result.assessment_name,
            official_url=result.url,
            category=result.category or "",
            test_type=result.test_type or "",
            description=result.text or "",
            skills=result.skills or [],
            competencies=result.competencies or [],
            duration_minutes=result.duration_minutes or 0,
            languages=result.languages or [],
            job_levels=result.job_levels or [],
            industries=result.industries or [],
            tags=result.tags or [],
            retrieval_rank=0,
            chunk_id=result.chunk_id,
            similarity_score=result.similarity_score,
        )
