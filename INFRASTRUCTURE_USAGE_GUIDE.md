# Phase 1 Infrastructure Usage Guide

Quick reference for using the Core Infrastructure components in future phases.

---

## 1. Configuration

### Get Settings
```python
from src.shared.config.settings import get_settings

settings = get_settings()  # Cached singleton

# Access configuration
llm_provider = settings.llm_provider
api_key = settings.openai_api_key
debug_mode = settings.debug

# Environment checks
if settings.is_production:
    # Production-specific logic
    pass
```

---

## 2. Logging

### Get Logger
```python
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)

# Log messages
logger.debug("Debug information")
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
logger.critical("Critical error")

# With extra context
logger.info("Processing document", extra={
    "document_id": "123",
    "user_id": "456"
})
```

### Set Request ID
```python
from src.shared.logging.logger import set_request_id

set_request_id("req_abc123")
# All logs will include this request_id
```

---

## 3. Exceptions

### Raise Exceptions
```python
from src.shared.exceptions import (
    ValidationException,
    NotFoundException,
    ExternalServiceException,
    ConfigurationException
)

# Validation error
raise ValidationException(
    message="Invalid email format",
    field="email"
)

# Not found
raise NotFoundException(
    resource_type="Assessment",
    resource_id="123"
)

# External service error
raise ExternalServiceException(
    service_name="OpenAI",
    message="API rate limit exceeded",
    status_code=429,
    details={"retry_after": 60}
)

# Configuration error
raise ConfigurationException(
    message="Missing API key",
    config_key="OPENAI_API_KEY"
)
```

---

## 4. Response Models

### Success Response
```python
from src.shared.schemas.response_models import SuccessResponse

data = {"recommendations": [...]}
response = SuccessResponse(
    data=data,
    message="Recommendations generated successfully"
)
return response
```

### Error Response (handled automatically by middleware)
```python
# Just raise exception, middleware converts to ErrorResponse
raise ValidationException("Invalid input")
```

### Paginated Response
```python
from src.shared.schemas.response_models import (
    PaginatedResponse,
    PaginationMeta
)

items = [...]  # Your data items
pagination = PaginationMeta(
    page=1,
    page_size=10,
    total_items=100,
    total_pages=10,
    has_next=True,
    has_previous=False
)

response = PaginatedResponse(
    data=items,
    pagination=pagination
)
```

---

## 5. Utilities

### DateTime
```python
from src.shared.utils.datetime_utils import (
    utcnow,
    to_iso_string,
    seconds_ago,
    is_expired
)

now = utcnow()
iso_timestamp = to_iso_string(now)
one_hour_ago = seconds_ago(3600)

expiry = seconds_from_now(3600)
if is_expired(expiry):
    # Handle expiration
    pass
```

### UUID
```python
from src.shared.utils.uuid_utils import (
    generate_uuid,
    generate_request_id,
    is_valid_uuid
)

uuid = generate_uuid()
request_id = generate_request_id()  # "req_<uuid>"

if is_valid_uuid(some_string):
    # Valid UUID
    pass
```

### Validators
```python
from src.shared.utils.validators import (
    is_valid_url,
    is_valid_email,
    is_valid_string_length,
    is_non_empty_string
)

if is_valid_url(url, require_https=True):
    # Valid HTTPS URL
    pass

if is_valid_string_length(text, min_length=10, max_length=100):
    # Valid length
    pass

if is_non_empty_string(value):
    # Not empty
    pass
```

### Collections
```python
from src.shared.utils.collection_utils import (
    chunk_list,
    deduplicate_list,
    merge_dicts,
    remove_none_values
)

# Process in batches
for batch in chunk_list(items, chunk_size=50):
    # Process batch
    pass

# Remove duplicates
unique_items = deduplicate_list(items, key=lambda x: x.id)

# Merge configurations
config = merge_dicts(defaults, overrides)

# Clean data
clean_data = remove_none_values(data_dict)
```

### Hash
```python
from src.shared.utils.hash_utils import (
    hash_string,
    generate_content_hash
)

hash_value = hash_string(text, algorithm="sha256")
content_id = generate_content_hash(document_content)
```

### Path
```python
from src.shared.utils.path_utils import (
    ensure_directory,
    get_project_root,
    get_data_directory,
    resolve_path
)

# Ensure directory exists
data_dir = ensure_directory("./data/embeddings")

# Get paths
root = get_project_root()
data = get_data_directory()

# Resolve relative paths
full_path = resolve_path("./catalog.json", base_path=data)
```

---

## 6. Interfaces (Implement These)

### Repository Pattern
```python
from src.shared.interfaces.base_interfaces import IRepository
from typing import List, Optional

class AssessmentRepository(IRepository[Assessment]):
    async def save(self, entity: Assessment) -> None:
        # Implementation
        pass
    
    async def load(self) -> List[Assessment]:
        # Implementation
        pass
    
    async def find_by_id(self, entity_id: str) -> Optional[Assessment]:
        # Implementation
        pass
    
    async def delete(self, entity_id: str) -> None:
        # Implementation
        pass
```

### LLM Provider
```python
from src.shared.interfaces.base_interfaces import ILLMProvider
from typing import List, Dict

class OpenAIProvider(ILLMProvider):
    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2000
    ) -> str:
        # Implementation
        pass
    
    async def generate_streaming(self, ...):
        # Implementation
        pass
    
    def count_tokens(self, text: str) -> int:
        # Implementation
        pass
```

