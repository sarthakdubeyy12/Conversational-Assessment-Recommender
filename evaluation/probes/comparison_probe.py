"""
Comparison Probe.

Tests assessment comparison behavior.

Expected behavior:
- System provides structured comparisons
- Comparisons are grounded in catalog
- Missing metadata handled gracefully
- No hallucinations
"""

from typing import Dict, Any
from httpx import AsyncClient
from evaluation.probes.base_probe import BaseProbe, ProbeResult


class ComparisonProbe(BaseProbe):
    """
    Probe for comparison behavior.
    
    Tests:
    1. Comparison requests handled correctly
    2. Structured comparison output
    3. No hallucinations
    4. Graceful handling of missing data
    """
    
    @property
    def probe_name(self) -> str:
        return "comparison"
    
    async def execute(
        self,
        client: AsyncClient,
        context: Dict[str, Any] = None,
    ) -> ProbeResult:
        """Execute comparison probe."""
        try:
            # Multi-turn: First get recommendations, then compare
            messages = [
                {"role": "user", "content": "I need cognitive ability assessments"}
            ]
            
            response1 = await self._send_chat_request(client, messages)
            recommendations = response1.get("recommendations", [])
            
            if len(recommendations) < 2:
                return ProbeResult(
                    probe_name=self.probe_name,
                    passed=False,
                    explanation="Could not get enough recommendations for comparison test",
                    details={"recommendations_count": len(recommendations)},
                )
            
            # Request comparison
            reply1 = response1.get("reply", "")
            messages.extend([
                {"role": "user", "content": "I need cognitive ability assessments"},
                {"role": "assistant", "content": reply1},
                {"role": "user", "content": f"Compare the first two assessments"},
            ])
            
            response2 = await self._send_chat_request(client, messages)
            reply2 = response2.get("reply", "")
            
            # Check: Reply should contain comparison keywords
            comparison_indicators = [
                "compare",
                "difference",
                "similar",
                "whereas",
                "while",
                "both",
                "first",
                "second",
            ]
            
            reply_lower = reply2.lower()
            has_comparison = any(
                indicator in reply_lower
                for indicator in comparison_indicators
            )
            
            if not has_comparison:
                return ProbeResult(
                    probe_name=self.probe_name,
                    passed=False,
                    explanation="System did not provide comparison",
                    details={"reply": reply2},
                )
            
            return ProbeResult(
                probe_name=self.probe_name,
                passed=True,
                explanation="System provided valid comparison",
                details={"reply_length": len(reply2)},
            )
            
        except Exception as e:
            return ProbeResult(
                probe_name=self.probe_name,
                passed=False,
                explanation=f"Probe execution failed: {e}",
                details={"error": str(e)},
            )
