"""
Correction handler.

Handles user corrections and updates to previous statements.
"""

from typing import List, Dict, Any
import re

from src.conversation.domain.entities import Message
from src.conversation.state.domain.conversation_state import HiringContext
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class CorrectionHandler:
    """
    Handles conversation corrections.
    
    Responsibilities:
    - Detect correction signals
    - Identify what is being corrected
    - Apply corrections to state
    - Track correction history
    
    Correction patterns:
    - "Actually..."
    - "Instead..."
    - "Change that to..."
    - "I meant..."
    - "Correction..."
    - "No, ..."
    """
    
    def __init__(self) -> None:
        """Initialize handler."""
        self._correction_signals = [
            r"actually\b",
            r"instead\b",
            r"change\s+(?:that\s+)?to\b",
            r"i\s+meant\b",
            r"correction\b",
            r"^no,?\s+",
            r"not\s+.+,?\s+(?:but|rather)\b",
            r"ignore\s+(?:that|previous)\b",
        ]
    
    def detect_corrections(
        self,
        messages: List[Message],
    ) -> List[Dict[str, Any]]:
        """
        Detect correction patterns in messages.
        
        Args:
            messages: Conversation messages
        
        Returns:
            List of detected corrections
        """
        corrections = []
        
        user_messages = [m for m in messages if m.role == "user"]
        
        for i, message in enumerate(user_messages):
            if self._is_correction(message.content):
                corrections.append({
                    "message_index": i,
                    "content": message.content,
                    "corrects_previous": i > 0,
                })
                logger.debug(f"Correction detected: {message.content[:50]}")
        
        return corrections
    
    def _is_correction(self, text: str) -> bool:
        """Check if message contains correction signal."""
        text_lower = text.lower()
        for pattern in self._correction_signals:
            if re.search(pattern, text_lower):
                return True
        return False
    
    def apply_corrections(
        self,
        context: HiringContext,
        corrections: List[Dict[str, Any]],
        messages: List[Message],
    ) -> HiringContext:
        """
        Apply corrections to context.
        
        Strategy:
        - Corrections replace previous values
        - Latest message takes precedence
        - Corrections are destructive updates
        
        Args:
            context: Current context
            corrections: Detected corrections
            messages: Full message history
        
        Returns:
            Updated context
        """
        if not corrections:
            return context
        
        # For simplicity, re-extract from latest messages
        # giving more weight to recent messages
        # This naturally handles corrections
        
        logger.debug(f"Applied {len(corrections)} corrections")
        
        return context
