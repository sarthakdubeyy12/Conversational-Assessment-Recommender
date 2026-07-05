"""
Pattern matcher.

Pattern-based intent detection.
"""

import re
from typing import List, Tuple, Optional


class PatternMatcher:
    """
    Pattern-based intent matching.
    
    Responsibilities:
    - Match regex patterns against text
    - Return matched patterns with scores
    - Support multiple pattern sets
    
    Design:
    - Deterministic pattern matching
    - Configurable patterns
    - Case-insensitive by default
    """
    
    def __init__(self) -> None:
        """Initialize with pattern library."""
        # Greeting patterns
        self._greeting_patterns = [
            r"^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening))[\s!.]*$",
            r"^(hi|hello|hey)\s+(there|kiro|assistant)[\s!.]*$",
        ]
        
        # Comparison patterns
        self._comparison_patterns = [
            r"\b(compare|comparison|difference|vs|versus)\b",
            r"\b(which\s+is\s+better|better\s+than)\b",
            r"\b(how\s+do\s+they\s+differ|what'?s\s+the\s+difference)\b",
        ]
        
        # Refinement patterns
        self._refinement_patterns = [
            r"\b(actually|instead|change|update|modify)\b",
            r"\b(also\s+include|also\s+add|add\s+to)\b",
            r"\b(remove|exclude|without|don'?t\s+need)\b",
            r"\b(only|just|must\s+have|required)\b",
        ]
        
        # Completion patterns
        self._completion_patterns = [
            r"^(thanks?|thank\s+you)[\s,!.]*",
            r"\b(that'?s\s+all|that'?s\s+it|i'?m\s+done|all\s+done|done|perfect|great)\b",
            r"^(no\s+more\s+questions|i'?m\s+good)[\s!.]*$",
            r"^(bye|goodbye|see\s+you)[\s!.]*$",
        ]
        
        # Recommendation request patterns
        self._recommendation_patterns = [
            r"\b(recommend|suggest|what\s+assessments?|which\s+tests?)\b",
            r"\b(need|want|looking\s+for)\b.*\b(assessments?|tests?)\b",
            r"\b(need|want)\s+to\s+(assess|evaluate|measure|test)\b",  # "need to assess"
            r"\b(give\s+me|show\s+me|find\s+me)\b",
            r"\b(hiring|recruit|looking\s+for)\b.*\b(senior|junior|developer|engineer|manager|analyst|designer)\b",
        ]
    
    def match_greeting(self, text: str) -> Tuple[bool, List[str]]:
        """Match greeting patterns."""
        return self._match_patterns(text, self._greeting_patterns)
    
    def match_comparison(self, text: str) -> Tuple[bool, List[str]]:
        """Match comparison patterns."""
        return self._match_patterns(text, self._comparison_patterns)
    
    def match_refinement(self, text: str) -> Tuple[bool, List[str]]:
        """Match refinement patterns."""
        return self._match_patterns(text, self._refinement_patterns)
    
    def match_completion(self, text: str) -> Tuple[bool, List[str]]:
        """Match completion patterns."""
        return self._match_patterns(text, self._completion_patterns)
    
    def match_recommendation(self, text: str) -> Tuple[bool, List[str]]:
        """Match recommendation patterns."""
        return self._match_patterns(text, self._recommendation_patterns)
    
    def _match_patterns(
        self,
        text: str,
        patterns: List[str],
    ) -> Tuple[bool, List[str]]:
        """
        Match text against patterns.
        
        Args:
            text: Input text
            patterns: List of regex patterns
        
        Returns:
            (matched, list of matched patterns)
        """
        text_lower = text.lower().strip()
        matched_patterns = []
        
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                matched_patterns.append(pattern)
        
        return len(matched_patterns) > 0, matched_patterns
