"""
Markdown Report Generator.

Generates human-readable Markdown reports.

Responsibilities:
- Generate formatted Markdown
- Include summary, metrics, details
- Support GitHub/GitLab
"""

from typing import Dict, Any
from pathlib import Path
from datetime import datetime


class MarkdownReportGenerator:
    """
    Generates Markdown evaluation reports.
    
    Used for:
    - Human review
    - GitHub/GitLab comments
    - Documentation
    """
    
    @staticmethod
    def generate(
        evaluation_data: Dict[str, Any],
        output_path: Path = None,
    ) -> str:
        """
        Generate Markdown report.
        
        Args:
            evaluation_data: Evaluation results
            output_path: Optional path to save report
        
        Returns:
            Markdown string
        """
        lines = []
        
        # Header
        lines.append("# SHL Assessment Recommender - Evaluation Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.utcnow().isoformat()}")
        lines.append("")
        
        # Summary
        if "summary" in evaluation_data:
            summary = evaluation_data["summary"]
            lines.append("## Summary")
            lines.append("")
            lines.append(f"- **Total Traces:** {summary.get('total_traces', 0)}")
            lines.append(f"- **Success Rate:** {summary.get('success_rate', 0):.2%}")
            lines.append(f"- **Average Recall@10:** {summary.get('average_recall_at_10', 0):.4f}")
            lines.append(f"- **Average Latency:** {summary.get('average_latency_ms', 0):.2f}ms")
            lines.append("")
        
        # Probe Results
        if "probes" in evaluation_data:
            lines.append("## Behavioral Probes")
            lines.append("")
            probes = evaluation_data["probes"]
            
            for probe in probes:
                status = "✅ PASS" if probe.get("passed") else "❌ FAIL"
                lines.append(f"### {probe.get('probe_name', 'Unknown')} - {status}")
                lines.append("")
                lines.append(f"**Explanation:** {probe.get('explanation', '')}")
                lines.append("")
        
        # Latency Statistics
        if "latency" in evaluation_data:
            latency = evaluation_data["latency"]
            lines.append("## Latency Statistics")
            lines.append("")
            lines.append(f"- **Count:** {latency.get('count', 0)}")
            lines.append(f"- **Mean:** {latency.get('mean_ms', 0):.2f}ms")
            lines.append(f"- **Median (P50):** {latency.get('p50_ms', 0):.2f}ms")
            lines.append(f"- **P90:** {latency.get('p90_ms', 0):.2f}ms")
            lines.append(f"- **P95:** {latency.get('p95_ms', 0):.2f}ms")
            lines.append(f"- **P99:** {latency.get('p99_ms', 0):.2f}ms")
            lines.append("")
        
        # Quality Score
        if "quality_score" in evaluation_data:
            score = evaluation_data["quality_score"]
            lines.append("## Quality Score")
            lines.append("")
            lines.append(f"**Overall:** {score.get('overall', 0):.1f}%")
            lines.append("")
        
        markdown = "\n".join(lines)
        
        # Save to file if requested
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(markdown)
        
        return markdown
