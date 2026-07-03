"""
Scope detector.

Detects out-of-scope and off-topic requests.
"""

import re
from typing import Tuple, List
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ScopeDetector:
    """
    Detect scope violations.
    
    Responsibilities:
    - Detect off-topic requests
    - Detect unsupported domains
    - Enforce SHL assessment scope
    
    Design:
    - Keyword-based detection
    - Domain classification
    - Explicit scope definition
    """
    
    def __init__(self) -> None:
        """Initialize with scope rules."""
        # In-scope topics (SHL assessments)
        self._in_scope_keywords = [
            "assessment", "test", "evaluation", "shl", "verify", "opp",
            "cognitive", "personality", "aptitude", "reasoning", "numerical",
            "verbal", "situational", "judgment", "competenc", "skill",
            "hire", "hiring", "recruit", "candidate", "job", "role",
            "compare", "difference", "recommend", "suggest", "which",
        ]
        
        # Off-topic domains
        self._off_topic_domains = {
            "weather": ["weather", "forecast", "temperature", "rain", "snow"],
            "politics": ["politics", "government", "election", "president", "congress"],
            "movies": ["movie", "film", "actor", "cinema", "netflix", "latest movies"],
            "sports": ["football", "basketball", "soccer", "sports", "game score"],
            "programming": ["code", "python", "javascript", "debug", "api", "function"],
            "medical": ["medical", "health", "disease", "symptom", "diagnosis", "treatment"],
            "financial": ["stock", "investment", "bitcoin", "crypto", "trading"],
            "legal": ["legal", "law", "attorney", "lawsuit", "court"],
            "general_chat": ["how are you", "what's up", "tell me a joke", "fun fact", "tell me about"],
        }
        
        # Unsupported HR topics (not assessment-specific)
        self._unsupported_hr = [
            "salary", "compensation", "pay", "wage", "benefit",
            "resume", "cv", "cover letter", "interview prep",
            "negotiate", "offer letter", "contract",
            "onboarding", "training", "career path",
        ]
    
    def detect(self, text: str) -> Tuple[bool, str, float]:
        """
        Detect scope violations.
        
        Args:
            text: Input text
        
        Returns:
            (is_out_of_scope, domain, confidence)
        """
        text_lower = text.lower().strip()
        
        # Check if clearly in-scope
        in_scope_matches = sum(
            1 for keyword in self._in_scope_keywords
            if keyword in text_lower
        )
        
        # Strong in-scope signal
        if in_scope_matches >= 2:
            return False, "in_scope", 0.0
        
        # Check off-topic domains
        for domain, keywords in self._off_topic_domains.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches >= 2:  # Need multiple matches for confidence
                logger.warning(f"Off-topic request detected: {domain}")
                return True, domain, 0.8
            elif matches == 1 and in_scope_matches == 0:
                # Single match with no in-scope signal
                return True, domain, 0.6
        
        # Check unsupported HR topics
        unsupported_matches = sum(
            1 for keyword in self._unsupported_hr
            if keyword in text_lower
        )
        
        if unsupported_matches >= 1 and in_scope_matches == 0:
            logger.warning("Unsupported HR topic detected")
            return True, "unsupported_hr", 0.7
        
        # Weak in-scope signal (1 match)
        if in_scope_matches == 1:
            return False, "in_scope", 0.0
        
        # No clear signal - could be ambiguous
        if len(text_lower) < 10:
            # Very short query, likely greeting or unclear
            return False, "unclear", 0.0
        
        # No matches at all - likely out of scope
        return True, "unknown", 0.5
