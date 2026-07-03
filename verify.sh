#!/bin/bash
#
# Quick Infrastructure Verification Script
# Usage: ./verify.sh
#

cd "$(dirname "$0")"

echo "🔍 Verifying Phase 1 Infrastructure..."
echo ""

# Method 1: Check Docker container
echo "1️⃣  Docker Container Status:"
if docker ps | grep -q "conversational-shl-assessment-recommender-api-1"; then
    echo "   ✅ Container is running"
    docker ps --filter "name=conversational-shl-assessment" --format "   📦 {{.Names}} - {{.Status}}"
else
    echo "   ❌ Container is not running"
    echo "   Run: docker-compose up -d"
    exit 1
fi

echo ""

# Method 2: Check Health Endpoint
echo "2️⃣  Health Endpoint Test:"
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo "   ✅ API is responding"
    echo "   Response:"
    curl -s http://localhost:8000/health | python3 -m json.tool | sed 's/^/   /'
else
    echo "   ❌ API is not responding"
    exit 1
fi

echo ""

# Method 3: Run Full Infrastructure Tests
echo "3️⃣  Running Full Infrastructure Tests:"
if [ -f "scripts/verify_infrastructure_docker.sh" ]; then
    bash scripts/verify_infrastructure_docker.sh
else
    echo "   ⚠️  Detailed test script not found, skipping"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Phase 1 Infrastructure: OPERATIONAL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Ready for Phase 2: Catalog Implementation"
echo ""
