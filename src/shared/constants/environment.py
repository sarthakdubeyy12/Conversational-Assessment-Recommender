"""
Environment constants.

Defines environment names and related constants.
"""

from enum import Enum


class Environment(str, Enum):
    """Application environments."""
    
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


# Environment names
ENV_DEVELOPMENT = "development"
ENV_STAGING = "staging"
ENV_PRODUCTION = "production"
ENV_TESTING = "testing"

# Debug flags
DEBUG_ENABLED = True
DEBUG_DISABLED = False
