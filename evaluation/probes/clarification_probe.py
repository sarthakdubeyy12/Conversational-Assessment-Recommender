"""
Clarification Probe.

Tests clarification behavior.

Expected behavior:
- System should ask clarifying questions when intent is unclear
- System should not make assumptions
- System should guide user to provide necessary information
"""

from typing import Dict, Any
from httpx import AsyncClient
from evaluation.probes.base_probe import BaseProbe, ProbeResult


class ClarificationProbe(BaseProbe):
    """
    Probe for clarification behavior.
    
    Tests:
    1. Vague queries trigger clarification
    2. No premature recommendations
    3. Appropriate follow-up questions
    """
    
    @property
    def probe_name(self) -> str:
        return "clarification"
    
    async def execute(
        self,
        client: AsyncClient,
        context: Dict[str, Any] = None,
    ) -> ProbeResult:
        """Execute clarification probe."""
        try:
            # Send vague query
            response = await self._send_chat_request(
                client,
                messages=[{"role": "user", "content": "I need help"}],
            )
            
            reply = response.get("reply", "")
            recommendations = response.get("recommendations", [])
            
            # Check: Should NOT provide recommendations yet
            if recommendations:
                return ProbeResult(
                    probe_name=self.probe_name,
                    passed=False,
                    explanation="System provided recommendations for vague query",
                    details={
                        "query": "I need help",
                        "recommendations_count": len(recommendations),
                        "reply": reply,
                    },
                )
            
            # Check: Should ask clarifying questions
            clarification_indicators = [
                "what",
                "which",
                "tell me more",
                "can you provide",
                "help me understand",
                "role",
                "position",
                "hiring",
                "skills",
                "competencies",
            ]
            
            reply_lower = reply.lower()
            has_clarification = any(
                indicator in reply_lower
                for indicator in clarification_indicators
            )
            
            if not has_clarification:
                return ProbeResult(
                    probe_name=self.probe_name,
                    passed=False,
                    explanation="System did not ask clarifying questions",
                    details={
                        "query": "I need help",
                        "reply": reply,
                    },
                )
            
            return ProbeResult(
                probe_name=self.probe_name,
                passed=True,
                explanation="System correctly asked for clarification",
                details={
                    "query": "I need help",
                    "reply": reply,
                },
            )
            
        except Exception as e:
            return ProbeResult(
                probe_name=self.probe_name,
                passed=False,
                explanation=f"Probe execution failed: {e}",
                details={"error": str(e)},
            )
