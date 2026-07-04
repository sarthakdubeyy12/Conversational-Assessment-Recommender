#!/bin/bash

# Phase 16 Verification Script
# Verifies evaluation framework implementation

set -e

echo "========================================================================"
echo "Phase 16: Production Evaluation Framework - Verification"
echo "========================================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counter
checks_passed=0
checks_failed=0

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((checks_passed++))
    else
        echo -e "${RED}✗${NC} $1 (missing)"
        ((checks_failed++))
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        ((checks_passed++))
    else
        echo -e "${RED}✗${NC} $1/ (missing)"
        ((checks_failed++))
    fi
}

echo "1. Checking evaluation directory structure..."
check_dir "evaluation"
check_dir "evaluation/replay"
check_dir "evaluation/recall"
check_dir "evaluation/probes"
check_dir "evaluation/latency"
check_dir "evaluation/hallucination"
check_dir "evaluation/regression"
check_dir "evaluation/scoring"
check_dir "evaluation/metrics"
check_dir "evaluation/reports"
check_dir "evaluation/traces"
echo ""

echo "2. Checking replay harness components..."
check_file "evaluation/replay/shl_replay_harness.py"
check_file "evaluation/traces/sample_traces.json"
echo ""

echo "3. Checking recall evaluation..."
check_file "evaluation/recall/__init__.py"
check_file "evaluation/recall/recall_calculator.py"
echo ""

echo "4. Checking behavioral probes..."
check_file "evaluation/probes/__init__.py"
check_file "evaluation/probes/base_probe.py"
check_file "evaluation/probes/clarification_probe.py"
check_file "evaluation/probes/recommendation_probe.py"
check_file "evaluation/probes/guardrails_probe.py"
check_file "evaluation/probes/comparison_probe.py"
echo ""

echo "5. Checking latency evaluation..."
check_file "evaluation/latency/__init__.py"
check_file "evaluation/latency/latency_collector.py"
echo ""

echo "6. Checking hallucination detection..."
check_file "evaluation/hallucination/__init__.py"
check_file "evaluation/hallucination/hallucination_detector.py"
echo ""

echo "7. Checking regression detection..."
check_file "evaluation/regression/__init__.py"
check_file "evaluation/regression/regression_checker.py"
echo ""

echo "8. Checking quality scoring..."
check_file "evaluation/scoring/__init__.py"
check_file "evaluation/scoring/quality_score.py"
echo ""

echo "9. Checking metrics aggregation..."
check_file "evaluation/metrics/__init__.py"
check_file "evaluation/metrics/metric_aggregator.py"
echo ""

echo "10. Checking report generators..."
check_file "evaluation/reports/__init__.py"
check_file "evaluation/reports/json_report.py"
check_file "evaluation/reports/markdown_report.py"
check_file "evaluation/reports/terminal_report.py"
echo ""

echo "11. Checking evaluation runner..."
check_file "scripts/run_evaluation.py"
echo ""

echo "12. Checking documentation..."
check_file "PHASE16_EVALUATION_FRAMEWORK.txt"
echo ""

echo "13. Validating Python syntax..."
python_files=(
    "evaluation/replay/shl_replay_harness.py"
    "evaluation/recall/recall_calculator.py"
    "evaluation/probes/base_probe.py"
    "evaluation/probes/clarification_probe.py"
    "evaluation/probes/recommendation_probe.py"
    "evaluation/probes/guardrails_probe.py"
    "evaluation/probes/comparison_probe.py"
    "evaluation/latency/latency_collector.py"
    "evaluation/hallucination/hallucination_detector.py"
    "evaluation/regression/regression_checker.py"
    "evaluation/scoring/quality_score.py"
    "evaluation/metrics/metric_aggregator.py"
    "evaluation/reports/json_report.py"
    "evaluation/reports/markdown_report.py"
    "evaluation/reports/terminal_report.py"
    "scripts/run_evaluation.py"
)

for file in "${python_files[@]}"; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $file syntax valid"
        ((checks_passed++))
    else
        echo -e "${RED}✗${NC} $file syntax error"
        ((checks_failed++))
    fi
done
echo ""

echo "14. Checking sample traces format..."
if python3 -c "import json; json.load(open('evaluation/traces/sample_traces.json'))" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Sample traces JSON valid"
    ((checks_passed++))
else
    echo -e "${RED}✗${NC} Sample traces JSON invalid"
    ((checks_failed++))
fi
echo ""

echo "========================================================================"
echo "Verification Summary"
echo "========================================================================"
echo -e "Checks passed: ${GREEN}$checks_passed${NC}"
echo -e "Checks failed: ${RED}$checks_failed${NC}"
echo ""

if [ $checks_failed -eq 0 ]; then
    echo -e "${GREEN}✅ Phase 16 verification PASSED${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run evaluation: python scripts/run_evaluation.py"
    echo "2. Review reports in evaluation/reports/"
    echo "3. Add more traces to evaluation/traces/"
    echo "4. Integrate into CI/CD pipeline"
    exit 0
else
    echo -e "${RED}❌ Phase 16 verification FAILED${NC}"
    echo ""
    echo "Please fix the issues above and run verification again."
    exit 1
fi
