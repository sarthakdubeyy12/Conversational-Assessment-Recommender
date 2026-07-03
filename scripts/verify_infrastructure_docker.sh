#!/bin/bash
#
# Docker-based Infrastructure Verification Script
# Runs verification inside the Docker container where dependencies are installed
#

set -e

echo "============================================================"
echo "PHASE 1 INFRASTRUCTURE VERIFICATION (Docker)"
echo "============================================================"
echo ""

# Check if container is running
if ! docker ps | grep -q "conversational-shl-assessment-recommender-api-1"; then
    echo "❌ ERROR: Docker container is not running!"
    echo ""
    echo "Please start the container first:"
    echo "  cd /Users/sarthakdubey/Downloads/Conversational-SHL-Assessment-Recommender"
    echo "  docker-compose up -d"
    exit 1
fi

echo "✓ Docker container is running"
echo ""

# Copy verification script into container
echo "✓ Copying verification script to container..."
docker cp scripts/verify_infrastructure.py conversational-shl-assessment-recommender-api-1:/app/verify_infrastructure.py

echo "✓ Running verification inside container..."
echo ""

# Run verification inside container
docker exec conversational-shl-assessment-recommender-api-1 python3 /app/verify_infrastructure.py

# Cleanup
docker exec conversational-shl-assessment-recommender-api-1 rm /app/verify_infrastructure.py

echo ""
echo "============================================================"
echo "✅ VERIFICATION COMPLETE"
echo "============================================================"
