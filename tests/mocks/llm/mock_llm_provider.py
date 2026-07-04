"""
Mock LLM provider for testing.

Provides deterministic responses without calling real APIs.
"""

from typing import Dict, Any
from src.prompting.providers.base_provider import BaseLLMProvider
from src.prompting.models.prompt_package import PromptPackage
from src.prompting.models.provider_response import ProviderResponse


class MockLLMProvider(BaseLLMProvider):
    """
    Mock LLM provider for testing.
    
    Returns predefined responses without making API calls.
    
    Design:
    - Deterministic responses
    - Configurable behavior
    - No network calls
    - Fast execution
    """
    
    def __init__(
        self,
        response_content: str = "Mock LLM response",
        should_fail: bool = False,
        latency_ms: float = 10.0,
    ) -> None:
        """
        Initialize mock provider.
        
        Args:
            response_content: Content to return
            should_fail: Whether to simulate failure
            latency_ms: Simulated latency
        """
        super().__init__(api_key="mock-key", model="mock-model")
        self._response_content = response_content
        self._should_fail = should_fail
        self._latency_ms = latency_ms
        self._call_count = 0
    
    def validate_configuration(self) -> None:
        """Validate mock configuration (always valid)."""
        pass
    
    async def generate(
        self,
        prompt_package: PromptPackage,
    ) -> ProviderResponse:
        """
        Generate mock response.
        
        Args:
            prompt_package: Prompt package
        
        Returns:
            Mock provider response
        """
        self._call_count += 1
        
        if self._should_fail:
            return ProviderResponse(
                content="",
                provider="mock",
                model="mock-model",
                success=False,
                error="Mock provider failure",
                latency_ms=self._latency_ms,
            )
        
        return ProviderResponse(
            content=self._response_content,
            raw_response={"mock": True},
            provider="mock",
            model="mock-model",
            input_tokens=50,
            output_tokens=20,
            total_tokens=70,
            latency_ms=self._latency_ms,
            success=True,
        )
    
    def get_call_count(self) -> int:
        """Get number of times generate was called."""
        return self._call_count
    
    def set_response(self, content: str) -> None:
        """Set response content."""
        self._response_content = content
    
    def set_should_fail(self, should_fail: bool) -> None:
        """Set failure behavior."""
        self._should_fail = should_fail
