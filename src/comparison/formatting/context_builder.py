"""
Context builder.

Builds LLM-ready structured comparison context.
"""

from typing import List
from src.comparison.domain.comparison_result import AssessmentInfo, FieldComparison
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ComparisonContextBuilder:
    """
    Build structured comparison context.
    
    Responsibilities:
    - Format comparison for LLM consumption
    - Structure catalog facts
    - No prose or conversation
    - Token efficient
    
    Design:
    - Structured format
    - Catalog-grounded only
    - No response generation
    - LLM-ready
    """
    
    def build_context(
        self,
        assessment_a: AssessmentInfo,
        assessment_b: AssessmentInfo,
        similarities: List[str],
        differences: List[str],
        field_comparisons: List[FieldComparison],
    ) -> str:
        """
        Build LLM-ready comparison context.
        
        Args:
            assessment_a: First assessment
            assessment_b: Second assessment
            similarities: Similarity statements
            differences: Difference statements
            field_comparisons: Field comparisons
        
        Returns:
            Structured context string
        """
        logger.debug("Building LLM-ready context")
        
        sections = []
        
        # Assessment A
        sections.append(f"ASSESSMENT A: {assessment_a.assessment_name}")
        sections.append(f"URL: {assessment_a.official_url}")
        if assessment_a.category:
            sections.append(f"Category: {assessment_a.category}")
        if assessment_a.test_type:
            sections.append(f"Type: {assessment_a.test_type}")
        if assessment_a.skills:
            sections.append(f"Skills: {', '.join(assessment_a.skills[:5])}")
        if assessment_a.duration_minutes:
            sections.append(f"Duration: {assessment_a.duration_minutes} minutes")
        
        sections.append("")
        
        # Assessment B
        sections.append(f"ASSESSMENT B: {assessment_b.assessment_name}")
        sections.append(f"URL: {assessment_b.official_url}")
        if assessment_b.category:
            sections.append(f"Category: {assessment_b.category}")
        if assessment_b.test_type:
            sections.append(f"Type: {assessment_b.test_type}")
        if assessment_b.skills:
            sections.append(f"Skills: {', '.join(assessment_b.skills[:5])}")
        if assessment_b.duration_minutes:
            sections.append(f"Duration: {assessment_b.duration_minutes} minutes")
        
        sections.append("")
        
        # Similarities
        if similarities:
            sections.append("SIMILARITIES:")
            for sim in similarities[:5]:
                sections.append(f"- {sim}")
            sections.append("")
        
        # Differences
        if differences:
            sections.append("DIFFERENCES:")
            for diff in differences[:5]:
                sections.append(f"- {diff}")
        
        context = "\n".join(sections)
        
        logger.info(f"Built context: {len(context)} chars")
        return context
