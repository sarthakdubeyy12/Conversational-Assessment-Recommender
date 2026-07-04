"""
Latency Collector.

Collects and analyzes latency metrics.

Responsibilities:
- Measure API latency
- Compute percentiles (P50, P90, P95, P99)
- Track latency distributions
- Identify slow requests
"""

import statistics
from typing import List, Dict, Any


class LatencyCollector:
    """
    Collects and analyzes latency metrics.
    
    Tracks latency measurements and computes statistics.
    """
    
    def __init__(self):
        """Initialize latency collector."""
        self._latencies: List[float] = []
    
    def record(self, latency_ms: float):
        """
        Record a latency measurement.
        
        Args:
            latency_ms: Latency in milliseconds
        """
        self._latencies.append(latency_ms)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get latency statistics.
        
        Returns:
            Dictionary with min, max, mean, median, percentiles
        """
        if not self._latencies:
            return {
                "count": 0,
                "min_ms": 0.0,
                "max_ms": 0.0,
                "mean_ms": 0.0,
                "median_ms": 0.0,
                "p50_ms": 0.0,
                "p90_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0,
            }
        
        sorted_latencies = sorted(self._latencies)
        
        return {
            "count": len(self._latencies),
            "min_ms": round(min(self._latencies), 2),
            "max_ms": round(max(self._latencies), 2),
            "mean_ms": round(statistics.mean(self._latencies), 2),
            "median_ms": round(statistics.median(self._latencies), 2),
            "p50_ms": round(self._percentile(sorted_latencies, 50), 2),
            "p90_ms": round(self._percentile(sorted_latencies, 90), 2),
            "p95_ms": round(self._percentile(sorted_latencies, 95), 2),
            "p99_ms": round(self._percentile(sorted_latencies, 99), 2),
        }
    
    def _percentile(self, sorted_values: List[float], percentile: int) -> float:
        """
        Calculate percentile from sorted values.
        
        Args:
            sorted_values: Sorted list of values
            percentile: Percentile to calculate (0-100)
        
        Returns:
            Percentile value
        """
        if not sorted_values:
            return 0.0
        
        index = (percentile / 100) * (len(sorted_values) - 1)
        lower = int(index)
        upper = min(lower + 1, len(sorted_values) - 1)
        weight = index - lower
        
        return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight
    
    def get_slow_requests(self, threshold_ms: float = 1000.0) -> List[float]:
        """
        Get requests exceeding latency threshold.
        
        Args:
            threshold_ms: Latency threshold in milliseconds
        
        Returns:
            List of slow request latencies
        """
        return [lat for lat in self._latencies if lat > threshold_ms]
    
    def clear(self):
        """Clear all latency measurements."""
        self._latencies.clear()
