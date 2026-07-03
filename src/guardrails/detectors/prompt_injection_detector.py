"""
Prompt injection detector.

Detects attempts to manipulate system behavior through malicious input.
"""

import re
from typing import Tuple, List, Optional
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class PromptInjectionDetector:
    """
    Detect prompt injection attacks.
    
    Responsibilities:
    - Detect instruction override attempts
    - Detect system prompt extraction
    - Detect role manipulation
    - Detect jailbreak patterns
    
    Design:
    - Pattern-based detection
    - No ML dependencies
    - Deterministic output
    - Fast execution
    """
    
    def __init__(self) -> None:
        """Initialize detector with patterns."""
        # Instruction override patterns
        self._instruction_patterns = [
            r"ignore\s+(previous|all|your)\s+(instructions?|prompts?|rules?)",
            r"forget\s+(everything|all|previous)",
            r"disregard\s+(previous|all|your)\s+(instructions?|commands?)",
            r"override\s+(system|instructions?|settings?)",
            r"new\s+(instructions?|task|directive)",
        ]
        
        # System prompt extraction patterns
        self._extraction_patterns = [
            r"(reveal|show|display|print|output|return)\s+(your|the|my)?\s*(hidden|internal)?\s*(system|initial|base)?\s*(prompt|instructions?)",
            r"what\s+(is|are|was)\s+your\s+(system|initial|original)\s+(prompt|instructions?)",
            r"(repeat|echo|output)\s+your\s+(instructions?|prompt)",
            r"show\s+me\s+(your|the)?\s*(hidden|internal|developer)?\s*(instructions?|prompt|settings?)",
            r"(print|display|output)\s+(hidden|your)\s+(instructions?|prompt)",
        ]
        
        # Role manipulation patterns
        self._role_patterns = [
            r"(act|pretend|roleplay|behave)\s+as\s+(if\s+)?(you\s+are\s+)?(?:a\s+)?(chatgpt|gpt|assistant|ai|dan|unrestricted)",
            r"you\s+are\s+now\s+(a\s+)?(different|new|another|unrestricted)",
            r"(enter|enable|activate)\s+(developer|debug|admin|god)\s+mode",
            r"switch\s+to\s+(developer|unrestricted|jailbreak)",
        ]
        
        # Tool manipulation patterns
        self._tool_patterns = [
            r"(call|access|use|invoke)\s+(internal|hidden|private)\s+(api|function|tool|method)",
            r"(bypass|skip|ignore)\s+(validation|safety|guardrails?|checks?)",
            r"(modify|change|alter)\s+(retrieval|database|catalog|memory)",
            r"access\s+(raw|hidden|internal)\s+(data|memory|storage)",
        ]
        
        # Compile patterns
        self._all_patterns = (
            self._instruction_patterns
            + self._extraction_patterns
            + self._role_patterns
            + self._tool_patterns
        )
        self._compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self._all_patterns
        ]
    
    def detect(self, text: str) -> Tuple[bool, float, List[str]]:
        """
        Detect prompt injection in text.
        
        Args:
            text: Input text to analyze
        
        Returns:
            (is_injection, confidence, trigger_phrases)
        """
        text_lower = text.lower().strip()
        
        # Quick length check
        if len(text_lower) < 5:
            return False, 0.0, []
        
        # Check against all patterns
        trigger_phrases = []
        matches = 0
        
        for pattern in self._compiled_patterns:
            match = pattern.search(text_lower)
            if match:
                trigger_phrases.append(match.group(0))
                matches += 1
        
        # Calculate confidence
        if matches == 0:
            return False, 0.0, []
        
        # Higher matches = higher confidence
        confidence = min(0.5 + (matches * 0.2), 1.0)
        
        is_injection = matches > 0
        
        if is_injection:
            logger.warning(
                f"Prompt injection detected: {matches} patterns matched"
            )
        
        return is_injection, confidence, trigger_phrases[:3]  # Top 3
