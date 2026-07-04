#!/bin/bash

echo "============================================================"
echo "PHASE 15 VERIFICATION"
echo "============================================================"

echo ""
echo "📁 Checking test structure..."
echo ""

# Core files
echo "Core Files:"
test -f tests/__init__.py && echo "  ✅ tests/__init__.py" || echo "  ❌ tests/__init__.py"
test -f tests/conftest.py && echo "  ✅ tests/conftest.py" || echo "  ❌ tests/conftest.py"
test -f pytest.ini && echo "  ✅ pytest.ini" || echo "  ❌ pytest.ini"

echo ""
echo "Unit Tests:"
test -f tests/unit/intent/test_intent_engine.py && echo "  ✅ test_intent_engine.py" || echo "  ❌ test_intent_engine.py"
test -f tests/unit/guardrails/test_guardrails_engine.py && echo "  ✅ test_guardrails_engine.py" || echo "  ❌ test_guardrails_engine.py"
test -f tests/unit/prompting/test_token_estimator.py && echo "  ✅ test_token_estimator.py" || echo "  ❌ test_token_estimator.py"
test -f tests/unit/prompting/test_system_prompt_builder.py && echo "  ✅ test_system_prompt_builder.py" || echo "  ❌ test_system_prompt_builder.py"

echo ""
echo "E2E Tests:"
test -f tests/e2e/api/test_api_endpoints.py && echo "  ✅ test_api_endpoints.py" || echo "  ❌ test_api_endpoints.py"
test -f tests/e2e/conversations/test_conversation_flows.py && echo "  ✅ test_conversation_flows.py" || echo "  ❌ test_conversation_flows.py"

echo ""
echo "Utilities:"
test -f tests/utils/test_helpers.py && echo "  ✅ test_helpers.py" || echo "  ❌ test_helpers.py"

echo ""
echo "Mocks:"
test -f tests/mocks/llm/mock_llm_provider.py && echo "  ✅ mock_llm_provider.py" || echo "  ❌ mock_llm_provider.py"

echo ""
echo "Scripts:"
test -f scripts/run_tests.py && echo "  ✅ run_tests.py" || echo "  ❌ run_tests.py"
test -f scripts/test_system_validation.py && echo "  ✅ test_system_validation.py" || echo "  ❌ test_system_validation.py"

echo ""
echo "Documentation:"
test -f PHASE15_TESTING_FRAMEWORK.txt && echo "  ✅ PHASE15_TESTING_FRAMEWORK.txt" || echo "  ❌ PHASE15_TESTING_FRAMEWORK.txt"

echo ""
echo "============================================================"
echo "🔍 Checking Python syntax..."
echo "============================================================"

python3 -m py_compile tests/unit/intent/test_intent_engine.py && echo "  ✅ Intent tests compile" || echo "  ❌ Intent tests syntax error"
python3 -m py_compile tests/unit/guardrails/test_guardrails_engine.py && echo "  ✅ Guardrails tests compile" || echo "  ❌ Guardrails tests syntax error"
python3 -m py_compile tests/e2e/api/test_api_endpoints.py && echo "  ✅ API tests compile" || echo "  ❌ API tests syntax error"

echo ""
echo "============================================================"
echo "✅ PHASE 15 VERIFICATION COMPLETE"
echo "============================================================"
echo ""
echo "Test framework is ready. Run tests with:"
echo "  python3 scripts/run_tests.py all"
echo "  python3 scripts/test_system_validation.py"
echo ""
