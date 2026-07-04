"""
End-to-end API tests.

Tests Phase 13 - FastAPI Service with exact schema compliance.
"""

import pytest
from httpx import AsyncClient
from src.api.app import create_app
from tests.utils.test_helpers import (
    assert_response_schema,
    assert_valid_url,
    assert_no_secrets_in_response,
)


class TestAPIEndpoints:
    """Test suite for API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app instance."""
        return create_app()
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, app):
        """Test GET /health endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "status" in data
            assert "version" in data
            assert "environment" in data
            
            assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_valid_request(self, app):
        """Test POST /chat with valid request."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            request_data = {
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
            
            response = await client.post("/chat", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate exact schema
            assert_response_schema(data)
            
            # Check no secrets exposed
            assert_no_secrets_in_response(data)
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_with_history(self, app):
        """Test POST /chat with conversation history."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            request_data = {
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi! How can I help?"},
                    {"role": "user", "content": "I need help hiring"}
                ]
            }
            
            response = await client.post("/chat", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert_response_schema(data)
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_empty_messages(self, app):
        """Test POST /chat with empty messages array."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            request_data = {
                "messages": []
            }
            
            response = await client.post("/chat", json=request_data)
            
            # Should return 422 validation error
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_missing_role(self, app):
        """Test POST /chat with missing role field."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            request_data = {
                "messages": [
                    {"content": "Hello"}
                ]
            }
            
            response = await client.post("/chat", json=request_data)
            
            # Should return 422 validation error
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_empty_content(self, app):
        """Test POST /chat with empty content."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            request_data = {
                "messages": [
                    {"role": "user", "content": ""}
                ]
            }
            
            response = await client.post("/chat", json=request_data)
            
            # Should return 422 validation error
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_last_message_not_user(self, app):
        """Test POST /chat with last message from assistant."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            request_data = {
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi!"}
                ]
            }
            
            response = await client.post("/chat", json=request_data)
            
            # Should return 422 validation error
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_invalid_json(self, app):
        """Test POST /chat with invalid JSON."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/chat",
                content="invalid json",
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 422 validation error
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_max_recommendations(self, app):
        """Test POST /chat returns max 10 recommendations."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            request_data = {
                "messages": [
                    {"role": "user", "content": "I need assessments for all roles"}
                ]
            }
            
            response = await client.post("/chat", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            # Should never exceed 10 recommendations
            assert len(data["recommendations"]) <= 10
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_recommendation_urls(self, app):
        """Test all recommendation URLs are valid."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            request_data = {
                "messages": [
                    {"role": "user", "content": "Recommend cognitive assessments"}
                ]
            }
            
            response = await client.post("/chat", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            # Check all URLs are valid
            for rec in data["recommendations"]:
                assert_valid_url(rec["url"])
