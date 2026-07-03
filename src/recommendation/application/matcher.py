"""Match criteria to assessments."""

from typing import List

from src.recommendation.domain.entities import HiringCriteria, Recommendation


class AssessmentMatcher:
    """Matches hiring criteria to assessments."""
    
    def match(self, criteria: HiringCriteria, assessments: List[dict]) -> List[Recommendation]:
        pass
