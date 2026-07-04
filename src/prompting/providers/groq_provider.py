"""
Groq LLM provider.

Implementation for Groq's LLM API.
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


class GroqProvider(BaseLLMProvider):
    """
    Groq LLM provider implementation.
    
    Supports Groq's fast inference API with models like:
    - llama-3.1-70b-versatile
    - mixtral-8x7b-32768
    - gemma-7b-it
    
    Design:
    - Uses httpx for async requests
    - Implements retry logic
    - Handles rate limiting
    - Extracts usage metrics
    """
    
    API_BASE = "https://api.groq.com/openai/v1"
    
    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-70b-versatile",
        timeout: int = 30,
        max_retries: int = 2,
    ) -> None:
        """
        Initialize Groq provider.
        
        Args:
            api_key: Groq API key
            model: Model name
            timeout: Request timeout
            max_retries: Maximum retries
        """
        super().__init__(api_key, model, timeout, max_retries)
        self._client = None
    
    def validate_configuration(self) -> None:
        """Validate Groq configuration."""
        if not self._api_key:
            raise ValueError("Groq API key is required")
        
        if not self._model:
            raise ValueError("Groq model name is required")
        
        logger.info(f"Groq provider configured with model: {self._model}")
    
    async def generate(
        self,
        prompt_package: PromptPackage,
    ) -> ProviderResponse:
        """
        Generate response using Groq API.
        
        Args:
            prompt_package: Prompt package
        
        Returns:
            Provider response
        """
        start_time = time.time()
        retry_count = 0
        last_error = None
        
        while retry_count <= self._max_retries:
            try:
                # Build request
                request_data = self._build_request(prompt_package)
                
                # Make API call
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
                
                # Parse response
                latency_ms = (time.time() - start_time) * 1000
                return self._parse_response(result, latency_ms, retry_count)
                
            except httpx.TimeoutException as e:
                last_error = f"Timeout: {e}"
                retry_count += 1
                logger.warning(f"Groq timeout, retry {retry_count}/{self._max_retries}")
                
            except httpx.HTTPStatusError as e:
                error_body = ""
                try:
                    error_body = e.response.text
                except:
                    pass
                last_error = f"HTTP {e.response.status_code}: {e} | Body: {error_body}"
                logger.error(f"Groq HTTP error: {last_error}")
                
                if e.response.status_code == 429:  # Rate limit
                    retry_count += 1
                    await asyncio.sleep(1)  # Brief backoff
                    logger.warning(f"Groq rate limit, retry {retry_count}/{self._max_retries}")
                else:
                    break  # Don't retry other HTTP errors
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"Groq error: {e}", exc_info=True)
                break
        
        # All retries failed
        latency_ms = (time.time() - start_time) * 1000
        return ProviderResponse(
            content="",
            provider="groq",
            model=self._model,
            success=False,
            error=last_error,
            latency_ms=latency_ms,
            retry_count=retry_count,
        )
    
    def _build_request(self, prompt_package: PromptPackage) -> Dict[str, Any]:
        """Build Groq API request."""
        messages = [
            {"role": "system", "content": prompt_package.system_prompt},
        ]
        
        # Add conversation history
        if prompt_package.conversation_history:
            messages.extend(prompt_package.conversation_history)
        
        # Add current user message
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
        """Parse Groq API response."""
        try:
            content = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            
            return ProviderResponse(
                content=content,
                raw_response=result,
                provider="groq",
                model=self._model,
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
                latency_ms=latency_ms,
                success=True,
                retry_count=retry_count,
            )
            
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse Groq response: {e}")
            return ProviderResponse(
                content="",
                provider="groq",
                model=self._model,
                success=False,
                error=f"Response parsing error: {e}",
                latency_ms=latency_ms,
                retry_count=retry_count,
            )
