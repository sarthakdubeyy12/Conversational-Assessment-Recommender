# Conversational SHL Assessment Recommender - Architecture

## System Overview

Production-grade conversational AI system for recommending SHL assessments through natural dialogue.

## Architecture Style

**Feature-First Modular Architecture** with **Clean Architecture** principles within each feature.

## Core Features

1. **catalog/** - Assessment catalog ingestion and management
2. **retrieval/** - Semantic search and context retrieval
3. **conversation/** - Dialogue orchestration and state management
4. **recommendation/** - Assessment selection and ranking
5. **comparison/** - Assessment comparison logic
6. **guardrails/** - Security, validation, and boundary enforcement
7. **api/** - HTTP interface and request handling
8. **shared/** - Cross-cutting infrastructure

## Data Flow

```
User Request
    ↓
API Layer (FastAPI)
    ↓
Conversation Orchestrator
    ↓
Intent Detection → Guardrails Check
    ↓
Clarification Engine OR Retrieval Pipeline
    ↓
Recommendation Engine OR Comparison Engine
    ↓
Response Formatter → Guardrails Check
    ↓
API Response
```

## Technology Stack

- **Runtime**: Python 3.12+
- **API**: FastAPI + Uvicorn
- **LLM**: OpenAI/Gemini/Groq (abstracted)
- **Vector DB**: ChromaDB (abstracted)
- **Embeddings**: sentence-transformers
- **Validation**: Pydantic v2
- **Testing**: pytest
- **Quality**: Ruff, Black, MyPy

## Design Principles

- Single Responsibility
- Dependency Inversion
- Interface-driven design
- High cohesion, low coupling
- No circular dependencies
- No god files
- Composition over inheritance

## Deployment

- Docker containerized
- Environment-based configuration
- Health checks
- Structured logging
- Graceful error handling
