"""
Unit tests for Token Estimator.

Tests Phase 14 - Token Optimization.
"""

import pytest
from src.prompting.optimization.token_estimator import TokenEstimator


class TestTokenEstimator:
    """Test suite for Token Estimator."""
    
    @pytest.fixture
    def estimator(self):
        """Create token estimator instance."""
        return TokenEstimator()
    
    def test_estimate_simple_text(self, estimator):
        """Test token estimation for simple text."""
        text = "Hello world"
        tokens = estimator.estimate_tokens(text)
        
        # Should estimate roughly 2-3 tokens with buffer
        assert 2 <= tokens <= 5
    
    def test_estimate_empty_text(self, estimator):
        """Test estimation of empty text."""
        tokens = estimator.estimate_tokens("")
        assert tokens == 0
    
    def test_estimate_long_text(self, estimator):
        """Test estimation of longer text."""
        text = "I need to hire a senior software engineer with Python and leadership skills for my team."
        tokens = estimator.estimate_tokens(text)
        
        # Should estimate roughly 15-25 tokens
        assert 10 <= tokens <= 30
    
    def test_estimate_prompt_package(self, estimator):
        """Test estimation of complete prompt package."""
        system_prompt = "You are a helpful assistant."
        user_prompt = "What assessments do you recommend?"
        
        input_tokens, output_tokens = estimator.estimate_prompt_package_tokens(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
        
        assert input_tokens > 0
        assert output_tokens == 300  # Default estimate
        assert input_tokens < output_tokens  # Typically output longer
    
    def test_validate_within_budget(self, estimator):
        """Test budget validation - within limits."""
        is_valid = estimator.validate_token_budget(
            input_tokens=1000,
            output_tokens=500,
            provider="groq",
            model="llama-3.3-70b-versatile",
        )
        
        assert is_valid is True
    
    def test_validate_exceeds_budget(self, estimator):
        """Test budget validation - exceeds limits."""
        is_valid = estimator.validate_token_budget(
            input_tokens=50000,
            output_tokens=50000,
            provider="groq",
            model="llama-3.3-70b-versatile",
        )
        
        assert is_valid is False
    
    def test_get_max_output_tokens(self, estimator):
        """Test calculation of max output tokens."""
        input_tokens = 1000
        max_output = estimator.get_max_output_tokens(
            input_tokens=input_tokens,
            provider="groq",
            model="llama-3.3-70b-versatile",
        )
        
        assert max_output > 0
        assert max_output < 8192  # Should be less than total limit
    
    def test_deterministic_estimation(self, estimator):
        """Test estimation is deterministic."""
        text = "I need to assess problem-solving skills"
        
        tokens1 = estimator.estimate_tokens(text)
        tokens2 = estimator.estimate_tokens(text)
        tokens3 = estimator.estimate_tokens(text)
        
        assert tokens1 == tokens2 == tokens3
    
    def test_provider_limits_known(self, estimator):
        """Test provider limits are correctly defined."""
        # Check Groq limits
        assert "groq" in estimator.PROVIDER_LIMITS
        assert "llama" in estimator.PROVIDER_LIMITS["groq"]
        
        # Check OpenAI limits
        assert "openai" in estimator.PROVIDER_LIMITS
        assert "gpt-4" in estimator.PROVIDER_LIMITS["openai"]