---

## 7. Constants

### Use Constants
```python
from src.shared.constants.api_constants import (
    MAX_RECOMMENDATIONS,
    USER_ROLE,
    ASSISTANT_ROLE,
    HTTP_400_BAD_REQUEST,
    HEADER_REQUEST_ID
)

from src.shared.constants.error_codes import (
    VALIDATION_ERROR,
    NOT_FOUND,
    EXTERNAL_SERVICE_ERROR
)

from src.shared.constants.environment import Environment

# Use in code
recommendations = recommendations[:MAX_RECOMMENDATIONS]

messages = [
    {"role": USER_ROLE, "content": "..."},
    {"role": ASSISTANT_ROLE, "content": "..."}
]

if settings.environment == Environment.PRODUCTION:
    # Production logic
    pass
```

---

## 8. Lifecycle Hooks

### Register Startup Hook
```python
from src.shared.lifecycle.app_lifecycle import LifecycleManager

lifecycle = LifecycleManager.get_instance()

@lifecycle.on_startup("vector_store", priority=2)
async def init_vector_store():
    """Initialize vector store on startup."""
    logger.info("Initializing vector store...")
    # Initialize vector store
    logger.info("Vector store initialized")

@lifecycle.on_shutdown("vector_store", priority=2)
async def close_vector_store():
    """Close vector store on shutdown."""
    logger.info("Closing vector store...")
    # Cleanup
    logger.info("Vector store closed")
```

---

## 9. Dependency Injection

### Register Dependencies
```python
from src.shared.dependencies.container import get_container
from src.shared.interfaces.base_interfaces import ILLMProvider

container = get_container()

# Register singleton
llm_provider = OpenAIProvider()
container.register_singleton(ILLMProvider, llm_provider)

# Register factory
def create_cache():
    return InMemoryCache()

container.register_factory(ICache, create_cache)
```

### Resolve Dependencies
```python
from src.shared.dependencies.container import get_container
from src.shared.interfaces.base_interfaces import ILLMProvider

container = get_container()
llm_provider = container.resolve(ILLMProvider)

# Use the provider
response = await llm_provider.generate(messages)
```

---

## 10. Request Context

### Set Context
```python
from src.shared.middleware.request_context import (
    RequestContext,
    set_request_context,
    get_request_id
)

context = RequestContext(
    request_id="req_123",
    correlation_id="corr_456",
    user_id="user_789"
)
set_request_context(context)

# Get current request ID
request_id = get_request_id()
```

---

## 11. FastAPI Integration

### Exception Handling (Automatic)
```python
from fastapi import APIRouter
from src.shared.exceptions import ValidationException

router = APIRouter()

@router.post("/example")
async def example():
    # Just raise exception, middleware handles it
    raise ValidationException("Invalid input", field="email")
    
    # Automatically converts to:
    # {
    #   "error": {
    #     "message": "Invalid input",
    #     "code": "VALIDATION_ERROR",
    #     "details": {"field": "email"}
    #   }
    # }
```

### Logging (Automatic)
```python
# Request logging happens automatically via LoggingMiddleware
# Every request gets:
# - Request ID generation
# - Request/response logging
# - Timing information
# - Context management
```

---

## Best Practices

### 1. Always use interfaces for dependencies
```python
# Good
def __init__(self, llm_provider: ILLMProvider):
    self._llm_provider = llm_provider

# Bad
def __init__(self, llm_provider: OpenAIProvider):
    self._llm_provider = llm_provider
```

### 2. Use dependency injection
```python
# Good
container = get_container()
service = container.resolve(ICatalogService)

# Bad
service = CatalogService()
```

### 3. Always get logger at module level
```python
# Good
logger = get_logger(__name__)

class MyClass:
    def method(self):
        logger.info("...")

# Bad
class MyClass:
    def __init__(self):
        self.logger = get_logger(__name__)
```

### 4. Use constants instead of magic values
```python
# Good
if len(recommendations) > MAX_RECOMMENDATIONS:
    recommendations = recommendations[:MAX_RECOMMENDATIONS]

# Bad
if len(recommendations) > 10:
    recommendations = recommendations[:10]
```

### 5. Raise specific exceptions
```python
# Good
raise NotFoundException("Assessment", assessment_id)

# Bad
raise Exception(f"Assessment {assessment_id} not found")
```

---

## Quick Command Reference

### Docker Commands
```bash
# Check status
docker ps

# View logs
docker logs conversational-shl-assessment-recommender-api-1 -f

# Restart after code changes
docker-compose restart

# Rebuild after dependency changes
docker-compose up -d --build

# Stop container
docker-compose down

# View health
curl http://localhost:8000/health
```

### Testing Infrastructure
```bash
# Test health endpoint
curl http://localhost:8000/health | python3 -m json.tool

# View API docs
open http://localhost:8000/docs

# Check logs
docker logs conversational-shl-assessment-recommender-api-1 --tail 100
```

---

## Next Steps

Phase 1 is complete. Future phases can now build upon this infrastructure:

- **Phase 2**: Implement Catalog (use IRepository, logging, exceptions)
- **Phase 3**: Implement Retrieval (use IEmbeddingProvider, IVectorStore)
- **Phase 4**: Implement Conversation (use ILLMProvider, request context)
- **Phase 5**: Implement Recommendation (use all interfaces, DI)

All infrastructure is production-ready and fully reusable.
