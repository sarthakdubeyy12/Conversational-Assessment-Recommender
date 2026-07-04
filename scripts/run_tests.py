"""
Test runner script for Phase 15 - Production Testing Framework.

Runs the complete test suite with various options.
"""

import sys
import subprocess
from pathlib import Path


def print_section(title: str) -> None:
    """Print section header."""
    print(f"\n{'='*70}")
    print(f"{title}")
    print('='*70)


def run_unit_tests():
    """Run unit tests."""
    print_section("RUNNING UNIT TESTS")
    result = subprocess.run(
        ["pytest", "tests/unit/", "-v", "-m", "not slow"],
        cwd=Path(__file__).parent.parent,
    )
    return result.returncode == 0


def run_integration_tests():
    """Run integration tests."""
    print_section("RUNNING INTEGRATION TESTS")
    result = subprocess.run(
        ["pytest", "tests/integration/", "-v"],
        cwd=Path(__file__).parent.parent,
    )
    return result.returncode == 0


def run_e2e_tests():
    """Run end-to-end tests."""
    print_section("RUNNING END-TO-END TESTS")
    result = subprocess.run(
        ["pytest", "tests/e2e/", "-v"],
        cwd=Path(__file__).parent.parent,
    )
    return result.returncode == 0


def run_all_tests():
    """Run all tests."""
    print_section("RUNNING ALL TESTS")
    result = subprocess.run(
        ["pytest", "tests/", "-v"],
        cwd=Path(__file__).parent.parent,
    )
    return result.returncode == 0


def run_with_coverage():
    """Run tests with coverage report."""
    print_section("RUNNING TESTS WITH COVERAGE")
    result = subprocess.run(
        [
            "pytest",
            "tests/",
            "-v",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html",
        ],
        cwd=Path(__file__).parent.parent,
    )
    
    if result.returncode == 0:
        print("\n✅ Coverage report generated in htmlcov/index.html")
    
    return result.returncode == 0


def run_specific_test(test_path: str):
    """Run specific test file or directory."""
    print_section(f"RUNNING: {test_path}")
    result = subprocess.run(
        ["pytest", test_path, "-v"],
        cwd=Path(__file__).parent.parent,
    )
    return result.returncode == 0


def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run tests for SHL Assessment Recommender")
    parser.add_argument(
        "suite",
        nargs="?",
        choices=["unit", "integration", "e2e", "all", "coverage"],
        default="all",
        help="Test suite to run (default: all)",
    )
    parser.add_argument(
        "--path",
        type=str,
        help="Specific test file or directory to run",
    )
    
    args = parser.parse_args()
    
    print_section("PHASE 15: PRODUCTION TESTING FRAMEWORK")
    
    success = False
    
    try:
        if args.path:
            success = run_specific_test(args.path)
        elif args.suite == "unit":
            success = run_unit_tests()
        elif args.suite == "integration":
            success = run_integration_tests()
        elif args.suite == "e2e":
            success = run_e2e_tests()
        elif args.suite == "coverage":
            success = run_with_coverage()
        else:  # all
            success = run_all_tests()
        
        if success:
            print_section("TEST SUMMARY")
            print("✅ All tests passed!")
            sys.exit(0)
        else:
            print_section("TEST SUMMARY")
            print("❌ Some tests failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test runner error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
