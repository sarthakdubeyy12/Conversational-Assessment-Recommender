"""
Execution trace.

Complete audit trail of pipeline execution.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.orchestrator.domain.pipeline_stage import PipelineStage


@dataclass
class StageTrace:
    """
    Single stage execution trace.
    """
    
    stage: PipelineStage
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: float = 0.0
    status: str = "running"  # running, completed, failed, skipped
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionTrace:
    """
    Complete execution audit trail.
    
    Tracks every stage for debugging and analysis.
    
    Design:
    - Chronological record
    - Performance metrics
    - Error tracking
    - Audit-ready
    """
    
    execution_id: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Stage traces
    stages: List[StageTrace] = field(default_factory=list)
    
    # Metrics
    total_duration_ms: float = 0.0
    stages_completed: int = 0
    stages_failed: int = 0
    stages_skipped: int = 0
    
    # Errors
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def start_stage(self, stage: PipelineStage) -> None:
        """Record stage start."""
        trace = StageTrace(
            stage=stage,
            started_at=datetime.utcnow(),
        )
        self.stages.append(trace)
    
    def complete_stage(
        self,
        stage: PipelineStage,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record stage completion."""
        for trace in reversed(self.stages):
            if trace.stage == stage and trace.status == "running":
                trace.completed_at = datetime.utcnow()
                trace.duration_ms = (
                    (trace.completed_at - trace.started_at).total_seconds() * 1000
                )
                trace.status = "completed"
                if metadata:
                    trace.metadata = metadata
                self.stages_completed += 1
                break
    
    def fail_stage(self, stage: PipelineStage, error: str) -> None:
        """Record stage failure."""
        for trace in reversed(self.stages):
            if trace.stage == stage and trace.status == "running":
                trace.completed_at = datetime.utcnow()
                trace.duration_ms = (
                    (trace.completed_at - trace.started_at).total_seconds() * 1000
                )
                trace.status = "failed"
                trace.error = error
                self.stages_failed += 1
                self.errors.append(f"{stage.value}: {error}")
                break
    
    def skip_stage(self, stage: PipelineStage, reason: str) -> None:
        """Record stage skip."""
        trace = StageTrace(
            stage=stage,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_ms=0.0,
            status="skipped",
            metadata={"reason": reason},
        )
        self.stages.append(trace)
        self.stages_skipped += 1
    
    def finalize(self) -> None:
        """Finalize trace."""
        self.completed_at = datetime.utcnow()
        self.total_duration_ms = (
            (self.completed_at - self.started_at).total_seconds() * 1000
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_duration_ms": self.total_duration_ms,
            "stages_completed": self.stages_completed,
            "stages_failed": self.stages_failed,
            "stages_skipped": self.stages_skipped,
            "errors": self.errors,
            "warnings": self.warnings,
            "stages": [
                {
                    "stage": s.stage.value,
                    "started_at": s.started_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                    "duration_ms": s.duration_ms,
                    "status": s.status,
                    "error": s.error,
                    "metadata": s.metadata,
                }
                for s in self.stages
            ],
        }
