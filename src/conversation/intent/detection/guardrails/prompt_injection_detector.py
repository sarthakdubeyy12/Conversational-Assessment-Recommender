"""
Prompt injection detector.

Detects prompt injection and jailbreak attempts.
"""

import re
from typing import Tuple, List


class PromptInjectionDetector:
    """
    Detects prompt injection attacks.
    
    Responsibilities:
    - Detect system prompt manipulation attempts
    - Detect roleplay attacks
    - Detect instruction override attempts
    - Detect jailbreak patterns
    
    Design:
    - Pattern-based detection
    - Multiple attack vectors
    - High sensitivity for security
    """
    
    def __init__(self) -> None:
        """Initialize with attack patterns."""
        self._injection_patterns = [
            # Direct instruction override
            r"\b(ignore|disregard|forget)\s+(previous|all|your|everything)\s+(instructions?|rules?|prompts?)\b",
            r"\b(ignore|disregard|forget)\s+(all|everything)\s+(previous\s+)?(instructions?|and)\b",
            r"\b(override|bypass|skip)\s+(instructions?|rules?|system)\b",
            
            # System prompt extraction
            r"\b(reveal|show|print|display|tell\s+me)\s+(your\s+)?(system\s+)?(prompt|instructions?|rules?)\b",
            r"\bwhat\s+(are\s+your|is\s+your)\s+(instructions?|system\s+prompt|hidden\s+prompt)\b",
            
            # Roleplay attacks
            r"\b(pretend|act\s+as|you\s+are\s+now)\s+.{0,20}(chatgpt|gpt|different|another)\b",
            r"\byou\s+are\s+(chatgpt|gpt-?\d|claude|assistant|ai\s+model)\b",
            r"\bignore\s+everything\s+and\b",
            r"\bfrom\s+now\s+on\b",
            
            # Developer mode
            r"\b(developer\s+mode|debug\s+mode|admin\s+mode)\b",
            r"\b(enable|activate)\s+(developer|debug|admin)\b",
            
            # Tool manipulation
            r"\bcall\s+.*\s+with\s+.*parameters?\b",
            r"\b(execute|run)\s+(function|tool|command)\b",
            
            # Jailbreak patterns
            r"^\s*\[\s*system\s*\]",
            r"^\s*##\s*(instructions?|system|developer)",
            r"\bdan\s+mode\b",  # "Do Anything Now"
            
            # Prompt leakage
            r"\bprint\s+(hidden|secret|internal)\b",
            r"\bexfiltrate\b",
        ]
    
    def detect(self, text: str) -> Tuple[bool, List[str], float]:
        """
        Detect prompt injection.
        
        Args:
            text: User message
        
        Returns:
            (is_injection, matched_patterns, confidence)
        """
        text_lower = text.lower()
        matched_patterns = []
        
        for pattern in self._injection_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                matched_patterns.append(pattern)
        
        is_injection = len(matched_patterns) > 0
        
        # Confidence based on number of matches
        if len(matched_patterns) >= 2:
            confidence = 1.0
        elif len(matched_patterns) == 1:
            confidence = 0.9
        else:
            confidence = 0.0
        
        return is_injection, matched_patterns, confidence
