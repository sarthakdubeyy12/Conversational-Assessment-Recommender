"""
Metric Aggregator.

Aggregates metrics from multiple evaluation dimensions.

Responsibilities:
- Collect metrics from all evaluation components
- Compute aggregate statistics
- Provide unified metric view
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class AggregatedMetrics:
    """Aggregated evaluation metrics."""
    
    # Replay metrics
    total_traces: int = 0
    successful_traces: int = 0
    failed_traces: int = 0
    success_rate: float = 0.0
    
    # Recall metrics
    average_recall_at_1: float = 0.0
    average_recall_at_3: float = 0.0
    average_recall_at_5: float = 0.0
    average_recall_at_10: float = 0.0
    
    # Probe metrics
    total_probes: int = 0
    passed_probes: int = 0
    failed_probes: int = 0
    probe_pass_rate: float = 0.0
    
    # Latency metrics
    mean_latency_ms: float = 0.0
    median_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Hallucination metrics
    total_hallucinations: int = 0
    hallucination_rate: float = 0.0
    
    # Quality metrics
    overall_quality_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "replay": {
                "total_traces": self.total_traces,
                "successful_traces": self.successful_traces,
                "failed_traces": self.failed_traces,
                "success_rate": round(self.success_rate, 4),
            },
            "recall": {
                "recall@1": round(self.average_recall_at_1, 4),
                "recall@3": round(self.average_recall_at_3, 4),
                "recall@5": round(self.average_recall_at_5, 4),
                "recall@10": round(self.average_recall_at_10, 4),
            },
            "probes": {
                "total_probes": self.total_probes,
                "passed_probes": self.passed_probes,
                "failed_probes": self.failed_probes,
                "pass_rate": round(self.probe_pass_rate, 4),
            },
            "latency": {
                "mean_ms": round(self.mean_latency_ms, 2),
                "median_ms": round(self.median_latency_ms, 2),
                "p95_ms": round(self.p95_latency_ms, 2),
                "p99_ms": round(self.p99_latency_ms, 2),
            },
            "hallucination": {
                "total_hallucinations": self.total_hallucinations,
                "rate": round(self.hallucination_rate, 4),
            },
            "quality": {
                "overall_score": round(self.overall_quality_score, 1),
            },
        }


class MetricAggregator:
    """
    Aggregates metrics from evaluation components.
    
    Collects and combines metrics from:
    - Replay harness
    - Behavioral probes
    - Latency collector
    - Hallucination detector
    - Quality calculator
    """
    
    @staticmethod
    def aggregate(evaluation_data: Dict[str, Any]) -> AggregatedMetrics:
        """
        Aggregate all metrics.
        
        Args:
            evaluation_data: Complete evaluation results
        
        Returns:
            Aggregated metrics
        """
        metrics = AggregatedMetrics()
        
        # Replay metrics
        summary = evaluation_data.get("summary", {})
        metrics.total_traces = summary.get("total_traces", 0)
        metrics.successful_traces = summary.get("successful", 0)
        metrics.failed_traces = summary.get("failed", 0)
        metrics.success_rate = summary.get("success_rate", 0.0)
        
        # Recall metrics
        metrics.average_recall_at_10 = summary.get("average_recall_at_10", 0.0)
        # Note: Would compute @1, @3, @5 from individual trace results
        
        # Probe metrics
        probes = evaluation_data.get("probes", [])
        metrics.total_probes = len(probes)
        metrics.passed_probes = sum(1 for p in probes if p.get("passed", False))
        metrics.failed_probes = metrics.total_probes - metrics.passed_probes
        if metrics.total_probes > 0:
            metrics.probe_pass_rate = metrics.passed_probes / metrics.total_probes
        
        # Latency metrics
        latency = evaluation_data.get("latency", {})
        metrics.mean_latency_ms = latency.get("mean_ms", 0.0)
        metrics.median_latency_ms = latency.get("median_ms", 0.0)
        metrics.p95_latency_ms = latency.get("p95_ms", 0.0)
        metrics.p99_latency_ms = latency.get("p99_ms", 0.0)
        
        # Hallucination metrics
        hallucinations = evaluation_data.get("hallucinations", {})
        metrics.total_hallucinations = hallucinations.get("total_hallucinations", 0)
        if metrics.total_traces > 0:
            metrics.hallucination_rate = metrics.total_hallucinations / metrics.total_traces
        
        # Quality score
        quality = evaluation_data.get("quality_score", {})
        metrics.overall_quality_score = quality.get("overall", 0.0)
        
        return metrics
