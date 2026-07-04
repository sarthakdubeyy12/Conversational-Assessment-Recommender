FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy project files
COPY pyproject.toml .
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY evaluation/ ./evaluation/
COPY tests/ ./tests/

# Install dependencies using pip directly (simpler approach)
RUN pip install --no-cache-dir \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.30.0" \
    "pydantic>=2.9.0" \
    "pydantic-settings>=2.5.0" \
    "chromadb>=0.5.0" \
    "sentence-transformers>=3.0.0" \
    "beautifulsoup4>=4.12.0" \
    "requests>=2.31.0" \
    "playwright>=1.47.0" \
    "openai>=1.45.0" \
    "google-generativeai>=0.8.0" \
    "python-dotenv>=1.0.0" \
    "pytest>=8.0.0" \
    "pytest-asyncio>=0.23.0" \
    "pytest-cov>=4.1.0" \
    "httpx>=0.27.0"

# Create data directories
RUN mkdir -p /app/data/raw /app/data/processed /app/data/embeddings

# Build catalog and knowledge base during image build
RUN python3 scripts/create_mock_catalog.py && \
    python3 scripts/build_knowledge_base.py

# Make startup script executable
RUN chmod +x scripts/startup.sh

# Expose port
EXPOSE 8000

# Run application with startup script
CMD ["bash", "scripts/startup.sh"]
