"""
Test helper functions.

Provides utilities for common testing patterns.
"""

from typing import Dict, Any, List
import json


def assert_valid_url(url: str) -> None:
    """
    Assert URL is valid and from SHL domain.
    
    Args:
        url: URL to validate
    """
    assert url, "URL cannot be empty"
    assert url.startswith("http"), "URL must start with http/https"
    assert "shl.com" in url.lower(), "URL must be from shl.com domain"


def assert_catalog_grounded(assessment: Dict[str, Any], catalog: List[Dict[str, Any]]) -> None:
    """
    Assert assessment exists in catalog (no hallucination).
    
    Args:
        assessment: Assessment to check
        catalog: Catalog of valid assessments
    """
    assessment_urls = [a.get("url") for a in catalog]
    assert assessment.get("url") in assessment_urls, f"Assessment URL {assessment.get('url')} not in catalog"


def assert_response_schema(response: Dict[str, Any]) -> None:
    """
    Assert response follows required schema.
    
    Args:
        response: Response to validate
    """
    assert "reply" in response, "Response must have 'reply' field"
    assert "recommendations" in response, "Response must have 'recommendations' field"
    assert "end_of_conversation" in response, "Response must have 'end_of_conversation' field"
    
    assert isinstance(response["reply"], str), "'reply' must be string"
    assert isinstance(response["recommendations"], list), "'recommendations' must be list"
    assert isinstance(response["end_of_conversation"], bool), "'end_of_conversation' must be boolean"
    
    assert len(response["reply"]) > 0, "'reply' cannot be empty"
    assert len(response["recommendations"]) <= 10, "Maximum 10 recommendations"
    
    # Validate each recommendation
    for rec in response["recommendations"]:
        assert "title" in rec, "Recommendation must have 'title'"
        assert "url" in rec, "Recommendation must have 'url'"
        assert_valid_url(rec["url"])


def assert_no_secrets_in_response(response: Dict[str, Any]) -> None:
    """
    Assert response doesn't contain API keys or secrets.
    
    Args:
        response: Response to check
    """
    response_str = json.dumps(response).lower()
    
    forbidden_terms = [
        "api_key",
        "api key",
        "secret",
        "password",
        "token",
        "gsk_",
        "sk-",
    ]
    
    for term in forbidden_terms:
        assert term not in response_str, f"Response contains forbidden term: {term}"


def assert_deterministic(func, *args, **kwargs) -> None:
    """
    Assert function returns same result on multiple calls.
    
    Args:
        func: Function to test
        *args: Function arguments
        **kwargs: Function keyword arguments
    """
    result1 = func(*args, **kwargs)
    result2 = func(*args, **kwargs)
    
    assert result1 == result2, "Function is not deterministic"


def assert_within_time_limit(duration_ms: float, limit_ms: float) -> None:
    """
    Assert execution time is within limit.
    
    Args:
        duration_ms: Actual duration
        limit_ms: Maximum allowed duration
    """
    assert duration_ms <= limit_ms, f"Execution took {duration_ms}ms, limit is {limit_ms}ms"


def assert_confidence_range(confidence: float) -> None:
    """
    Assert confidence score is in valid range [0, 1].
    
    Args:
        confidence: Confidence score
    """
    assert 0.0 <= confidence <= 1.0, f"Confidence {confidence} must be between 0 and 1"
