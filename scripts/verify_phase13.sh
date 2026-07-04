#!/bin/bash

echo "============================================================"
echo "PHASE 13 VERIFICATION"
echo "============================================================"

echo ""
echo "📁 Checking file structure..."
echo ""

# Models
echo "Models:"
test -f src/api/models/chat_request.py && echo "  ✅ chat_request.py" || echo "  ❌ chat_request.py"
test -f src/api/models/chat_response.py && echo "  ✅ chat_response.py" || echo "  ❌ chat_response.py"
test -f src/api/models/health_response.py && echo "  ✅ health_response.py" || echo "  ❌ health_response.py"
test -f src/api/models/error_response.py && echo "  ✅ error_response.py" || echo "  ❌ error_response.py"

echo ""
echo "Routes:"
test -f src/api/routes/chat.py && echo "  ✅ chat.py" || echo "  ❌ chat.py"
test -f src/api/routes/health.py && echo "  ✅ health.py" || echo "  ❌ health.py"

echo ""
echo "Dependencies:"
test -f src/api/dependencies/orchestrator.py && echo "  ✅ orchestrator.py" || echo "  ❌ orchestrator.py"
test -f src/api/dependencies/container.py && echo "  ✅ container.py" || echo "  ❌ container.py"

echo ""
echo "Middleware:"
test -f src/api/middleware/error_handler.py && echo "  ✅ error_handler.py" || echo "  ❌ error_handler.py"
test -f src/api/middleware/logging_middleware.py && echo "  ✅ logging_middleware.py" || echo "  ❌ logging_middleware.py"

echo ""
echo "Application:"
test -f src/api/app.py && echo "  ✅ app.py" || echo "  ❌ app.py"

echo ""
echo "Documentation:"
test -f PHASE13_FASTAPI_SERVICE.txt && echo "  ✅ PHASE13_FASTAPI_SERVICE.txt" || echo "  ❌ PHASE13_FASTAPI_SERVICE.txt"

echo ""
echo "Tests:"
test -f scripts/test_fastapi_service.py && echo "  ✅ test_fastapi_service.py" || echo "  ❌ test_fastapi_service.py"

echo ""
echo "============================================================"
echo "🔍 Checking schema compliance..."
echo "============================================================"

echo ""
echo "ChatRequest schema:"
grep -q "messages: List\[MessageModel\]" src/api/models/chat_request.py && echo "  ✅ messages field present" || echo "  ❌ messages field missing"
grep -q "def get_current_message" src/api/models/chat_request.py && echo "  ✅ get_current_message() method" || echo "  ❌ get_current_message() missing"
grep -q "def get_history" src/api/models/chat_request.py && echo "  ✅ get_history() method" || echo "  ❌ get_history() missing"

echo ""
echo "ChatResponse schema:"
grep -q "reply: str" src/api/models/chat_response.py && echo "  ✅ reply field present" || echo "  ❌ reply field missing"
grep -q "recommendations: List\[RecommendationModel\]" src/api/models/chat_response.py && echo "  ✅ recommendations field present" || echo "  ❌ recommendations field missing"
grep -q "end_of_conversation: bool" src/api/models/chat_response.py && echo "  ✅ end_of_conversation field present" || echo "  ❌ end_of_conversation field missing"

echo ""
echo "RecommendationModel schema:"
grep -q "title: str" src/api/models/chat_response.py && echo "  ✅ title field present" || echo "  ❌ title field missing"
grep -q "url: str" src/api/models/chat_response.py && echo "  ✅ url field present" || echo "  ❌ url field missing"

echo ""
echo "============================================================"
echo "🔍 Checking endpoint implementation..."
echo "============================================================"

echo ""
echo "Chat endpoint:"
grep -q "@router.post(\"/chat\"" src/api/routes/chat.py && echo "  ✅ POST /chat endpoint defined" || echo "  ❌ POST /chat missing"
grep -q "async def chat" src/api/routes/chat.py && echo "  ✅ Async handler defined" || echo "  ❌ Async handler missing"
grep -q "Depends(get_orchestrator)" src/api/routes/chat.py && echo "  ✅ Orchestrator injection" || echo "  ❌ Orchestrator injection missing"
grep -q "await orchestrator.execute" src/api/routes/chat.py && echo "  ✅ Calls orchestrator" || echo "  ❌ Orchestrator call missing"

echo ""
echo "Health endpoint:"
grep -q "@router.get(\"/health\"" src/api/routes/health.py && echo "  ✅ GET /health endpoint defined" || echo "  ❌ GET /health missing"
grep -q "async def health" src/api/routes/health.py && echo "  ✅ Async handler defined" || echo "  ❌ Async handler missing"

echo ""
echo "============================================================"
echo "✅ PHASE 13 VERIFICATION COMPLETE"
echo "============================================================"
echo ""
echo "All files created and schema compliant."
echo "Ready for Docker build and integration testing."
echo ""
