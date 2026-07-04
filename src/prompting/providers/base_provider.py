"""
Base LLM provider interface.

Defines the contract all LLM providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from src.prompting.models.prompt_package import PromptPackage
from src.prompting.models.provider_response import ProviderResponse


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All provider implementations must inherit from this class
    and implement the required methods.
    
    Design:
    - Provider-agnostic interface
    - Consistent error handling
    - Retry logic support
    - Timeout support
    """
    
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: int = 30,
        max_retries: int = 2,
    ) -> None:
        """
        Initialize provider.
        
        Args:
            api_key: API key for provider
            model: Model name/identifier
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self._api_key = api_key
        self._model = model
        self._timeout = timeout
        self._max_retries = max_retries
        self._provider_name = self.__class__.__name__.replace("Provider", "").lower()
    
    @abstractmethod
    async def generate(
        self,
        prompt_package: PromptPackage,
    ) -> ProviderResponse:
        """
        Generate response from LLM.
        
        Args:
            prompt_package: Complete prompt package
        
        Returns:
            Provider response
        
        Raises:
            Exception: On provider errors
        """
        pass
    
    @abstractmethod
    def validate_configuration(self) -> None:
        """
        Validate provider configuration.
        
        Checks API key, model availability, etc.
        
        Raises:
            ValueError: If configuration is invalid
        """
        pass
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return self._provider_name
    
    def get_model(self) -> str:
        """Get model name."""
        return self._model
