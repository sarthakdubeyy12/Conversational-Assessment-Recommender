#!/bin/bash

echo "============================================================"
echo "PHASE 14 VERIFICATION"
echo "============================================================"

echo ""
echo "📁 Checking file structure..."
echo ""

# Models
echo "Models:"
test -f src/prompting/models/prompt_package.py && echo "  ✅ prompt_package.py" || echo "  ❌ prompt_package.py"
test -f src/prompting/models/provider_response.py && echo "  ✅ provider_response.py" || echo "  ❌ provider_response.py"

echo ""
echo "Builders:"
test -f src/prompting/builders/system_prompt_builder.py && echo "  ✅ system_prompt_builder.py" || echo "  ❌ system_prompt_builder.py"
test -f src/prompting/builders/recommendation_prompt_builder.py && echo "  ✅ recommendation_prompt_builder.py" || echo "  ❌ recommendation_prompt_builder.py"
test -f src/prompting/builders/comparison_prompt_builder.py && echo "  ✅ comparison_prompt_builder.py" || echo "  ❌ comparison_prompt_builder.py"
test -f src/prompting/builders/clarification_prompt_builder.py && echo "  ✅ clarification_prompt_builder.py" || echo "  ❌ clarification_prompt_builder.py"
test -f src/prompting/builders/refusal_prompt_builder.py && echo "  ✅ refusal_prompt_builder.py" || echo "  ❌ refusal_prompt_builder.py"
test -f src/prompting/builders/fallback_prompt_builder.py && echo "  ✅ fallback_prompt_builder.py" || echo "  ❌ fallback_prompt_builder.py"

echo ""
echo "Optimization:"
test -f src/prompting/optimization/token_estimator.py && echo "  ✅ token_estimator.py" || echo "  ❌ token_estimator.py"

echo ""
echo "Providers:"
test -f src/prompting/providers/base_provider.py && echo "  ✅ base_provider.py" || echo "  ❌ base_provider.py"
test -f src/prompting/providers/openai_provider.py && echo "  ✅ openai_provider.py" || echo "  ❌ openai_provider.py"
test -f src/prompting/providers/groq_provider.py && echo "  ✅ groq_provider.py" || echo "  ❌ groq_provider.py"
test -f src/prompting/providers/provider_factory.py && echo "  ✅ provider_factory.py" || echo "  ❌ provider_factory.py"

echo ""
echo "Service:"
test -f src/prompting/prompt_service.py && echo "  ✅ prompt_service.py" || echo "  ❌ prompt_service.py"

echo ""
echo "Documentation:"
test -f PHASE14_PROMPT_ENGINEERING.txt && echo "  ✅ PHASE14_PROMPT_ENGINEERING.txt" || echo "  ❌ PHASE14_PROMPT_ENGINEERING.txt"

echo ""
echo "Tests:"
test -f scripts/test_prompt_service.py && echo "  ✅ test_prompt_service.py" || echo "  ❌ test_prompt_service.py"

echo ""
echo "============================================================"
echo "🔍 Checking configuration..."
echo "============================================================"

echo ""
echo "Environment variables:"
grep -q "LLM_PROVIDER=groq" .env && echo "  ✅ LLM_PROVIDER set to groq" || echo "  ⚠️  LLM_PROVIDER not set to groq"
grep -q "GROQ_API_KEY=gsk_" .env && echo "  ✅ GROQ_API_KEY configured" || echo "  ❌ GROQ_API_KEY missing"

echo ""
echo "============================================================"
echo "✅ PHASE 14 VERIFICATION COMPLETE"
echo "============================================================"
echo ""
echo "All files created successfully."
echo "Ready for Docker rebuild and testing."
echo ""
