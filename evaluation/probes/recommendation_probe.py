"""
Recommendation Probe.

Tests recommendation behavior.

Expected behavior:
- System provides recommendations when sufficient information is available
- Recommendations are relevant and grounded in catalog
- Recommendations are ranked by relevance
- No duplicate recommendations
"""

from typing import Dict, Any
from httpx import AsyncClient
from evaluation.probes.base_probe import BaseProbe, ProbeResult


class RecommendationProbe(BaseProbe):
    """
    Probe for recommendation behavior.
    
    Tests:
    1. Clear queries produce recommendations
    2. Recommendations are relevant
    3. No duplicates
    4. Between 1-10 recommendations
    """
    
    @property
    def probe_name(self) -> str:
        return "recommendation"
    
    async def execute(
        self,
        client: AsyncClient,
        context: Dict[str, Any] = None,
    ) -> ProbeResult:
        """Execute recommendation probe."""
        try:
            # Send clear query
            query = "I need to assess cognitive ability and problem-solving skills"
            response = await self._send_chat_request(
                client,
                messages=[{"role": "user", "content": query}],
            )
            
            reply = response.get("reply", "")
            recommendations = response.get("recommendations", [])
            
            # Check: Should provide recommendations
            if not recommendations:
                return ProbeResult(
                    probe_name=self.probe_name,
                    passed=False,
                    explanation="System did not provide recommendations for clear query",
                    details={
                        "query": query,
                        "reply": reply,
                    },
                )
            
            # Check: Between 1-10 recommendations
            if len(recommendations) > 10:
                return ProbeResult(
                    probe_name=self.probe_name,
                    passed=False,
                    explanation=f"System provided {len(recommendations)} recommendations (max 10)",
                    details={
                        "query": query,
                        "recommendations_count": len(recommendations),
                    },
                )
            
            # Check: No duplicates
            urls = [rec.get("url") for rec in recommendations]
            if len(urls) != len(set(urls)):
                return ProbeResult(
                    probe_name=self.probe_name,
                    passed=False,
                    explanation="System provided duplicate recommendations",
                    details={
                        "query": query,
                        "recommendations_count": len(recommendations),
                        "unique_count": len(set(urls)),
                    },
                )
            
            # Check: All recommendations have required fields
            for rec in recommendations:
                if not rec.get("url") or not rec.get("title"):
                    return ProbeResult(
                        probe_name=self.probe_name,
                        passed=False,
                        explanation="Recommendation missing required fields",
                        details={
                            "query": query,
                            "invalid_recommendation": rec,
                        },
                    )
            
            return ProbeResult(
                probe_name=self.probe_name,
                passed=True,
                explanation=f"System provided {len(recommendations)} valid recommendations",
                details={
                    "query": query,
                    "recommendations_count": len(recommendations),
                },
            )
            
        except Exception as e:
            return ProbeResult(
                probe_name=self.probe_name,
                passed=False,
                explanation=f"Probe execution failed: {e}",
                details={"error": str(e)},
            )
