"""LLM client implementation."""

from typing import List

from src.conversation.domain.interfaces import ILLMClient


class LLMClient(ILLMClient):
    """Multi-provider LLM client."""
    
    def __init__(self, provider: str, api_key: str) -> None:
        self._provider = provider
        self._api_key = api_key
    
    async def generate(self, messages: List[dict], system_prompt: str) -> str:
        pass
