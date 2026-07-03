"""
Conflict detector.

Detects contradictions in hiring requirements.
"""

from typing import List
from src.conversation.state.domain.conversation_state import HiringContext
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ConflictDetector:
    """
    Detects conflicts in hiring context.
    
    Responsibilities:
    - Detect logical contradictions
    - Identify incompatible requirements
    - Flag suspicious combinations
    
    Examples of conflicts:
    - Junior role + 10 years experience
    - Entry-level + leadership required
    - Conflicting seniority signals
    """
    
    def detect_conflicts(
        self,
        context: HiringContext,
    ) -> List[str]:
        """
        Detect conflicts in context.
        
        Args:
            context: Hiring context
        
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Check seniority vs experience
        seniority_exp_conflict = self._check_seniority_experience(context)
        if seniority_exp_conflict:
            conflicts.append(seniority_exp_conflict)
        
        # Check role vs seniority
        role_seniority_conflict = self._check_role_seniority(context)
        if role_seniority_conflict:
            conflicts.append(role_seniority_conflict)
        
        # Check leadership vs seniority
        leadership_conflict = self._check_leadership_seniority(context)
        if leadership_conflict:
            conflicts.append(leadership_conflict)
        
        if conflicts:
            logger.debug(f"Detected {len(conflicts)} conflicts")
        
        return conflicts
    
    def _check_seniority_experience(
        self,
        context: HiringContext,
    ) -> str | None:
        """Check seniority vs years of experience."""
        if not context.seniority or context.years_of_experience is None:
            return None
        
        years = context.years_of_experience
        seniority = context.seniority
        
        # Junior with many years
        if seniority == "junior" and years > 3:
            return (
                f"Conflict: Junior level but {years} years experience "
                f"(junior typically < 2 years)"
            )
        
        # Senior with few years
        if seniority == "senior" and years < 5:
            return (
                f"Conflict: Senior level but only {years} years experience "
                f"(senior typically 5+ years)"
            )
        
        return None
    
    def _check_role_seniority(
        self,
        context: HiringContext,
    ) -> str | None:
        """Check role title vs seniority."""
        if not context.role_title or not context.seniority:
            return None
        
        role_lower = context.role_title.lower()
        
        # Junior in title but senior seniority
        if "junior" in role_lower and context.seniority == "senior":
            return "Conflict: Role title says 'junior' but seniority is 'senior'"
        
        # Senior in title but junior seniority
        if "senior" in role_lower and context.seniority == "junior":
            return "Conflict: Role title says 'senior' but seniority is 'junior'"
        
        return None
    
    def _check_leadership_seniority(
        self,
        context: HiringContext,
    ) -> str | None:
        """Check leadership requirement vs seniority."""
        if context.leadership_required is None or not context.seniority:
            return None
        
        # Leadership required but junior level
        if context.leadership_required and context.seniority == "junior":
            return (
                "Conflict: Leadership required but junior level "
                "(junior roles typically don't require leadership)"
            )
        
        return None
