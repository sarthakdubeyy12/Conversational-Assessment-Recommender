"""
Pytest configuration and shared fixtures.

Provides reusable fixtures for all tests.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_user_message():
    """Sample user message for testing."""
    return "I need to hire a senior software engineer with Python skills"


@pytest.fixture
def sample_catalog_assessment():
    """Sample assessment from catalog."""
    return {
        "name": "Verify G+",
        "url": "https://www.shl.com/solutions/products/assessments/verify-gplus/",
        "category": "Cognitive Ability",
        "description": "Measures general cognitive ability",
        "competencies": ["Problem Solving", "Analytical Thinking"],
        "skills": ["Critical Thinking", "Logical Reasoning"],
        "duration": "45 minutes",
        "languages": ["English", "Spanish", "French"],
        "seniority_levels": ["Entry Level", "Mid Level", "Senior"],
    }


@pytest.fixture
def sample_conversation_history():
    """Sample conversation history."""
    return [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help you?"},
        {"role": "user", "content": "I need to assess problem-solving skills"},
    ]


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Based on your requirements, I recommend Verify G+ assessment."
                }
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 20,
            "total_tokens": 120,
        },
    }


@pytest.fixture
def sample_hiring_context():
    """Sample hiring context."""
    return {
        "role_title": "Senior Software Engineer",
        "seniority": "senior",
        "skills": ["Python", "Problem Solving", "Leadership"],
        "competencies": ["Technical Skills", "Team Leadership"],
        "years_experience": 5,
    }
