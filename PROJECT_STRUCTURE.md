# Project Structure

```
Conversational-SHL-Assessment-Recommender/
├── src/
│   ├── catalog/                    # Catalog ingestion and management
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── entities.py        # Assessment, TestType, Category entities
│   │   │   ├── interfaces.py      # ICatalogRepository, ICatalogScraper
│   │   │   └── value_objects.py   # URL, TestTypeEnum value objects
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   ├── catalog_service.py # Orchestrates catalog operations
│   │   │   ├── scraper_service.py # Scraping orchestration
│   │   │   └── parser_service.py  # Parsing logic
│   │   ├── infrastructure/
│   │   │   ├── __init__.py
│   │   │   ├── web_scraper.py     # BeautifulSoup/Playwright implementation
│   │   │   ├── catalog_parser.py  # HTML parsing
│   │   │   ├── json_repository.py # JSON storage
│   │   │   └── validators.py      # URL and data validation
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── catalog_schemas.py # Pydantic models for API
│   │   └── dependencies.py         # DI container for catalog
│   │
│   ├── retrieval/                  # Semantic search and retrieval
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── entities.py        # RetrievalContext, SearchQuery
│   │   │   ├── interfaces.py      # IVectorStore, IEmbedder, IRetriever
│   │   │   └── search_strategy.py # Search strategy patterns
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   ├── retrieval_service.py    # Main retrieval orchestration
│   │   │   ├── query_builder.py        # Query construction
│   │   │   ├── context_builder.py      # Context assembly
│   │   │   ├── filter_builder.py       # Metadata filtering
│   │   │   └── reranker_service.py     # Reranking logic (future)
│   │   ├── infrastructure/
│   │   │   ├── __init__.py
│   │   │   ├── chroma_store.py         # ChromaDB implementation
│   │   │   ├── embedder.py             # sentence-transformers wrapper
│   │   │   ├── hybrid_search.py        # Hybrid search implementation
│   │   │   └── metadata_extractor.py   # Extract metadata from assessments
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── retrieval_schemas.py    # Query, Result schemas
│   │   └── dependencies.py
│   │
│   ├── conversation/               # Dialogue orchestration
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── entities.py        # ConversationState, Turn, Intent
│   │   │   ├── interfaces.py      # IConversationOrchestrator, IIntentDetector
│   │   │   └── intent_types.py    # Intent enums and types
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py         # Main conversation flow
│   │   │   ├── intent_detector.py      # Intent classification
│   │   │   ├── state_manager.py        # State reconstruction
│   │   │   ├── clarification_engine.py # When to ask questions
│   │   │   ├── response_formatter.py   # Format final responses
│   │   │   └── workflow_router.py      # Route to appropriate feature
│   │   ├── infrastructure/
│   │   │   ├── __init__.py
│   │   │   ├── llm_client.py           # LLM provider abstraction
│   │   │   ├── prompt_builder.py       # Prompt construction
│   │   │   └── history_parser.py       # Parse message history
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── conversation_schemas.py # Message, State schemas
│   │   └── dependencies.py
│   │
│   ├── recommendation/             # Assessment recommendation
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── entities.py        # Recommendation, Criteria
│   │   │   ├── interfaces.py      # IRecommendationEngine, IRanker
│   │   │   └── ranking_strategy.py # Ranking algorithms
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   ├── recommendation_service.py # Main recommendation logic
│   │   │   ├── criteria_extractor.py     # Extract hiring criteria
│   │   │   ├── matcher.py                # Match criteria to assessments
│   │   │   └── ranker.py                 # Rank and limit results
│   │   ├── infrastructure/
│   │   │   ├── __init__.py
│   │   │   ├── scoring_engine.py         # Scoring implementation
│   │   │   └── filter_engine.py          # Filter assessments
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── recommendation_schemas.py # Recommendation DTOs
│   │   └── dependencies.py
│   │
│   ├── comparison/                 # Assessment comparison
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── entities.py        # ComparisonResult, Difference
│   │   │   └── interfaces.py      # IComparisonEngine
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   ├── comparison_service.py     # Main comparison logic
│   │   │   ├── diff_analyzer.py          # Analyze differences
│   │   │   └── feature_extractor.py      # Extract comparable features
│   │   ├── infrastructure/
│   │   │   ├── __init__.py
│   │   │   └── llm_comparer.py           # LLM-based comparison
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── comparison_schemas.py     # Comparison DTOs
│   │   └── dependencies.py
│   │
│   ├── guardrails/                 # Security and validation
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── entities.py        # ValidationResult, SecurityCheck
│   │   │   └── interfaces.py      # IGuardrail, IValidator
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   ├── guardrail_service.py      # Main guardrail orchestration
│   │   │   ├── input_validator.py        # Input validation
│   │   │   ├── output_validator.py       # Output validation
│   │   │   ├── prompt_injection_detector.py # Prompt injection defense
│   │   │   ├── scope_enforcer.py         # Keep agent in scope
│   │   │   └── url_validator.py          # Validate URLs against catalog
│   │   ├── infrastructure/
│   │   │   ├── __init__.py
│   │   │   ├── pattern_matcher.py        # Regex patterns for detection
│   │   │   └── catalog_checker.py        # Check against catalog
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── guardrail_schemas.py      # Validation DTOs
│   │   └── dependencies.py
│   │
│   ├── api/                        # HTTP interface
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── health.py          # GET /health
│   │   │   └── chat.py            # POST /chat
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── error_handler.py   # Global error handling
│   │   │   ├── logging_middleware.py # Request/response logging
│   │   │   └── timeout_middleware.py # Timeout enforcement
│   │   ├── dependencies/
│   │   │   ├── __init__.py
│   │   │   └── container.py       # FastAPI dependency injection
│   │   ├── __init__.py
│   │   └── app.py                 # FastAPI app factory
│   │
│   ├── shared/                     # Cross-cutting concerns
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── settings.py        # Pydantic Settings
│   │   │   └── llm_config.py      # LLM provider configs
│   │   ├── logging/
│   │   │   ├── __init__.py
│   │   │   ├── logger.py          # Logger setup
│   │   │   └── formatters.py      # Log formatters
│   │   ├── exceptions/
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # Base exception
│   │   │   ├── catalog_exceptions.py
│   │   │   ├── retrieval_exceptions.py
│   │   │   ├── conversation_exceptions.py
│   │   │   └── api_exceptions.py
│   │   ├── interfaces/
│   │   │   ├── __init__.py
│   │   │   └── base_interfaces.py # Shared interfaces
│   │   ├── constants/
│   │   │   ├── __init__.py
│   │   │   ├── api_constants.py
│   │   │   └── test_type_constants.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── text_utils.py      # Text processing
│   │   │   └── timing.py          # Performance timing
│   │   └── __init__.py
│   │
│   ├── __init__.py
│   └── main.py                     # Application entry point
│
├── tests/
│   ├── unit/
│   │   ├── catalog/
│   │   │   ├── __init__.py
│   │   │   ├── test_catalog_service.py
│   │   │   ├── test_scraper.py
│   │   │   └── test_parser.py
│   │   ├── retrieval/
│   │   │   ├── __init__.py
│   │   │   ├── test_retrieval_service.py
│   │   │   ├── test_embedder.py
│   │   │   └── test_query_builder.py
│   │   ├── conversation/
│   │   │   ├── __init__.py
│   │   │   ├── test_orchestrator.py
│   │   │   ├── test_intent_detector.py
│   │   │   └── test_state_manager.py
│   │   ├── recommendation/
│   │   │   ├── __init__.py
│   │   │   ├── test_recommendation_service.py
│   │   │   └── test_matcher.py
│   │   ├── comparison/
│   │   │   ├── __init__.py
│   │   │   └── test_comparison_service.py
│   │   ├── guardrails/
│   │   │   ├── __init__.py
│   │   │   ├── test_guardrail_service.py
│   │   │   ├── test_prompt_injection_detector.py
│   │   │   └── test_url_validator.py
│   │   └── __init__.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_api_endpoints.py
│   │   ├── test_conversation_flow.py
│   │   └── test_retrieval_pipeline.py
│   ├── e2e/
│   │   ├── __init__.py
│   │   └── test_full_conversation.py
│   ├── fixtures/
│   │   ├── __init__.py
│   │   ├── catalog_fixtures.py
│   │   └── conversation_fixtures.py
│   ├── conftest.py
│   └── __init__.py
│
├── scripts/
│   ├── scrape_catalog.py          # One-time catalog scraping
│   ├── build_embeddings.py        # Generate embeddings
│   ├── validate_catalog.py        # Validate catalog data
│   └── run_evaluation.py          # Run evaluation traces
│
├── data/
│   ├── raw/                        # Raw scraped data
│   ├── processed/                  # Processed catalog JSON
│   └── embeddings/                 # Vector embeddings
│
├── evaluation/
│   ├── traces/                     # Conversation traces
│   └── metrics/                    # Evaluation metrics
│
├── docs/
│   ├── API.md                      # API documentation
│   ├── ARCHITECTURE.md             # Architecture details
│   ├── DEVELOPMENT.md              # Development guide
│   └── DEPLOYMENT.md               # Deployment guide
│
├── .env.example                    # Example environment variables
├── .gitignore
├── .python-version                 # Python version (3.12)
├── pyproject.toml                  # UV project configuration
├── uv.lock                         # UV lock file
├── Dockerfile
├── docker-compose.yml
├── README.md
└── ARCHITECTURE.md
```
