"""LLM provider configurations."""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


class LLMProvider(str, Enum):
    """
    Supported LLM providers.
    
    Extensible enum for adding new providers.
    """
    
    OPENAI = "openai"
    GEMINI = "gemini"
    GROQ = "groq"


@dataclass(frozen=True)
class ProviderConfig:
    """
    Provider-specific configuration.
    
    Immutable configuration for each provider.
    """
    
    name: str
    api_base_url: Optional[str]
    default_model: str
    max_tokens: int
    supports_streaming: bool
    supports_function_calling: bool


class LLMConfig:
    """
    LLM configuration manager.
    
    Centralizes provider-specific configurations.
    Makes it easy to add new providers.
    """
    
    _PROVIDER_CONFIGS: Dict[LLMProvider, ProviderConfig] = {
        LLMProvider.OPENAI: ProviderConfig(
            name="OpenAI",
            api_base_url="https://api.openai.com/v1",
            default_model="gpt-4",
            max_tokens=4096,
            supports_streaming=True,
            supports_function_calling=True,
        ),
        LLMProvider.GEMINI: ProviderConfig(
            name="Google Gemini",
            api_base_url="https://generativelanguage.googleapis.com",
            default_model="gemini-pro",
            max_tokens=2048,
            supports_streaming=True,
            supports_function_calling=False,
        ),
        LLMProvider.GROQ: ProviderConfig(
            name="Groq",
            api_base_url="https://api.groq.com/openai/v1",
            default_model="llama-3.1-70b-versatile",
            max_tokens=8192,
            supports_streaming=True,
            supports_function_calling=False,
        ),
    }
    
    @classmethod
    def get_provider_config(cls, provider: LLMProvider) -> ProviderConfig:
        """Get configuration for specific provider."""
        if provider not in cls._PROVIDER_CONFIGS:
            raise ValueError(f"Unknown provider: {provider}")
        return cls._PROVIDER_CONFIGS[provider]
    
    @classmethod
    def is_provider_supported(cls, provider: str) -> bool:
        """Check if provider is supported."""
        try:
            LLMProvider(provider)
            return True
        except ValueError:
            return False
    
    @classmethod
    def get_all_providers(cls) -> list[LLMProvider]:
        """Get list of all supported providers."""
        return list(cls._PROVIDER_CONFIGS.keys())
