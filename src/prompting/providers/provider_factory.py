"""
LLM provider factory.

Creates and configures LLM provider instances based on configuration.
"""

from typing import Optional
from src.prompting.providers.base_provider import BaseLLMProvider
from src.prompting.providers.openai_provider import OpenAIProvider
from src.prompting.providers.groq_provider import GroqProvider
from src.shared.config.settings import get_settings
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ProviderFactory:
    """
    Factory for creating LLM providers.
    
    Responsibilities:
    - Create provider instances based on configuration
    - Validate API keys
    - Provide fallback providers
    - Startup validation
    
    Design:
    - Configuration-driven
    - Fail-fast validation
    - Clear error messages
    """
    
    @staticmethod
    def create_provider(
        provider_name: Optional[str] = None,
        model: Optional[str] = None,
    ) -> BaseLLMProvider:
        """
        Create LLM provider instance.
        
        Args:
            provider_name: Provider name (openai, groq, etc.)
            model: Model name (overrides config)
        
        Returns:
            Configured provider instance
        
        Raises:
            ValueError: If provider configuration is invalid
        """
        settings = get_settings()
        
        # Use settings if not specified
        provider_name = provider_name or settings.llm_provider
        model = model or settings.llm_model
        
        logger.info(f"Creating LLM provider: {provider_name}, model: {model}")
        
        # Create provider based on name
        if provider_name == "openai":
            return ProviderFactory._create_openai_provider(model, settings)
        
        elif provider_name == "groq":
            return ProviderFactory._create_groq_provider(model, settings)
        
        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider_name}. "
                f"Supported providers: openai, groq"
            )
    
    @staticmethod
    def _create_openai_provider(model: str, settings) -> OpenAIProvider:
        """Create OpenAI provider."""
        api_key = settings.openai_api_key
        
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured. "
                "Set OPENAI_API_KEY environment variable or update .env file."
            )
        
        provider = OpenAIProvider(
            api_key=api_key,
            model=model,
            timeout=settings.llm_timeout,
            max_retries=2,
        )
        
        provider.validate_configuration()
        return provider
    
    @staticmethod
    def _create_groq_provider(model: str, settings) -> GroqProvider:
        """Create Groq provider."""
        api_key = settings.groq_api_key
        
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured. "
                "Set GROQ_API_KEY environment variable or update .env file."
            )
        
        provider = GroqProvider(
            api_key=api_key,
            model=model,
            timeout=settings.llm_timeout,
            max_retries=2,
        )
        
        provider.validate_configuration()
        return provider
    
    @staticmethod
    def validate_provider_configuration() -> None:
        """
        Validate that the configured provider has the required API key.
        
        This should be called at application startup to fail fast
        if configuration is invalid.
        
        Raises:
            ValueError: If provider configuration is invalid
        """
        settings = get_settings()
        provider_name = settings.llm_provider
        
        logger.info(f"Validating provider configuration: {provider_name}")
        
        # Check API key is present
        if provider_name == "openai":
            if not settings.openai_api_key:
                raise ValueError(
                    "LLM_PROVIDER is set to 'openai' but OPENAI_API_KEY is missing. "
                    "Please set OPENAI_API_KEY in your environment or .env file."
                )
        
        elif provider_name == "groq":
            if not settings.groq_api_key:
                raise ValueError(
                    "LLM_PROVIDER is set to 'groq' but GROQ_API_KEY is missing. "
                    "Please set GROQ_API_KEY in your environment or .env file."
                )
        
        else:
            raise ValueError(
                f"Invalid LLM_PROVIDER: {provider_name}. "
                f"Supported providers: openai, groq"
            )
        
        logger.info(f"✓ Provider configuration valid: {provider_name}")
