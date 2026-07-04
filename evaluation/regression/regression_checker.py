"""
Regression Checker.

Detects quality regressions between evaluation runs.

Responsibilities:
- Compare current vs baseline metrics
- Detect significant regressions
- Generate regression report
"""

from typing import Dict, Any, List
from pathlib import Path
import json


class RegressionChecker:
    """
    Detects regressions in system quality.
    
    Compares current evaluation against baseline.
    """
    
    # Regression thresholds (percentage decrease that triggers alert)
    THRESHOLDS = {
        "recall@10": 0.05,      # 5% decrease
        "success_rate": 0.05,   # 5% decrease
        "probe_pass_rate": 0.10, # 10% decrease
        "latency_p95": 0.20,    # 20% increase (note: increase is bad for latency)
    }
    
    def __init__(self, baseline_path: Path = None):
        """
        Initialize regression checker.
        
        Args:
            baseline_path: Path to baseline evaluation JSON
        """
        self._baseline = None
        if baseline_path and baseline_path.exists():
            with open(baseline_path) as f:
                self._baseline = json.load(f)
    
    def check(self, current_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for regressions.
        
        Args:
            current_evaluation: Current evaluation results
        
        Returns:
            Regression report
        """
        if not self._baseline:
            return {
                "has_baseline": False,
                "message": "No baseline found - this will become the baseline",
                "regressions": [],
            }
        
        regressions = []
        
        # Check Recall@10
        current_recall = current_evaluation.get("summary", {}).get("average_recall_at_10", 0)
        baseline_recall = self._baseline.get("evaluation", {}).get("summary", {}).get("average_recall_at_10", 0)
        if baseline_recall > 0:
            recall_change = (current_recall - baseline_recall) / baseline_recall
            if recall_change < -self.THRESHOLDS["recall@10"]:
                regressions.append({
                    "metric": "recall@10",
                    "current": current_recall,
                    "baseline": baseline_recall,
                    "change_pct": recall_change * 100,
                    "threshold_pct": -self.THRESHOLDS["recall@10"] * 100,
                })
        
        # Check Success Rate
        current_success = current_evaluation.get("summary", {}).get("success_rate", 0)
        baseline_success = self._baseline.get("evaluation", {}).get("summary", {}).get("success_rate", 0)
        if baseline_success > 0:
            success_change = (current_success - baseline_success) / baseline_success
            if success_change < -self.THRESHOLDS["success_rate"]:
                regressions.append({
                    "metric": "success_rate",
                    "current": current_success,
                    "baseline": baseline_success,
                    "change_pct": success_change * 100,
                    "threshold_pct": -self.THRESHOLDS["success_rate"] * 100,
                })
        
        # Check Latency P95 (increase is bad)
        current_latency = current_evaluation.get("latency", {}).get("p95_ms", 0)
        baseline_latency = self._baseline.get("evaluation", {}).get("latency", {}).get("p95_ms", 0)
        if baseline_latency > 0:
            latency_change = (current_latency - baseline_latency) / baseline_latency
            if latency_change > self.THRESHOLDS["latency_p95"]:
                regressions.append({
                    "metric": "latency_p95",
                    "current": current_latency,
                    "baseline": baseline_latency,
                    "change_pct": latency_change * 100,
                    "threshold_pct": self.THRESHOLDS["latency_p95"] * 100,
                })
        
        return {
            "has_baseline": True,
            "regressions_detected": len(regressions) > 0,
            "regression_count": len(regressions),
            "regressions": regressions,
        }
    
    def save_baseline(
        self,
        evaluation_data: Dict[str, Any],
        baseline_path: Path,
    ):
        """
        Save current evaluation as baseline.
        
        Args:
            evaluation_data: Evaluation to save
            baseline_path: Path to save baseline
        """
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        with open(baseline_path, "w") as f:
            json.dump(evaluation_data, f, indent=2)
