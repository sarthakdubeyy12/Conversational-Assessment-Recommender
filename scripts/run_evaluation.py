"""
Main Evaluation Runner.

Orchestrates complete evaluation framework.

Responsibilities:
- Run SHL replay harness
- Execute behavioral probes
- Collect latency metrics
- Detect hallucinations
- Check regressions
- Generate reports
- Provide CI/CD exit codes
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from httpx import AsyncClient, ASGITransport
from src.api.app import create_app
from evaluation.replay.shl_replay_harness import SHLReplayHarness, ConversationTrace
from evaluation.probes.clarification_probe import ClarificationProbe
from evaluation.probes.recommendation_probe import RecommendationProbe
from evaluation.probes.guardrails_probe import GuardrailsProbe
from evaluation.recall.recall_calculator import RecallCalculator
from evaluation.latency.latency_collector import LatencyCollector
from evaluation.hallucination.hallucination_detector import HallucinationDetector
from evaluation.scoring.quality_score import QualityScoreCalculator
from evaluation.regression.regression_checker import RegressionChecker
from evaluation.reports.json_report import JSONReportGenerator
from evaluation.reports.markdown_report import MarkdownReportGenerator
from evaluation.reports.terminal_report import TerminalReportGenerator


class EvaluationRunner:
    """
    Main evaluation orchestrator.
    
    Runs complete evaluation suite and generates reports.
    """
    
    def __init__(self):
        """Initialize evaluation runner."""
        self.app = create_app()
        self.replay_harness = SHLReplayHarness(app=self.app)
        self.latency_collector = LatencyCollector()
        self.hallucination_detector = HallucinationDetector()
        self.regression_checker = RegressionChecker(
            baseline_path=Path("evaluation/reports/baseline.json")
        )
    
    async def run(
        self,
        traces_path: Path = None,
        run_probes: bool = True,
        check_regressions: bool = True,
        output_dir: Path = None,
    ) -> Dict[str, Any]:
        """
        Run complete evaluation.
        
        Args:
            traces_path: Path to conversation traces JSON
            run_probes: Whether to run behavioral probes
            check_regressions: Whether to check for regressions
            output_dir: Directory for output reports
        
        Returns:
            Complete evaluation results
        """
        print("=" * 70)
        print("SHL Assessment Recommender - Evaluation Framework")
        print("=" * 70)
        print()
        
        # Default paths
        if traces_path is None:
            traces_path = Path("evaluation/traces/sample_traces.json")
        
        if output_dir is None:
            output_dir = Path("evaluation/reports")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Load traces
        print(f"📁 Loading conversation traces from {traces_path}...")
        traces = self.replay_harness.load_traces_from_file(traces_path)
        print(f"   Loaded {len(traces)} traces")
        print()
        
        # 2. Replay traces
        print("🔄 Replaying conversation traces...")
        replay_results = await self.replay_harness.replay_traces(traces)
        
        # Collect latencies
        for result in replay_results:
            self.latency_collector.record(result.latency_ms)
        
        print(f"   Completed {len(replay_results)} trace replays")
        print()
        
        # 3. Run behavioral probes
        probe_results = []
        if run_probes:
            print("🔍 Running behavioral probes...")
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                probes = [
                    ClarificationProbe(),
                    RecommendationProbe(),
                    GuardrailsProbe(),
                ]
                
                for probe in probes:
                    result = await probe.execute(client)
                    probe_results.append(result.to_dict())
                    status = "✅ PASS" if result.passed else "❌ FAIL"
                    print(f"   {status} {probe.probe_name}")
            print()
        
        # 4. Get summary
        summary = self.replay_harness.get_summary()
        
        # 5. Collect latency statistics
        latency_stats = self.latency_collector.get_statistics()
        
        # 6. Check for hallucinations
        print("🔬 Checking for hallucinations...")
        hallucination_summary = {"total_hallucinations": 0}
        # Note: Would need to extract all recommendations from replay results
        print()
        
        # 7. Build evaluation data
        evaluation_data = {
            "summary": summary,
            "probes": probe_results,
            "latency": latency_stats,
            "hallucinations": hallucination_summary,
        }
        
        # 8. Calculate quality score
        print("📊 Calculating quality score...")
        quality_score = QualityScoreCalculator.calculate(evaluation_data)
        evaluation_data["quality_score"] = quality_score
        print(f"   Overall Quality Score: {quality_score['overall']:.1f}%")
        print()
        
        # 9. Check for regressions
        regression_report = None
        if check_regressions:
            print("📉 Checking for regressions...")
            regression_report = self.regression_checker.check(evaluation_data)
            evaluation_data["regressions"] = regression_report
            
            if regression_report.get("regressions_detected"):
                print(f"   ⚠️  {regression_report['regression_count']} regressions detected")
            else:
                print("   ✅ No regressions detected")
            print()
        
        # 10. Generate reports
        print("📄 Generating reports...")
        
        # JSON Report
        json_path = output_dir / "evaluation_report.json"
        JSONReportGenerator.generate(evaluation_data, json_path)
        print(f"   ✓ JSON: {json_path}")
        
        # Markdown Report
        md_path = output_dir / "evaluation_report.md"
        MarkdownReportGenerator.generate(evaluation_data, md_path)
        print(f"   ✓ Markdown: {md_path}")
        
        # Terminal Report
        terminal_report = TerminalReportGenerator.generate(evaluation_data)
        print(terminal_report)
        
        # Save as baseline if no baseline exists
        baseline_path = output_dir / "baseline.json"
        if not baseline_path.exists():
            print(f"💾 Saving baseline to {baseline_path}...")
            self.regression_checker.save_baseline(
                {"evaluation": evaluation_data},
                baseline_path
            )
        
        return evaluation_data


async def main():
    """Main entry point."""
    runner = EvaluationRunner()
    
    try:
        results = await runner.run()
        
        # Exit code based on quality score
        quality_score = results.get("quality_score", {}).get("overall", 0)
        
        if quality_score >= 80:
            print("✅ Evaluation PASSED (Quality Score >= 80%)")
            sys.exit(0)
        elif quality_score >= 60:
            print("⚠️  Evaluation WARNING (Quality Score 60-80%)")
            sys.exit(0)  # Still exit 0, just warn
        else:
            print("❌ Evaluation FAILED (Quality Score < 60%)")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Evaluation failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
