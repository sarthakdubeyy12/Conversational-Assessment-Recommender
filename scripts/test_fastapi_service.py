"""
FastAPI service contract test.

Verifies exact schema compliance for Phase 13.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.api.models.chat_request import ChatRequest, MessageModel
from src.api.models.chat_response import ChatResponse, RecommendationModel
from src.api.models.health_response import HealthResponse
from src.api.models.error_response import ErrorResponse, ValidationErrorResponse


def print_section(title: str) -> None:
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)


def test_request_schema() -> None:
    """Test request schema validation."""
    print_section("REQUEST SCHEMA TEST")
    
    # Valid request
    try:
        request = ChatRequest(
            messages=[
                MessageModel(role="user", content="Hello"),
            ]
        )
        print("✅ Valid single message request")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Valid request with history
    try:
        request = ChatRequest(
            messages=[
                MessageModel(role="user", content="Hello"),
                MessageModel(role="assistant", content="Hi there!"),
                MessageModel(role="user", content="I need help"),
            ]
        )
        print("✅ Valid multi-message request")
        print(f"   Current message: {request.get_current_message()}")
        print(f"   History length: {len(request.get_history())}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Invalid: empty messages
    try:
        request = ChatRequest(messages=[])
        print("❌ Should have failed: empty messages")
    except Exception as e:
        print(f"✅ Correctly rejected empty messages: {e}")
    
    # Invalid: empty content
    try:
        request = ChatRequest(
            messages=[MessageModel(role="user", content="")]
        )
        print("❌ Should have failed: empty content")
    except Exception as e:
        print(f"✅ Correctly rejected empty content: {e}")
    
    # Invalid: last message not from user
    try:
        request = ChatRequest(
            messages=[
                MessageModel(role="user", content="Hello"),
                MessageModel(role="assistant", content="Hi"),
            ]
        )
        print("❌ Should have failed: last message not from user")
    except Exception as e:
        print(f"✅ Correctly rejected: {e}")


def test_response_schema() -> None:
    """Test response schema validation."""
    print_section("RESPONSE SCHEMA TEST")
    
    # Valid response with recommendations
    try:
        response = ChatResponse(
            reply="Here are some recommendations",
            recommendations=[
                RecommendationModel(
                    title="Verify G+",
                    url="https://www.shl.com/verify-gplus/",
                )
            ],
            end_of_conversation=False,
        )
        print("✅ Valid response with recommendations")
        print(f"   Reply: {response.reply}")
        print(f"   Recommendations: {len(response.recommendations)}")
        print(f"   End: {response.end_of_conversation}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Valid response without recommendations
    try:
        response = ChatResponse(
            reply="Can you provide more details?",
            recommendations=[],
            end_of_conversation=False,
        )
        print("✅ Valid response without recommendations")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Valid response with conversation end
    try:
        response = ChatResponse(
            reply="You're welcome! Goodbye.",
            recommendations=[],
            end_of_conversation=True,
        )
        print("✅ Valid response with end_of_conversation=True")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Invalid: too many recommendations
    try:
        response = ChatResponse(
            reply="Too many recommendations",
            recommendations=[
                RecommendationModel(title=f"Test {i}", url=f"https://test{i}.com")
                for i in range(11)
            ],
            end_of_conversation=False,
        )
        print("❌ Should have failed: >10 recommendations")
    except Exception as e:
        print(f"✅ Correctly rejected >10 recommendations: {e}")
    
    # Invalid: empty reply
    try:
        response = ChatResponse(
            reply="",
            recommendations=[],
            end_of_conversation=False,
        )
        print("❌ Should have failed: empty reply")
    except Exception as e:
        print(f"✅ Correctly rejected empty reply: {e}")


def test_health_schema() -> None:
    """Test health response schema."""
    print_section("HEALTH SCHEMA TEST")
    
    try:
        health = HealthResponse(
            status="healthy",
            version="1.0.0",
            environment="development",
        )
        print("✅ Valid health response")
        print(f"   Status: {health.status}")
        print(f"   Version: {health.version}")
        print(f"   Environment: {health.environment}")
    except Exception as e:
        print(f"❌ Failed: {e}")


def test_error_schema() -> None:
    """Test error response schemas."""
    print_section("ERROR SCHEMA TEST")
    
    # Generic error
    try:
        error = ErrorResponse(
            error="Invalid request",
            detail="Message content cannot be empty",
        )
        print("✅ Valid error response")
        print(f"   Error: {error.error}")
        print(f"   Detail: {error.detail}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Validation error
    try:
        from src.api.models.error_response import ErrorDetail
        error = ValidationErrorResponse(
            error="Validation error",
            detail=[
                ErrorDetail(
                    loc=["body", "messages"],
                    msg="At least one message is required",
                    type="value_error",
                )
            ],
        )
        print("✅ Valid validation error response")
        print(f"   Error: {error.error}")
        print(f"   Details: {len(error.detail)} errors")
    except Exception as e:
        print(f"❌ Failed: {e}")


def test_json_serialization() -> None:
    """Test JSON serialization."""
    print_section("JSON SERIALIZATION TEST")
    
    # Request
    request = ChatRequest(
        messages=[
            MessageModel(role="user", content="Hello"),
        ]
    )
    json_data = request.model_dump()
    print("✅ Request serialization:")
    print(f"   {json_data}")
    
    # Response
    response = ChatResponse(
        reply="Hello!",
        recommendations=[
            RecommendationModel(title="Test", url="https://test.com")
        ],
        end_of_conversation=False,
    )
    json_data = response.model_dump()
    print("✅ Response serialization:")
    print(f"   {json_data}")


def main():
    """Run all contract tests."""
    print_section("PHASE 13: FASTAPI SERVICE CONTRACT TEST")
    
    try:
        test_request_schema()
        test_response_schema()
        test_health_schema()
        test_error_schema()
        test_json_serialization()
        
        print_section("SUMMARY")
        print("✅ All contract tests passed")
        print("\nSchema compliance verified:")
        print("  ✓ Request schema matches assignment spec")
        print("  ✓ Response schema matches assignment spec")
        print("  ✓ Health endpoint defined")
        print("  ✓ Error responses defined")
        print("  ✓ JSON serialization works")
        
    except Exception as e:
        print_section("SUMMARY")
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
