"""LLM provider configurations."""

from enum import Enum
from typing import Dict, Any


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    
    OPENAI = "openai"
    GEMINI = "gemini"
    GROQ = "groq"


class LLMConfig:
    """LLM configuration manager."""
    
    @staticmethod
    def get_provider_config(provider: LLMProvider) -> Dict[str, Any]:
        pass
