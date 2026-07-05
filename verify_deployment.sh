#!/bin/bash

# SHL Assessment Recommender - Deployment Verification Script
# Usage: ./verify_deployment.sh <YOUR_DEPLOYED_URL>

set -e

if [ -z "$1" ]; then
    echo "❌ Error: Please provide your deployed URL"
    echo "Usage: ./verify_deployment.sh https://your-app.onrender.com"
    exit 1
fi

API_URL="$1"
echo "🔍 Verifying deployment at: $API_URL"
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "--------------------"
HEALTH_RESPONSE=$(curl -s "${API_URL}/health")
echo "$HEALTH_RESPONSE" | python3 -m json.tool
HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))")

if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo "✅ Health check PASSED"
else
    echo "❌ Health check FAILED"
    exit 1
fi
echo ""

# Test 2: Catalog Size
echo "Test 2: Catalog Size"
echo "--------------------"
CATALOG_SIZE=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('catalog_size', 0))")
echo "Catalog size: $CATALOG_SIZE assessments"

if [ "$CATALOG_SIZE" -ge 5 ]; then
    echo "✅ Catalog size acceptable (${CATALOG_SIZE} >= 5)"
else
    echo "❌ Catalog size too small (${CATALOG_SIZE} < 5)"
    exit 1
fi
echo ""

# Test 3: Chat Endpoint
echo "Test 3: Chat Endpoint"
echo "--------------------"
CHAT_REQUEST='{
  "message": "I need to assess problem-solving and analytical skills",
  "session_id": "verification-test"
}'

CHAT_RESPONSE=$(curl -s -X POST "${API_URL}/chat" \
    -H "Content-Type: application/json" \
    -d "$CHAT_REQUEST")

echo "$CHAT_RESPONSE" | python3 -m json.tool

# Check response structure
HAS_REPLY=$(echo "$CHAT_RESPONSE" | python3 -c "import sys, json; print('reply' in json.load(sys.stdin))")
HAS_RECOMMENDATIONS=$(echo "$CHAT_RESPONSE" | python3 -c "import sys, json; print('recommendations' in json.load(sys.stdin))")
REC_COUNT=$(echo "$CHAT_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('recommendations', [])))")

if [ "$HAS_REPLY" = "True" ] && [ "$HAS_RECOMMENDATIONS" = "True" ]; then
    echo "✅ Chat endpoint PASSED"
    echo "   Reply: Present"
    echo "   Recommendations: $REC_COUNT"
else
    echo "❌ Chat endpoint FAILED"
    exit 1
fi
echo ""

# Test 4: Recommendation URLs
echo "Test 4: Recommendation URLs"
echo "--------------------"
URLS=$(echo "$CHAT_RESPONSE" | python3 -c "import sys, json; recs = json.load(sys.stdin).get('recommendations', []); [print(r['url']) for r in recs if 'url' in r]")

ALL_VALID=true
while IFS= read -r url; do
    if [[ $url == https://www.shl.com/* ]]; then
        echo "✅ Valid SHL URL: $url"
    else
        echo "❌ Invalid URL: $url"
        ALL_VALID=false
    fi
done <<< "$URLS"

if [ "$ALL_VALID" = true ]; then
    echo "✅ All URLs are valid SHL URLs"
else
    echo "❌ Some URLs are invalid"
    exit 1
fi
echo ""

# Test 5: OpenAPI Docs
echo "Test 5: OpenAPI Documentation"
echo "--------------------"
DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/docs")

if [ "$DOCS_STATUS" = "200" ]; then
    echo "✅ OpenAPI docs accessible at ${API_URL}/docs"
else
    echo "❌ OpenAPI docs not accessible (HTTP $DOCS_STATUS)"
    exit 1
fi
echo ""

# Final Summary
echo "================================"
echo "🎉 ALL TESTS PASSED!"
echo "================================"
echo ""
echo "Your deployment is ready for submission:"
echo "  • API URL: $API_URL"
echo "  • Health: ✅ Healthy"
echo "  • Catalog: ✅ $CATALOG_SIZE assessments"
echo "  • Chat: ✅ Functional"
echo "  • URLs: ✅ All valid SHL URLs"
echo "  • Docs: ✅ ${API_URL}/docs"
echo ""
echo "📋 Next steps:"
echo "  1. Test more queries manually"
echo "  2. Review DEPLOYMENT_GUIDE.md for submission template"
echo "  3. Submit your GitHub repo + deployed URL"
echo ""
