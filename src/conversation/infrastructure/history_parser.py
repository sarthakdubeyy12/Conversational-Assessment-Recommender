"""Message history parsing."""

from typing import List

from src.conversation.domain.entities import Message


class HistoryParser:
    """Parses message history."""
    
    def parse_messages(self, raw_messages: List[dict]) -> List[Message]:
        pass
