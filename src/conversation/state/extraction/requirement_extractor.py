"""
Requirement extractor.

Extracts hiring requirements from conversation messages.
"""

from typing import List, Dict, Any
import re

from src.conversation.domain.entities import Message
from src.conversation.state.domain.conversation_state import HiringContext
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class RequirementExtractor:
    """
    Extracts structured hiring requirements from messages.
    
    Responsibilities:
    - Parse user messages for hiring signals
    - Extract role, skills, experience, etc.
    - Handle multiple extraction patterns
    - Normalize extracted values
    
    Design:
    - Pattern-based extraction
    - Keyword matching
    - Context-aware parsing
    - Incremental extraction
    """
    
    def __init__(self) -> None:
        """Initialize extractor with patterns."""
        self._role_patterns = [
            r"hiring\s+(?:a\s+)?(.+?)(?:\s+developer|\s+engineer|\s+manager)?",
            r"looking\s+for\s+(?:a\s+)?(.+?)(?:\s+developer|\s+engineer)?",
            r"need\s+(?:a\s+)?(.+?)(?:\s+developer|\s+engineer)?",
            r"(?:role|position):\s*(.+?)(?:\.|$)",
        ]
        
        self._seniority_keywords = {
            "junior": ["junior", "entry", "entry-level", "graduate"],
            "mid": ["mid", "mid-level", "intermediate"],
            "senior": ["senior", "lead", "principal", "staff"],
            "executive": ["executive", "director", "vp", "cto", "ceo"],
        }
        
        self._skill_keywords = [
            "java", "python", "javascript", "typescript", "react", "node",
            "kubernetes", "docker", "aws", "azure", "gcp",
            "sql", "nosql", "mongodb", "postgresql",
            "leadership", "communication", "problem solving",
            "teamwork", "analytical", "critical thinking",
        ]
        
        self._assessment_keywords = {
            "cognitive": ["cognitive", "reasoning", "logical", "problem solving"],
            "personality": ["personality", "behavioral", "soft skills"],
            "technical": ["technical", "coding", "programming"],
            "numerical": ["numerical", "math", "quantitative"],
            "verbal": ["verbal", "communication", "writing"],
        }
    
    def extract_from_messages(
        self,
        messages: List[Message],
    ) -> HiringContext:
        """
        Extract hiring context from conversation messages.
        
        Args:
            messages: Conversation history
        
        Returns:
            Extracted hiring context
        """
        context = HiringContext()
        
        # Extract from user messages only
        user_messages = [m for m in messages if m.role == "user"]
        
        if not user_messages:
            return context
        
        # Combine all user messages
        combined_text = " ".join([m.content for m in user_messages])
        combined_lower = combined_text.lower()
        
        # Extract role
        context.role_title = self._extract_role(combined_lower)
        
        # Extract seniority
        context.seniority = self._extract_seniority(combined_lower)
        
        # Extract years of experience
        context.years_of_experience = self._extract_years_experience(combined_lower)
        
        # Extract skills
        skills = self._extract_skills(combined_lower)
        context.technical_skills = skills
        context.required_skills = skills[:5] if skills else []
        
        # Extract assessment preferences
        context.assessment_types_requested = self._extract_assessment_types(
            combined_lower
        )
        
        # Extract requirements
        context.leadership_required = self._check_leadership(combined_lower)
        context.cognitive_required = self._check_cognitive(combined_lower)
        context.personality_required = self._check_personality(combined_lower)
        context.coding_required = self._check_coding(combined_lower)
        
        # Extract job description if present
        if len(combined_text) > 100:
            context.job_description = combined_text[:500]
        
        logger.debug(f"Extracted context: role={context.role_title}, "
                    f"seniority={context.seniority}, "
                    f"skills={len(context.technical_skills)}")
        
        return context
    
    def _extract_role(self, text: str) -> str | None:
        """Extract role title."""
        for pattern in self._role_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                role = match.group(1).strip()
                # Clean up
                role = re.sub(r'\s+', ' ', role)
                if len(role) > 3 and len(role) < 50:
                    return role.title()
        return None
    
    def _extract_seniority(self, text: str) -> str | None:
        """Extract seniority level."""
        for level, keywords in self._seniority_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return level
        return None
    
    def _extract_years_experience(self, text: str) -> int | None:
        """Extract years of experience."""
        patterns = [
            r"(\d+)\+?\s*years?",
            r"(\d+)\+?\s*yrs?",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                years = int(match.group(1))
                if 0 < years < 50:
                    return years
        return None
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills."""
        found_skills = []
        for skill in self._skill_keywords:
            if skill in text:
                found_skills.append(skill.title())
        return found_skills
    
    def _extract_assessment_types(self, text: str) -> List[str]:
        """Extract requested assessment types."""
        types = []
        for type_name, keywords in self._assessment_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    if type_name not in types:
                        types.append(type_name)
                    break
        return types
    
    def _check_leadership(self, text: str) -> bool:
        """Check if leadership assessment is needed."""
        keywords = ["leadership", "manager", "lead", "team lead", "director"]
        return any(kw in text for kw in keywords)
    
    def _check_cognitive(self, text: str) -> bool:
        """Check if cognitive assessment is needed."""
        keywords = ["cognitive", "reasoning", "problem solving", "analytical"]
        return any(kw in text for kw in keywords)
    
    def _check_personality(self, text: str) -> bool:
        """Check if personality assessment is needed."""
        keywords = ["personality", "behavioral", "culture fit", "soft skills"]
        return any(kw in text for kw in keywords)
    
    def _check_coding(self, text: str) -> bool:
        """Check if coding assessment is needed."""
        keywords = ["coding", "programming", "technical test", "algorithm"]
        return any(kw in text for kw in keywords)
