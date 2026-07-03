"""Catalog test fixtures."""

import pytest


@pytest.fixture
def sample_assessment_dict():
    """Sample assessment dictionary."""
    return {
        "id": "java-8-new",
        "name": "Java 8 (New)",
        "url": "https://www.shl.com/solutions/products/java-8/",
        "test_type": {"code": "K", "name": "Knowledge"},
        "description": "Java programming assessment",
    }
