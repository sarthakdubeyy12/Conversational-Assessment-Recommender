"""
Data normalization component.

Cleans, standardizes, and normalizes assessment data.
"""

import re
from dataclasses import replace
from typing import List

from src.catalog.domain.entities import Assessment
from src.catalog.domain.interfaces import IDataNormalizer
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class DataNormalizer(IDataNormalizer):
    """
    Normalizes assessment data.
    
    Operations:
    - Trim whitespace
    - Normalize casing
    - Remove HTML
    - Deduplicate lists
    - Clean unicode
    - Standardize formats
    """
    
    def normalize(self, assessment: Assessment) -> Assessment:
        """
        Normalize assessment data.
        
        Args:
            assessment: Assessment to normalize
        
        Returns:
            Normalized assessment
        """
        return replace(
            assessment,
            name=self._normalize_text(assessment.name),
            description=self._normalize_text(assessment.description) if assessment.description else None,
            category=self._normalize_category(assessment.category) if assessment.category else None,
            test_type=self._normalize_text(assessment.test_type) if assessment.test_type else None,
            skills_measured=self._normalize_list(assessment.skills_measured),
            competencies=self._normalize_list(assessment.competencies),
            languages=self._normalize_list(assessment.languages),
            job_levels=self._normalize_list(assessment.job_levels),
            suitable_roles=self._normalize_list(assessment.suitable_roles),
            industries=self._normalize_list(assessment.industries),
            tags=self._normalize_list(assessment.tags),
        )
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text field.
        
        - Trim whitespace
        - Remove multiple spaces
        - Remove HTML tags
        - Clean unicode
        """
        if not text:
            return text
        
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)
        
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)
        
        # Trim
        text = text.strip()
        
        return text
    
    def _normalize_category(self, category: str) -> str:
        """Normalize category - title case."""
        if not category:
            return category
        
        normalized = self._normalize_text(category)
        return normalized.title()
    
    def _normalize_list(self, items: List[str]) -> List[str]:
        """
        Normalize list of items.
        
        - Normalize each item
        - Remove empty strings
        - Deduplicate
        - Sort
        """
        if not items:
            return []
        
        # Normalize each item
        normalized = [self._normalize_text(item) for item in items]
        
        # Remove empty
        normalized = [item for item in normalized if item]
        
        # Deduplicate (case-insensitive)
        seen = set()
        unique = []
        for item in normalized:
            lower = item.lower()
            if lower not in seen:
                seen.add(lower)
                unique.append(item)
        
        # Sort for consistency
        unique.sort()
        
        return unique
