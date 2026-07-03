"""Analyze differences between assessments."""

from typing import List, Dict, Any

from src.comparison.domain.entities import Difference


class DiffAnalyzer:
    """Analyzes differences between assessments."""
    
    def analyze(self, assessment_a: Dict[str, Any], assessment_b: Dict[str, Any]) -> List[Difference]:
        pass
