"""
Context inferrer.

Infers missing information from provided context.
"""

from typing import Set
from src.conversation.state.domain.conversation_state import HiringContext
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ContextInferrer:
    """
    Infers hiring context from explicit information.
    
    Responsibilities:
    - Infer seniority from years of experience
    - Infer required assessments from role
    - Infer skills from role title
    - Mark inferred fields separately
    
    Design:
    - Rule-based inference
    - Conservative inference (high confidence only)
    - Track what was inferred vs explicit
    """
    
    def __init__(self) -> None:
        """Initialize inferrer."""
        self._senior_roles = [
            "senior", "lead", "principal", "staff", "architect",
            "manager", "director", "vp", "head",
        ]
        
        self._technical_roles = [
            "developer", "engineer", "programmer", "architect",
            "sre", "devops", "qa", "tester",
        ]
        
        self._leadership_roles = [
            "manager", "director", "lead", "head", "vp",
            "team lead", "tech lead", "principal",
        ]
    
    def infer_context(
        self,
        context: HiringContext,
    ) -> tuple[HiringContext, Set[str]]:
        """
        Infer missing context.
        
        Args:
            context: Current hiring context
        
        Returns:
            (Updated context, Set of inferred fields)
        """
        inferred_fields = set()
        
        # Infer seniority from experience
        if context.seniority is None and context.years_of_experience:
            context.seniority = self._infer_seniority_from_experience(
                context.years_of_experience
            )
            if context.seniority:
                inferred_fields.add("seniority")
        
        # Infer seniority from role
        if context.seniority is None and context.role_title:
            context.seniority = self._infer_seniority_from_role(
                context.role_title
            )
            if context.seniority:
                inferred_fields.add("seniority")
        
        # Infer leadership requirement
        if context.leadership_required is None and context.role_title:
            context.leadership_required = self._infer_leadership(
                context.role_title,
                context.seniority,
            )
            if context.leadership_required:
                inferred_fields.add("leadership_required")
        
        # Infer cognitive requirement (most roles need it)
        if context.cognitive_required is None:
            context.cognitive_required = True
            inferred_fields.add("cognitive_required")
        
        # Infer coding requirement from role
        if context.coding_required is None and context.role_title:
            context.coding_required = self._infer_coding_need(
                context.role_title
            )
            if context.coding_required:
                inferred_fields.add("coding_required")
        
        if inferred_fields:
            logger.debug(f"Inferred fields: {inferred_fields}")
        
        return context, inferred_fields
    
    def _infer_seniority_from_experience(self, years: int) -> str | None:
        """Infer seniority from years of experience."""
        if years < 2:
            return "junior"
        elif years < 5:
            return "mid"
        elif years < 10:
            return "senior"
        else:
            return "senior"
    
    def _infer_seniority_from_role(self, role: str) -> str | None:
        """Infer seniority from role title."""
        role_lower = role.lower()
        
        for keyword in self._senior_roles:
            if keyword in role_lower:
                return "senior"
        
        if "junior" in role_lower or "entry" in role_lower:
            return "junior"
        
        return None
    
    def _infer_leadership(
        self,
        role: str,
        seniority: str | None,
    ) -> bool:
        """Infer if leadership assessment is needed."""
        role_lower = role.lower()
        
        # Check role keywords
        for keyword in self._leadership_roles:
            if keyword in role_lower:
                return True
        
        # Senior roles often need leadership
        if seniority == "senior":
            return True
        
        return False
    
    def _infer_coding_need(self, role: str) -> bool:
        """Infer if coding assessment is needed."""
        role_lower = role.lower()
        
        for keyword in self._technical_roles:
            if keyword in role_lower:
                return True
        
        return False
