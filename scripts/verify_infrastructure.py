#!/usr/bin/env python3
"""
Infrastructure Verification Script

Tests all Phase 1 Core Infrastructure components to ensure they work correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_configuration():
    """Test configuration management."""
    print("✓ Testing Configuration Management...")
    from src.shared.config.settings import get_settings
    
    settings = get_settings()
    assert settings is not None
    assert settings.environment in ["development", "staging", "production"]
    assert settings.port > 0
    print("  ✓ Configuration loaded successfully")
    print(f"  ✓ Environment: {settings.environment}")
    print(f"  ✓ Debug: {settings.debug}")


def test_logging():
    """Test logging system."""
    print("\n✓ Testing Logging System...")
    from src.shared.logging.logger import get_logger
    
    logger = get_logger("test")
    assert logger is not None
    logger.info("Test log message")
    print("  ✓ Logger created successfully")
    print("  ✓ Log message sent")


def test_exceptions():
    """Test exception framework."""
    print("\n✓ Testing Exception Framework...")
    from src.shared.exceptions import (
        ValidationException,
        NotFoundException,
        ConfigurationException,
        ExternalServiceException
    )
    
    try:
        raise ValidationException("Test validation", field="test_field")
    except ValidationException as e:
        assert e.error_code == "VALIDATION_ERROR"
        assert e.status_code == 400
        print("  ✓ ValidationException works")
    
    try:
        raise NotFoundException("TestResource", "123")
    except NotFoundException as e:
        assert e.error_code == "NOT_FOUND"
        assert e.status_code == 404
        print("  ✓ NotFoundException works")


def test_response_models():
    """Test response models."""
    print("\n✓ Testing Response Models...")
    from src.shared.schemas.response_models import (
        SuccessResponse,
        ErrorResponse,
        ErrorDetail,
        PaginationMeta
    )
    
    # Success response
    response = SuccessResponse(data={"test": "value"}, message="Success")
    assert response.data == {"test": "value"}
    print("  ✓ SuccessResponse works")
    
    # Error response
    error = ErrorResponse(
        error=ErrorDetail(
            message="Test error",
            code="TEST_ERROR",
            details={}
        )
    )
    assert error.error.code == "TEST_ERROR"
    print("  ✓ ErrorResponse works")
    
    # Pagination
    pagination = PaginationMeta(
        page=1,
        page_size=10,
        total_items=100,
        total_pages=10,
        has_next=True,
        has_previous=False
    )
    assert pagination.page == 1
    print("  ✓ PaginationMeta works")


def test_utilities():
    """Test utility functions."""
    print("\n✓ Testing Utilities...")
    
    # DateTime utils
    from src.shared.utils.datetime_utils import utcnow, to_iso_string
    now = utcnow()
    iso = to_iso_string(now)
    assert iso is not None
    print("  ✓ DateTime utils work")
    
    # UUID utils
    from src.shared.utils.uuid_utils import generate_uuid, generate_request_id
    uuid = generate_uuid()
    request_id = generate_request_id()
    assert len(uuid) == 36
    assert request_id.startswith("req_")
    print("  ✓ UUID utils work")
    
    # Validators
    from src.shared.utils.validators import is_valid_url, is_valid_email
    assert is_valid_url("https://example.com")
    assert is_valid_email("test@example.com")
    print("  ✓ Validators work")
    
    # Collection utils
    from src.shared.utils.collection_utils import chunk_list, deduplicate_list
    chunks = chunk_list([1, 2, 3, 4, 5], 2)
    assert len(chunks) == 3
    unique = deduplicate_list([1, 2, 2, 3, 3, 3])
    assert unique == [1, 2, 3]
    print("  ✓ Collection utils work")
    
    # Hash utils
    from src.shared.utils.hash_utils import hash_string
    hash_val = hash_string("test")
    assert len(hash_val) == 64  # SHA256 hex
    print("  ✓ Hash utils work")
    
    # Path utils
    from src.shared.utils.path_utils import get_project_root, get_data_directory
    root = get_project_root()
    data = get_data_directory()
    assert root.exists()
    assert data.exists()
    print("  ✓ Path utils work")


def test_interfaces():
    """Test base interfaces."""
    print("\n✓ Testing Base Interfaces...")
    from src.shared.interfaces.base_interfaces import (
        IRepository,
        ILLMProvider,
        IEmbeddingProvider,
        IVectorStore
    )
    
    # Just verify they can be imported
    assert IRepository is not None
    assert ILLMProvider is not None
    assert IEmbeddingProvider is not None
    assert IVectorStore is not None
    print("  ✓ All interfaces defined")


def test_constants():
    """Test constants."""
    print("\n✓ Testing Constants...")
    from src.shared.constants.api_constants import (
        MAX_RECOMMENDATIONS,
        USER_ROLE,
        ASSISTANT_ROLE
    )
    from src.shared.constants.error_codes import VALIDATION_ERROR, NOT_FOUND
    from src.shared.constants.environment import Environment
    
    assert MAX_RECOMMENDATIONS == 10
    assert USER_ROLE == "user"
    assert VALIDATION_ERROR == "VALIDATION_ERROR"
    assert Environment.DEVELOPMENT == "development"
    print("  ✓ All constants accessible")


def test_dependency_injection():
    """Test dependency injection."""
    print("\n✓ Testing Dependency Injection...")
    from src.shared.dependencies.container import get_container, reset_container
    
    # Reset for clean test
    reset_container()
    
    container = get_container()
    assert container is not None
    
    # Test singleton
    test_instance = "test_value"
    container.register_singleton(str, test_instance)
    resolved = container.resolve(str)
    assert resolved == test_instance
    print("  ✓ Singleton registration works")
    
    # Test factory
    def create_int():
        return 42
    
    container.register_factory(int, create_int)
    resolved_int = container.resolve(int)
    assert resolved_int == 42
    print("  ✓ Factory registration works")
    
    # Cleanup
    reset_container()


def test_lifecycle():
    """Test lifecycle management."""
    print("\n✓ Testing Lifecycle Management...")
    from src.shared.lifecycle.app_lifecycle import ApplicationLifecycle
    
    lifecycle = ApplicationLifecycle()
    
    executed = []
    
    @lifecycle.on_startup("test", priority=1)
    async def startup_hook():
        executed.append("startup")
    
    @lifecycle.on_shutdown("test", priority=1)
    async def shutdown_hook():
        executed.append("shutdown")
    
    import asyncio
    
    asyncio.run(lifecycle.startup())
    assert "startup" in executed
    print("  ✓ Startup hooks work")
    
    asyncio.run(lifecycle.shutdown())
    assert "shutdown" in executed
    print("  ✓ Shutdown hooks work")


def test_request_context():
    """Test request context."""
    print("\n✓ Testing Request Context...")
    from src.shared.middleware.request_context import (
        RequestContext,
        set_request_context,
        get_request_context,
        get_request_id,
        clear_request_context
    )
    
    context = RequestContext(request_id="test_123")
    set_request_context(context)
    
    retrieved = get_request_context()
    assert retrieved is not None
    assert retrieved.request_id == "test_123"
    print("  ✓ Context setting works")
    
    request_id = get_request_id()
    assert request_id == "test_123"
    print("  ✓ Request ID retrieval works")
    
    clear_request_context()
    retrieved = get_request_context()
    assert retrieved is None
    print("  ✓ Context clearing works")


def main():
    """Run all tests."""
    print("=" * 60)
    print("PHASE 1 INFRASTRUCTURE VERIFICATION")
    print("=" * 60)
    
    try:
        test_configuration()
        test_logging()
        test_exceptions()
        test_response_models()
        test_utilities()
        test_interfaces()
        test_constants()
        test_dependency_injection()
        test_lifecycle()
        test_request_context()
        
        print("\n" + "=" * 60)
        print("✅ ALL INFRASTRUCTURE TESTS PASSED")
        print("=" * 60)
        print("\nPhase 1 Core Infrastructure is working correctly!")
        print("Ready for Phase 2: Catalog Implementation")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
