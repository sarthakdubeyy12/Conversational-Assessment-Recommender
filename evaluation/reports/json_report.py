"""
JSON Report Generator.

Generates machine-readable JSON reports.

Responsibilities:
- Generate structured JSON output
- Include all metrics and details
- Support CI/CD integration
"""

import json
from typing import Dict, Any
from pathlib import Path
from datetime import datetime


class JSONReportGenerator:
    """
    Generates JSON evaluation reports.
    
    Used for:
    - CI/CD integration
    - Programmatic analysis
    - Data pipelines
    """
    
    @staticmethod
    def generate(
        evaluation_data: Dict[str, Any],
        output_path: Path = None,
    ) -> str:
        """
        Generate JSON report.
        
        Args:
            evaluation_data: Evaluation results
            output_path: Optional path to save report
        
        Returns:
            JSON string
        """
        # Add metadata
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "evaluation": evaluation_data,
        }
        
        # Generate JSON
        json_str = json.dumps(report, indent=2)
        
        # Save to file if requested
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(json_str)
        
        return json_str
