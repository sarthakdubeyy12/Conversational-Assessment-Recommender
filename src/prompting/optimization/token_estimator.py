"""
Token estimator.

Estimates token counts for prompts to optimize LLM costs and stay within limits.
"""

import re
from typing import List


class TokenEstimator:
    """
    Estimates token counts for text.
    
    Uses approximation: ~0.75 tokens per word (GPT-style tokenization).
    More accurate than character count, faster than tiktoken.
    
    Responsibilities:
    - Estimate input token counts
    - Estimate output token budgets
    - Validate against token limits
    
    Design:
    - Fast approximation
    - Provider-agnostic
    - Conservative estimates
    """
    
    # Approximation factors
    TOKENS_PER_WORD = 0.75
    TOKENS_PER_CHAR = 0.25  # For non-English or technical text
    
    # Common provider limits
    PROVIDER_LIMITS = {
        "openai": {
            "gpt-4": 8192,
            "gpt-4-turbo": 128000,
            "gpt-3.5-turbo": 16385,
        },
        "groq": {
            "llama": 8192,
            "mixtral": 32768,
        },
        "gemini": {
            "gemini-pro": 30720,
        },
        "anthropic": {
            "claude": 100000,
        },
    }
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text to estimate
        
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        
        # Count words (split on whitespace)
        words = text.split()
        word_count = len(words)
        
        # Estimate tokens (conservative)
        estimated_tokens = int(word_count * self.TOKENS_PER_WORD)
        
        # Add buffer for special tokens and formatting
        buffer = max(10, int(estimated_tokens * 0.1))
        
        return estimated_tokens + buffer
    
    def estimate_prompt_package_tokens(
        self,
        system_prompt: str,
        user_prompt: str,
        conversation_history: List[dict] = None,
    ) -> tuple:
        """
        Estimate total tokens for a complete prompt package.
        
        Args:
            system_prompt: System prompt text
            user_prompt: User prompt text
            conversation_history: Optional conversation history
        
        Returns:
            Tuple of (input_tokens, estimated_output_tokens)
        """
        # Estimate system prompt
        system_tokens = self.estimate_tokens(system_prompt)
        
        # Estimate user prompt
        user_tokens = self.estimate_tokens(user_prompt)
        
        # Estimate history
        history_tokens = 0
        if conversation_history:
            for msg in conversation_history:
                content = msg.get("content", "")
                history_tokens += self.estimate_tokens(content)
        
        # Total input tokens
        input_tokens = system_tokens + user_tokens + history_tokens
        
        # Estimate output tokens (typically 200-500 for responses)
        # Use 300 as conservative estimate
        estimated_output_tokens = 300
        
        return input_tokens, estimated_output_tokens
    
    def validate_token_budget(
        self,
        input_tokens: int,
        output_tokens: int,
        provider: str,
        model: str,
    ) -> bool:
        """
        Validate if token counts are within provider limits.
        
        Args:
            input_tokens: Estimated input tokens
            output_tokens: Estimated output tokens
            provider: Provider name
            model: Model name
        
        Returns:
            True if within limits, False otherwise
        """
        # Get provider limit
        provider_models = self.PROVIDER_LIMITS.get(provider.lower(), {})
        
        # Find model limit (check partial matches)
        model_limit = None
        for model_key, limit in provider_models.items():
            if model_key in model.lower():
                model_limit = limit
                break
        
        # Default to 8K if unknown
        if model_limit is None:
            model_limit = 8192
        
        # Check if total tokens fit
        total_tokens = input_tokens + output_tokens
        return total_tokens <= model_limit
    
    def get_max_output_tokens(
        self,
        input_tokens: int,
        provider: str,
        model: str,
    ) -> int:
        """
        Calculate maximum output tokens given input size.
        
        Args:
            input_tokens: Input token count
            provider: Provider name
            model: Model name
        
        Returns:
            Maximum output tokens
        """
        # Get provider limit
        provider_models = self.PROVIDER_LIMITS.get(provider.lower(), {})
        
        model_limit = None
        for model_key, limit in provider_models.items():
            if model_key in model.lower():
                model_limit = limit
                break
        
        if model_limit is None:
            model_limit = 8192
        
        # Calculate remaining budget
        remaining = model_limit - input_tokens
        
        # Return safe maximum (with 10% buffer)
        return max(100, int(remaining * 0.9))
