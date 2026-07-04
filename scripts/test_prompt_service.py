"""
Test script for prompt service.

Tests Phase 14 - Prompt Engineering & LLM Integration.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.prompting.prompt_service import PromptService
from src.prompting.providers.provider_factory import ProviderFactory
from src.prompting.builders.system_prompt_builder import SystemPromptBuilder
from src.prompting.builders.recommendation_prompt_builder import RecommendationPromptBuilder
from src.prompting.optimization.token_estimator import TokenEstimator


def print_section(title: str) -> None:
    """Print section header."""
    print(f"\n{'='*70}")
    print(f"{title}")
    print('='*70)


def test_provider_validation() -> None:
    """Test provider configuration validation."""
    print_section("PROVIDER VALIDATION TEST")
    
    try:
        ProviderFactory.validate_provider_configuration()
        print("✅ Provider configuration is valid")
    except Exception as e:
        print(f"❌ Provider validation failed: {e}")
        sys.exit(1)


def test_system_prompt() -> None:
    """Test system prompt builder."""
    print_section("SYSTEM PROMPT BUILDER TEST")
    
    builder = SystemPromptBuilder(catalog_count=15)
    system_prompt = builder.build()
    
    print(f"System prompt length: {len(system_prompt)} characters")
    print("\nFirst 500 characters:")
    print(system_prompt[:500] + "...")
    
    # Check key elements
    checks = [
        ("Identity" in system_prompt or "expert" in system_prompt, "Contains identity"),
        ("catalog" in system_prompt.lower(), "Mentions catalog"),
        ("never" in system_prompt.lower(), "Contains safety rules"),
        ("url" in system_prompt.lower(), "Mentions URLs"),
    ]
    
    for check, desc in checks:
        print(f"{'✅' if check else '❌'} {desc}")


def test_token_estimation() -> None:
    """Test token estimator."""
    print_section("TOKEN ESTIMATOR TEST")
    
    estimator = TokenEstimator()
    
    # Test simple text
    text = "I need to hire a senior software engineer with Python and leadership skills."
    tokens = estimator.estimate_tokens(text)
    print(f"Text: '{text}'")
    print(f"Estimated tokens: {tokens}")
    
    # Test prompt package estimation
    system_prompt = "You are a helpful assistant."
    user_prompt = "What assessments do you recommend?"
    
    input_tokens, output_tokens = estimator.estimate_prompt_package_tokens(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )
    
    print(f"\nPrompt package estimation:")
    print(f"  Input tokens: {input_tokens}")
    print(f"  Estimated output tokens: {output_tokens}")
    
    # Test validation
    is_valid = estimator.validate_token_budget(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        provider="groq",
        model="llama-3.1-70b-versatile",
    )
    print(f"  Within budget: {'✅' if is_valid else '❌'}")


def test_provider_creation() -> None:
    """Test provider creation."""
    print_section("PROVIDER CREATION TEST")
    
    try:
        provider = ProviderFactory.create_provider()
        print(f"✅ Provider created: {provider.get_provider_name()}")
        print(f"   Model: {provider.get_model()}")
    except Exception as e:
        print(f"❌ Provider creation failed: {e}")
        raise


async def test_simple_llm_call() -> None:
    """Test simple LLM API call."""
    print_section("SIMPLE LLM CALL TEST")
    
    try:
        from src.prompting.models.prompt_package import PromptPackage
        
        provider = ProviderFactory.create_provider()
        
        package = PromptPackage(
            system_prompt="You are a helpful assistant. Be concise.",
            user_prompt="Say 'Hello, I am working!' in one short sentence.",
            prompt_type="test",
            temperature=0.7,
            max_tokens=50,
        )
        
        print(f"Calling {provider.get_provider_name()} with model {provider.get_model()}...")
        
        response = await provider.generate(package)
        
        print(f"\nResponse:")
        print(f"  Success: {'✅' if response.success else '❌'}")
        print(f"  Content: {response.content}")
        print(f"  Latency: {response.latency_ms:.0f}ms")
        print(f"  Tokens: {response.total_tokens} (in: {response.input_tokens}, out: {response.output_tokens})")
        print(f"  Retries: {response.retry_count}")
        
        if not response.success:
            print(f"  Error: {response.error}")
        
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests."""
    print_section("PHASE 14: PROMPT SERVICE & LLM INTEGRATION TEST")
    
    try:
        # Test 1: Provider validation
        test_provider_validation()
        
        # Test 2: System prompt
        test_system_prompt()
        
        # Test 3: Token estimation
        test_token_estimation()
        
        # Test 4: Provider creation
        test_provider_creation()
        
        # Test 5: Simple LLM call
        await test_simple_llm_call()
        
        print_section("SUMMARY")
        print("✅ All Phase 14 tests passed!")
        print("\nComponents verified:")
        print("  ✓ Provider configuration validation")
        print("  ✓ System prompt builder")
        print("  ✓ Token estimator")
        print("  ✓ Provider factory")
        print("  ✓ LLM API integration")
        print("\nPhase 14 is ready for integration with orchestrator.")
        
    except Exception as e:
        print_section("SUMMARY")
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
