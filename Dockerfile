FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy project files
COPY pyproject.toml .
COPY src/ ./src/

# Install dependencies
RUN uv pip install --system -e .

# Create data directories
RUN mkdir -p /app/data/raw /app/data/processed /app/data/embeddings

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "src.main"]
