"""
Unit tests for System Prompt Builder.

Tests Phase 14 - System Prompt Generation.
"""

import pytest
from src.prompting.builders.system_prompt_builder import SystemPromptBuilder


class TestSystemPromptBuilder:
    """Test suite for System Prompt Builder."""
    
    @pytest.fixture
    def builder(self):
        """Create system prompt builder."""
        return SystemPromptBuilder(catalog_count=15)
    
    def test_build_system_prompt(self, builder):
        """Test system prompt generation."""
        prompt = builder.build()
        
        assert len(prompt) > 0
        assert isinstance(prompt, str)
    
    def test_contains_identity(self, builder):
        """Test prompt contains assistant identity."""
        prompt = builder.build()
        
        assert "SHL" in prompt
        assert "Assessment" in prompt or "assessment" in prompt
    
    def test_contains_scope(self, builder):
        """Test prompt defines scope."""
        prompt = builder.build()
        
        assert "catalog" in prompt.lower()
        assert "only" in prompt.lower() or "ONLY" in prompt
    
    def test_contains_safety_rules(self, builder):
        """Test prompt contains safety rules."""
        prompt = builder.build()
        
        assert "never" in prompt.lower() or "NEVER" in prompt
        assert "hallucin" in prompt.lower() or "invent" in prompt.lower()
    
    def test_contains_url_instruction(self, builder):
        """Test prompt mentions URL handling."""
        prompt = builder.build()
        
        assert "URL" in prompt or "url" in prompt
    
    def test_contains_grounding_instruction(self, builder):
        """Test prompt emphasizes catalog grounding."""
        prompt = builder.build()
        
        grounding_keywords = ["provided", "context", "catalog", "retrieved"]
        assert any(keyword in prompt.lower() for keyword in grounding_keywords)
    
    def test_deterministic_generation(self, builder):
        """Test prompt generation is deterministic."""
        prompt1 = builder.build()
        prompt2 = builder.build()
        prompt3 = builder.build()
        
        assert prompt1 == prompt2 == prompt3
    
    def test_catalog_count_included(self):
        """Test catalog count is included when provided."""
        builder = SystemPromptBuilder(catalog_count=25)
        prompt = builder.build()
        
        assert "25" in prompt or "catalog" in prompt.lower()
    
    def test_without_catalog_count(self):
        """Test prompt builds without catalog count."""
        builder = SystemPromptBuilder(catalog_count=None)
        prompt = builder.build()
        
        assert len(prompt) > 0
        assert "catalog" in prompt.lower()
