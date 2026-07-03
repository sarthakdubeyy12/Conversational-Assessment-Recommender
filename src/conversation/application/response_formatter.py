"""Response formatting logic."""

from typing import List, Dict, Any


class ResponseFormatter:
    """Formats responses to match API schema."""
    
    def format_response(
        self,
        reply: str,
        recommendations: List[Dict[str, Any]],
        end_of_conversation: bool
    ) -> dict:
        pass
