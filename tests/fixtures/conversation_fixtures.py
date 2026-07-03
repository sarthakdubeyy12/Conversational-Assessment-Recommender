"""Conversation test fixtures."""

import pytest


@pytest.fixture
def sample_messages():
    """Sample conversation messages."""
    return [
        {"role": "user", "content": "I need to hire a Java developer"},
        {"role": "assistant", "content": "What seniority level?"},
        {"role": "user", "content": "Mid-level, around 4 years"},
    ]
