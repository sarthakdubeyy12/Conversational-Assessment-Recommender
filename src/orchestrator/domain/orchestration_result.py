"""
Orchestration result.

Complete output from orchestrator.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
from src.orchestrator.domain.execution_trace import ExecutionTrace


@dataclass
class OrchestrationStatistics:
    """
    Orchestration performance statistics.
    """
    
    total_duration_ms: float
    state_reconstruction_ms: float = 0.0
    intent_detection_ms: float = 0.0
    guardrails_input_ms: float = 0.0
    retrieval_ms: float = 0.0
    recommendation_ms: float = 0.0
    comparison_ms: float = 0.0
    guardrails_output_ms: float = 0.0
    response_generation_ms: float = 0.0
    
    # Counts
    stages_executed: int = 0
    stages_skipped: int = 0
    stages_failed: int = 0


@dataclass
class OrchestrationResult:
    """
    Complete orchestration output.
    
    Contains all pipeline results and metadata.
    
    Design:
    - Immutable after creation
    - Comprehensive data
    - Audit-ready
    - API-ready
    """
    
    # Primary output
    response: str
    success: bool
    
    # Execution details
    execution_trace: ExecutionTrace
    statistics: OrchestrationStatistics
    
    # Component results (optional, for debugging)
    conversation_state: Optional[Any] = None
    intent_result: Optional[Any] = None
    guardrail_input_result: Optional[Any] = None
    retrieval_result: Optional[Any] = None
    recommendation_result: Optional[Any] = None
    comparison_result: Optional[Any] = None
    guardrail_output_result: Optional[Any] = None
    
    # Metadata
    session_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "response": self.response,
            "success": self.success,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "statistics": {
                "total_duration_ms": self.statistics.total_duration_ms,
                "stages_executed": self.statistics.stages_executed,
                "stages_skipped": self.statistics.stages_skipped,
                "stages_failed": self.statistics.stages_failed,
            },
            "trace": self.execution_trace.to_dict(),
        }
    
    def to_api_response(self) -> Dict[str, Any]:
        """Convert to minimal API response (no internals)."""
        return {
            "response": self.response,
            "success": self.success,
            "session_id": self.session_id,
        }
