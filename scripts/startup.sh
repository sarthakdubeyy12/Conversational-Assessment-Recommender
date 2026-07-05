#!/bin/bash
set -e

echo "🚀 Starting SHL Assessment Recommender..."
echo ""

# Check if catalog exists
if [ ! -f "./data/processed/catalog.json" ]; then
    echo "📦 Building catalog..."
    python3 scripts/build_catalog.py
    echo ""
fi

# Check if knowledge base exists
CHROMA_DB="./data/embeddings/chroma.sqlite3"
if [ ! -f "$CHROMA_DB" ]; then
    echo "🧠 Building knowledge base..."
    python3 scripts/build_knowledge_base.py
    echo ""
fi

echo "✅ Startup checks complete"
echo ""

# Start the API
echo "🌐 Starting API server..."
python -m src.main
