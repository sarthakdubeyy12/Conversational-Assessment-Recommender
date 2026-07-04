"""
Official SHL Replay Harness.

Simulates the exact evaluation process used by SHL's automated grading system.

This harness:
1. Reads conversation traces from JSON
2. Replays them exactly through the /chat endpoint
3. Simulates the user by feeding back messages from the trace
4. Stops when end_of_conversation becomes true
5. Compares final recommendations against expected assessments
6. Computes Recall@10 automatically
7. Produces detailed summary report

Design:
- Exact simulation of SHL evaluation
- Stateless execution
- Deterministic replay
- Comprehensive metrics
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from httpx import AsyncClient, ASGITransport
from src.api.app import create_app


class ConversationTrace:
    """
    Conversation trace for replay.
    
    Format:
    {
        "trace_id": "trace_001",
        "description": "Senior software engineer hiring",
        "turns": [
            {"role": "user", "content": "I need to hire..."},
            {"role": "assistant", "content": "..."}
        ],
        "expected_assessments": [
            "https://www.shl.com/...",
            "https://www.shl.com/..."
        ]
    }
    """
    
    def __init__(self, data: Dict[str, Any]):
        self.trace_id = data["trace_id"]
        self.description = data.get("description", "")
        self.turns = data["turns"]
        self.expected_assessments = data.get("expected_assessments", [])
    
    def get_user_messages(self) -> List[str]:
        """Extract user messages in order."""
        return [turn["content"] for turn in self.turns if turn["role"] == "user"]


class ReplayResult:
    """Result from replaying a conversation trace."""
    
    def __init__(
        self,
        trace_id: str,
        success: bool,
        turns_executed: int,
        recommendations: List[Dict[str, Any]],
        expected_assessments: List[str],
        recall_at_10: float,
        latency_ms: float,
        error: Optional[str] = None,
    ):
        self.trace_id = trace_id
        self.success = success
        self.turns_executed = turns_executed
        self.recommendations = recommendations
        self.expected_assessments = expected_assessments
        self.recall_at_10 = recall_at_10
        self.latency_ms = latency_ms
        self.error = error
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "success": self.success,
            "turns_executed": self.turns_executed,
            "recommendations_count": len(self.recommendations),
            "expected_count": len(self.expected_assessments),
            "recall_at_10": round(self.recall_at_10, 4),
            "latency_ms": round(self.latency_ms, 2),
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }


class SHLReplayHarness:
    """
    Official SHL Replay Harness.
    
    Mimics the exact evaluation process used by SHL.
    
    Responsibilities:
    - Load conversation traces
    - Replay through /chat endpoint
    - Simulate multi-turn conversations
    - Collect recommendations
    - Compute Recall@10
    - Generate evaluation reports
    """
    
    def __init__(self, app=None):
        """
        Initialize replay harness.
        
        Args:
            app: FastAPI app instance (optional, creates one if not provided)
        """
        self._app = app or create_app()
        self._results: List[ReplayResult] = []
    
    async def replay_trace(
        self,
        trace: ConversationTrace,
        max_turns: int = 20,
    ) -> ReplayResult:
        """
        Replay a single conversation trace.
        
        Args:
            trace: Conversation trace to replay
            max_turns: Maximum turns to execute
        
        Returns:
            Replay result with metrics
        """
        start_time = asyncio.get_event_loop().time()
        conversation_history = []
        final_recommendations = []
        turns_executed = 0
        error = None
        
        try:
            transport = ASGITransport(app=self._app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # Replay each user message
                for user_message in trace.get_user_messages():
                    if turns_executed >= max_turns:
                        break
                    
                    # Build messages array
                    messages = conversation_history + [
                        {"role": "user", "content": user_message}
                    ]
                    
                    # Call /chat endpoint
                    response = await client.post("/chat", json={"messages": messages})
                    
                    if response.status_code != 200:
                        error = f"HTTP {response.status_code}: {response.text}"
                        break
                    
                    data = response.json()
                    assistant_reply = data["reply"]
                    recommendations = data.get("recommendations", [])
                    end_of_conversation = data.get("end_of_conversation", False)
                    
                    # Update conversation history
                    conversation_history.append({"role": "user", "content": user_message})
                    conversation_history.append({"role": "assistant", "content": assistant_reply})
                    
                    # Collect recommendations
                    if recommendations:
                        final_recommendations = recommendations
                    
                    turns_executed += 1
                    
                    # Stop if conversation ended
                    if end_of_conversation:
                        break
            
            # Calculate Recall@10
            recall = self._calculate_recall_at_10(
                final_recommendations,
                trace.expected_assessments,
            )
            
            # Calculate latency
            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            result = ReplayResult(
                trace_id=trace.trace_id,
                success=error is None,
                turns_executed=turns_executed,
                recommendations=final_recommendations,
                expected_assessments=trace.expected_assessments,
                recall_at_10=recall,
                latency_ms=latency_ms,
                error=error,
            )
            
        except Exception as e:
            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            result = ReplayResult(
                trace_id=trace.trace_id,
                success=False,
                turns_executed=turns_executed,
                recommendations=[],
                expected_assessments=trace.expected_assessments,
                recall_at_10=0.0,
                latency_ms=latency_ms,
                error=str(e),
            )
        
        self._results.append(result)
        return result
    
    async def replay_traces(
        self,
        traces: List[ConversationTrace],
    ) -> List[ReplayResult]:
        """
        Replay multiple conversation traces.
        
        Args:
            traces: List of conversation traces
        
        Returns:
            List of replay results
        """
        results = []
        for trace in traces:
            result = await self.replay_trace(trace)
            results.append(result)
        return results
    
    def _calculate_recall_at_10(
        self,
        recommendations: List[Dict[str, Any]],
        expected_assessments: List[str],
    ) -> float:
        """
        Calculate Recall@10.
        
        Recall@10 = (# expected assessments in top 10) / (# expected assessments)
        
        Args:
            recommendations: List of recommendations returned
            expected_assessments: List of expected assessment URLs
        
        Returns:
            Recall@10 score [0.0, 1.0]
        """
        if not expected_assessments:
            return 1.0  # No expectations, perfect score
        
        # Extract URLs from recommendations (top 10)
        recommended_urls = [
            rec.get("url", "") for rec in recommendations[:10]
        ]
        
        # Count matches
        matches = sum(
            1 for expected in expected_assessments
            if expected in recommended_urls
        )
        
        return matches / len(expected_assessments)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Generate summary statistics.
        
        Returns:
            Summary dictionary with metrics
        """
        if not self._results:
            return {
                "total_traces": 0,
                "message": "No traces evaluated",
            }
        
        successful = [r for r in self._results if r.success]
        failed = [r for r in self._results if not r.success]
        
        avg_recall = sum(r.recall_at_10 for r in successful) / len(successful) if successful else 0.0
        avg_latency = sum(r.latency_ms for r in self._results) / len(self._results)
        
        return {
            "total_traces": len(self._results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(self._results),
            "average_recall_at_10": round(avg_recall, 4),
            "average_latency_ms": round(avg_latency, 2),
            "results": [r.to_dict() for r in self._results],
        }
    
    def load_traces_from_file(self, filepath: Path) -> List[ConversationTrace]:
        """
        Load conversation traces from JSON file.
        
        Args:
            filepath: Path to JSON file
        
        Returns:
            List of conversation traces
        """
        with open(filepath, "r") as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return [ConversationTrace(trace) for trace in data]
        else:
            return [ConversationTrace(data)]
