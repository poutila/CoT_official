#!/usr/bin/env python3
"""Test runner for RAG Pipeline test suite."""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run tests with pytest.

    Args:
        test_type: Type of tests to run (all, unit, integration)
        verbose: Enable verbose output
        coverage: Generate coverage report
    """
    import pytest

    args = []

    # Select test type
    if test_type == "unit":
        args.extend(["-m", "unit", "unit/"])
    elif test_type == "integration":
        args.extend(["-m", "integration", "integration/"])
    elif test_type == "all":
        args.append(".")
    else:
        print(f"Unknown test type: {test_type}")
        return 1

    # Add verbosity
    if verbose:
        args.append("-vv")
    else:
        args.append("-v")

    # Add coverage
    if coverage:
        args.extend(["--cov=..", "--cov-report=term-missing", "--cov-report=html:htmlcov"])

    # Add color
    args.append("--color=yes")

    # Run tests
    print(f"Running {test_type} tests...")
    print(f"Command: pytest {' '.join(args)}")

    return pytest.main(args)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run RAG Pipeline tests")
    parser.add_argument(
        "type",
        nargs="?",
        default="all",
        choices=["all", "unit", "integration"],
        help="Type of tests to run (default: all)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-c", "--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--quick", action="store_true", help="Skip slow tests")
    parser.add_argument("--markers", action="store_true", help="List available test markers")

    args = parser.parse_args()

    if args.markers:
        print("Available test markers:")
        print("  unit         - Unit tests (fast, isolated)")
        print("  integration  - Integration tests (may use real resources)")
        print("  slow         - Slow tests (> 1 second)")
        print("  requires_model - Tests that require ML models")
        return 0

    # Install pytest if needed
    try:
        import pytest
    except ImportError:
        print("Installing pytest...")
        import subprocess

        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pytest", "pytest-cov", "pytest-mock"]
        )

    # Run tests
    if args.quick:
        # Skip slow tests
        sys.argv.extend(["-m", "not slow"])

    return run_tests(args.type, args.verbose, args.coverage)


if __name__ == "__main__":
    sys.exit(main())
