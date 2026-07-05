# Assessment Recommender

Conversational AI system for recommending Individual Test Solutions through natural dialogue.

## Project Structure

```
src/
├── catalog/          # Assessment catalog management
├── retrieval/        # Semantic search and retrieval
├── conversation/     # Dialogue orchestration
├── recommendation/   # Assessment recommendation logic
├── comparison/       # Assessment comparison
├── guardrails/       # Security and validation
├── api/             # FastAPI endpoints
└── shared/          # Cross-cutting infrastructure
```

## Setup

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e .

# Install dev dependencies
uv pip install -e ".[dev]"

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
```

## Run

```bash
# Run directly
python -m src.main

# Or with Docker
docker-compose up
```

## Development

```bash
# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/ --fix

# Type check
mypy src/
```

## Architecture

- **Feature-First Modular Architecture**
- **Clean Architecture** within each feature
- **Dependency Inversion** throughout
- **Framework Independence**

## API Endpoints

- `GET /health` - Health check
- `POST /chat` - Conversational interface
