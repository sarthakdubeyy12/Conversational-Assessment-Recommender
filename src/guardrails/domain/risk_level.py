"""
Risk levels.

Classification of threat severity.
"""

from enum import Enum


class RiskLevel(str, Enum):
    """
    Risk severity levels.
    
    Determines urgency and handling of violations.
    """
    
    NONE = "none"           # No risk detected
    LOW = "low"             # Minor concern, allow with warning
    MEDIUM = "medium"       # Moderate risk, may block
    HIGH = "high"           # Significant risk, should block
    CRITICAL = "critical"   # Severe threat, must block
