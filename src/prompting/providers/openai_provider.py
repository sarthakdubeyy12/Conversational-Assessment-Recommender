"""
OpenAI LLM provider.

Implementation for OpenAI's API (GPT models).
"""

import time
import asyncio
import httpx
from typing import Dict, Any
from src.prompting.providers.base_provider import BaseLLMProvider
from src.prompting.models.prompt_package import PromptPackage
from src.prompting.models.provider_response import ProviderResponse
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI LLM provider implementation.
    
    Supports OpenAI models like:
    - gpt-4
    - gpt-4-turbo
    - gpt-3.5-turbo
    
    Design:
    - Uses httpx for async requests
    - Implements retry logic
    - Handles rate limiting
    - Extracts usage metrics
    """
    
    API_BASE = "https://api.openai.com/v1"
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        timeout: int = 30,
        max_retries: int = 2,
    ) -> None:
        """Initialize OpenAI provider."""
        super().__init__(api_key, model, timeout, max_retries)
    
    def validate_configuration(self) -> None:
        """Validate OpenAI configuration."""
        if not self._api_key:
            raise ValueError("OpenAI API key is required")
        
        if not self._model:
            raise ValueError("OpenAI model name is required")
        
        logger.info(f"OpenAI provider configured with model: {self._model}")
    
    async def generate(
        self,
        prompt_package: PromptPackage,
    ) -> ProviderResponse:
        """Generate response using OpenAI API."""
        start_time = time.time()
        retry_count = 0
        last_error = None
        
        while retry_count <= self._max_retries:
            try:
                request_data = self._build_request(prompt_package)
                
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.post(
                        f"{self.API_BASE}/chat/completions",
                        json=request_data,
                        headers={
                            "Authorization": f"Bearer {self._api_key}",
                            "Content-Type": "application/json",
                        },
                    )
                    response.raise_for_status()
                    result = response.json()
                
                latency_ms = (time.time() - start_time) * 1000
                return self._parse_response(result, latency_ms, retry_count)
                
            except httpx.TimeoutException as e:
                last_error = f"Timeout: {e}"
                retry_count += 1
                logger.warning(f"OpenAI timeout, retry {retry_count}/{self._max_retries}")
                
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}: {e}"
                if e.response.status_code == 429:
                    retry_count += 1
                    await asyncio.sleep(2)
                    logger.warning(f"OpenAI rate limit, retry {retry_count}/{self._max_retries}")
                else:
                    break
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"OpenAI error: {e}", exc_info=True)
                break
        
        latency_ms = (time.time() - start_time) * 1000
        return ProviderResponse(
            content="",
            provider="openai",
            model=self._model,
            success=False,
            error=last_error,
            latency_ms=latency_ms,
            retry_count=retry_count,
        )
    
    def _build_request(self, prompt_package: PromptPackage) -> Dict[str, Any]:
        """Build OpenAI API request."""
        messages = [
            {"role": "system", "content": prompt_package.system_prompt},
        ]
        
        if prompt_package.conversation_history:
            messages.extend(prompt_package.conversation_history)
        
        messages.append({"role": "user", "content": prompt_package.user_prompt})
        
        return {
            "model": self._model,
            "messages": messages,
            "temperature": prompt_package.temperature,
            "max_tokens": prompt_package.max_tokens,
        }
    
    def _parse_response(
        self,
        result: Dict[str, Any],
        latency_ms: float,
        retry_count: int,
    ) -> ProviderResponse:
        """Parse OpenAI API response."""
        try:
            content = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            
            return ProviderResponse(
                content=content,
                raw_response=result,
                provider="openai",
                model=self._model,
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
                latency_ms=latency_ms,
                success=True,
                retry_count=retry_count,
            )
            
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            return ProviderResponse(
                content="",
                provider="openai",
                model=self._model,
                success=False,
                error=f"Response parsing error: {e}",
                latency_ms=latency_ms,
                retry_count=retry_count,
            )
