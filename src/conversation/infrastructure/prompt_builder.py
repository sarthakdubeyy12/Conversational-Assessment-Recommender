"""Prompt construction."""

from typing import List, Dict, Any


class PromptBuilder:
    """Builds prompts for LLM."""
    
    def build_system_prompt(self, context: str) -> str:
        pass
    
    def build_user_prompt(self, criteria: Dict[str, Any]) -> str:
        pass
