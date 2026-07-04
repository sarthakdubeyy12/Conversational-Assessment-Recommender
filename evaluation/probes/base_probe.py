"""
Base Probe.

Abstract base for all behavioral probes.

Responsibilities:
- Define probe interface
- Execute probe logic
- Return PASS/FAIL with explanation
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List
from httpx import AsyncClient


@dataclass
class ProbeResult:
    """Result from a behavioral probe."""
    
    probe_name: str
    passed: bool
    explanation: str
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "probe_name": self.probe_name,
            "passed": self.passed,
            "explanation": self.explanation,
            "details": self.details,
        }


class BaseProbe(ABC):
    """
    Abstract base for behavioral probes.
    
    All probes must:
    1. Define probe_name
    2. Implement execute() method
    3. Return ProbeResult
    """
    
    @property
    @abstractmethod
    def probe_name(self) -> str:
        """Get probe name."""
        pass
    
    @abstractmethod
    async def execute(
        self,
        client: AsyncClient,
        context: Dict[str, Any] = None,
    ) -> ProbeResult:
        """
        Execute probe.
        
        Args:
            client: HTTP client for API calls
            context: Additional context
        
        Returns:
            Probe result
        """
        pass
    
    async def _send_chat_request(
        self,
        client: AsyncClient,
        messages: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Send chat request to API.
        
        Args:
            client: HTTP client
            messages: List of messages
        
        Returns:
            Response JSON
        """
        response = await client.post("/chat", json={"messages": messages})
        return response.json()
