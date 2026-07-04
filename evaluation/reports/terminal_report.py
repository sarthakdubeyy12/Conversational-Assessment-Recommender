"""
Terminal Report Generator.

Generates colorized terminal output.

Responsibilities:
- Generate formatted terminal output
- Use colors for pass/fail
- Provide quick summary
"""

from typing import Dict, Any


class TerminalReportGenerator:
    """
    Generates terminal evaluation reports.
    
    Used for:
    - Quick feedback
    - CI/CD logs
    - Development workflow
    """
    
    # ANSI color codes
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    
    @staticmethod
    def generate(evaluation_data: Dict[str, Any]) -> str:
        """
        Generate terminal report.
        
        Args:
            evaluation_data: Evaluation results
        
        Returns:
            Formatted terminal string
        """
        lines = []
        
        # Header
        lines.append(f"\n{TerminalReportGenerator.BOLD}{'='*70}{TerminalReportGenerator.RESET}")
        lines.append(f"{TerminalReportGenerator.BOLD}SHL Assessment Recommender - Evaluation Report{TerminalReportGenerator.RESET}")
        lines.append(f"{TerminalReportGenerator.BOLD}{'='*70}{TerminalReportGenerator.RESET}\n")
        
        # Summary
        if "summary" in evaluation_data:
            summary = evaluation_data["summary"]
            success_rate = summary.get('success_rate', 0)
            
            # Color based on success rate
            if success_rate >= 0.9:
                color = TerminalReportGenerator.GREEN
            elif success_rate >= 0.7:
                color = TerminalReportGenerator.YELLOW
            else:
                color = TerminalReportGenerator.RED
            
            lines.append(f"{TerminalReportGenerator.BOLD}SUMMARY{TerminalReportGenerator.RESET}")
            lines.append(f"  Total Traces: {summary.get('total_traces', 0)}")
            lines.append(f"  Success Rate: {color}{success_rate:.2%}{TerminalReportGenerator.RESET}")
            lines.append(f"  Avg Recall@10: {summary.get('average_recall_at_10', 0):.4f}")
            lines.append(f"  Avg Latency: {summary.get('average_latency_ms', 0):.2f}ms")
            lines.append("")
        
        # Probes
        if "probes" in evaluation_data:
            lines.append(f"{TerminalReportGenerator.BOLD}BEHAVIORAL PROBES{TerminalReportGenerator.RESET}")
            probes = evaluation_data["probes"]
            
            for probe in probes:
                passed = probe.get("passed", False)
                status_color = TerminalReportGenerator.GREEN if passed else TerminalReportGenerator.RED
                status_text = "PASS" if passed else "FAIL"
                
                lines.append(f"  {status_color}{status_text}{TerminalReportGenerator.RESET} {probe.get('probe_name', 'Unknown')}")
                lines.append(f"      {probe.get('explanation', '')}")
            lines.append("")
        
        # Quality Score
        if "quality_score" in evaluation_data:
            score = evaluation_data["quality_score"]
            overall = score.get("overall", 0)
            
            # Color based on score
            if overall >= 90:
                color = TerminalReportGenerator.GREEN
            elif overall >= 70:
                color = TerminalReportGenerator.YELLOW
            else:
                color = TerminalReportGenerator.RED
            
            lines.append(f"{TerminalReportGenerator.BOLD}QUALITY SCORE{TerminalReportGenerator.RESET}")
            lines.append(f"  Overall: {color}{overall:.1f}%{TerminalReportGenerator.RESET}")
            lines.append("")
        
        lines.append(f"{TerminalReportGenerator.BOLD}{'='*70}{TerminalReportGenerator.RESET}\n")
        
        return "\n".join(lines)
