"""
Quality Score Calculator.

Computes overall system quality score.

Responsibilities:
- Aggregate multiple metrics
- Weight different dimensions
- Produce final quality percentage
"""

from typing import Dict, Any


class QualityScoreCalculator:
    """
    Calculates overall system quality score.
    
    Combines multiple evaluation dimensions:
    - Recall@10
    - Success Rate
    - Probe Pass Rate
    - Latency Performance
    - Hallucination Rate
    """
    
    # Weights for different dimensions (must sum to 1.0)
    # Adjusted to value system reliability and safety over pure recall
    WEIGHTS = {
        "recall": 0.20,      # 20% - Important but not everything
        "success_rate": 0.30, # 30% - System reliability is critical
        "probes": 0.25,      # 25% - Behavioral correctness is key
        "latency": 0.15,     # 15% - Performance matters
        "hallucination": 0.10, # 10% - Safety baseline
    }
    
    @staticmethod
    def calculate(evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate quality score.
        
        Args:
            evaluation_data: Complete evaluation results
        
        Returns:
            Quality score breakdown
        """
        scores = {}
        
        # Recall score (0-100)
        recall = evaluation_data.get("summary", {}).get("average_recall_at_10", 0.0)
        scores["recall"] = recall * 100
        
        # Success rate score (0-100)
        success_rate = evaluation_data.get("summary", {}).get("success_rate", 0.0)
        scores["success_rate"] = success_rate * 100
        
        # Probe score (0-100)
        probes = evaluation_data.get("probes", [])
        if probes:
            passed_count = sum(1 for p in probes if p.get("passed", False))
            scores["probes"] = (passed_count / len(probes)) * 100
        else:
            scores["probes"] = 100  # No probes = perfect score
        
        # Latency score (0-100)
        latency_stats = evaluation_data.get("latency", {})
        p95_ms = latency_stats.get("p95_ms", 0)
        scores["latency"] = QualityScoreCalculator._latency_score(p95_ms)
        
        # Hallucination score (0-100)
        hallucination_count = evaluation_data.get("hallucinations", {}).get("total_hallucinations", 0)
        total_requests = evaluation_data.get("summary", {}).get("total_traces", 1)
        hallucination_rate = hallucination_count / max(total_requests, 1)
        scores["hallucination"] = max(0, 100 - (hallucination_rate * 100))
        
        # Calculate weighted overall score
        overall = sum(
            scores.get(key, 0) * weight
            for key, weight in QualityScoreCalculator.WEIGHTS.items()
        )
        
        return {
            "overall": round(overall, 1),
            "breakdown": {
                "recall": round(scores["recall"], 1),
                "success_rate": round(scores["success_rate"], 1),
                "probes": round(scores["probes"], 1),
                "latency": round(scores["latency"], 1),
                "hallucination": round(scores["hallucination"], 1),
            },
            "weights": QualityScoreCalculator.WEIGHTS,
        }
    
    @staticmethod
    def _latency_score(p95_ms: float) -> float:
        """
        Calculate latency score.
        
        Score degrades as P95 latency increases:
        - < 500ms: 100 points
        - 500-1000ms: 90-100 points (linear)
        - 1000-2000ms: 70-90 points (linear)
        - > 2000ms: 0-70 points (linear)
        
        Args:
            p95_ms: P95 latency in milliseconds
        
        Returns:
            Latency score (0-100)
        """
        if p95_ms < 500:
            return 100.0
        elif p95_ms < 1000:
            return 90 + (1000 - p95_ms) / 500 * 10
        elif p95_ms < 2000:
            return 70 + (2000 - p95_ms) / 1000 * 20
        else:
            return max(0, 70 - (p95_ms - 2000) / 100)
