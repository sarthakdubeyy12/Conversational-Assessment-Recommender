"""
Provider response model.

Standardized response from LLM providers.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class ProviderResponse:
    """
    Standardized LLM provider response.
    
    Normalizes responses across different providers.
    
    Design:
    - Provider-agnostic
    - Contains raw and parsed data
    - Includes usage metrics
    - Audit-ready
    """
    
    # Response content
    content: str
    raw_response: Dict[str, Any] = field(default_factory=dict)
    
    # Provider info
    provider: str = ""
    model: str = ""
    
    # Usage metrics
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    
    # Performance
    latency_ms: float = 0.0
    
    # Status
    success: bool = True
    error: Optional[str] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    request_id: str = ""
    
    # Retry info
    retry_count: int = 0
    used_fallback: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "provider": self.provider,
            "model": self.model,
            "success": self.success,
            "content_length": len(self.content),
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "latency_ms": self.latency_ms,
            "retry_count": self.retry_count,
            "used_fallback": self.used_fallback,
            "error": self.error,
        }
