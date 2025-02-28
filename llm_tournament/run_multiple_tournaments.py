#!/usr/bin/env python
"""
Runs multiple LLM tournaments with different models or settings.

This script runs a series of tournaments with different configurations
to allow for consistency analysis.
"""

import os
import sys
import argparse
import subprocess
import json
import time
import datetime
from typing import List, Dict, Any


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run Multiple LLM Tournaments")

    parser.add_argument(
        "--contenders", type=str, required=True, help="Path to contenders JSON file"
    )

    parser.add_argument(
        "--framework",
        type=str,
        required=True,
        help="Path to assessment framework JSON file",
    )

    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of tournament runs per configuration",
    )

    parser.add_argument(
        "--models",
        type=str,
        nargs="+",
        default=["llama3"],
        help="List of models to test (e.g., 'llama3 mistral phi3')",
    )

    parser.add_argument(
        "--headless", action="store_true", help="Run tournaments in headless mode"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="./results",
        help="Directory for tournament results",
    )

    parser.add_argument(
        "--run-analysis",
        action="store_true",
        help="Run consistency analysis after all tournaments complete",
    )

    return parser.parse_args()


def run_tournament(
    contenders_file: str,
    framework_file: str,
    model: str,
    output_file: str,
    run_id: str,
    headless: bool = False,
) -> bool:
    """
    Run a single tournament with the specified parameters.

    Args:
        contenders_file: Path to contenders JSON file
        framework_file: Path to assessment framework JSON file
        model: LLM model to use
        output_file: Path to output results file
        run_id: Unique ID for this run
        headless: Whether to run without UI

    Returns:
        True if successful, False otherwise
    """
    command = [
        sys.executable,
        "main.py",
        "--contenders",
        contenders_file,
        "--framework",
        framework_file,
        "--model",
        model,
        "--output",
        output_file,
    ]

    if headless:
        command.append("--headless")

    print(f"\nRunning tournament {run_id} with model {model}")
    print(f"Command: {' '.join(command)}")

    try:
        process = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Check if the output file was created
        if os.path.exists(output_file):
            print(f"Tournament {run_id} completed successfully")
            return True
        else:
            print(f"Tournament {run_id} failed: output file not created")
            return False

    except subprocess.CalledProcessError as e:
        print(f"Tournament {run_id} failed with code {e.returncode}")
        print(f"Error output: {e.stderr.strip()}")
        return False
    except Exception as e:
        print(f"Unexpected error running tournament {run_id}: {str(e)}")
        return False


def run_multiple_tournaments(args: argparse.Namespace) -> Dict[str, List[str]]:
    """
    Run multiple tournaments with different models.

    Args:
        args: Command line arguments

    Returns:
        Dictionary mapping models to lists of result file paths
    """
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate timestamp for this batch
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Dictionary to track result files by model
    results_by_model = {}

    # Run tournaments for each model
    for model in args.models:
        print(f"\n{'=' * 70}")
        print(f"RUNNING {args.runs} TOURNAMENTS WITH MODEL: {model}")
        print(f"{'=' * 70}")

        model_results = []

        for run in range(1, args.runs + 1):
            # Generate unique output filename
            run_id = f"{model}_{timestamp}_run{run}"
            output_file = os.path.join(args.output_dir, f"tournament_{run_id}.json")

            # Run the tournament
            success = run_tournament(
                contenders_file=args.contenders,
                framework_file=args.framework,
                model=model,
                output_file=output_file,
                run_id=run_id,
                headless=args.headless,
            )

            if success:
                model_results.append(output_file)

            # Short delay between runs
            time.sleep(1)

        results_by_model[model] = model_results

        print(
            f"\nCompleted {len(model_results)}/{args.runs} tournaments with model {model}"
        )

    return results_by_model


def run_consistency_analysis(results_by_model: Dict[str, List[str]]):
    """
    Run consistency analysis on the tournament results.

    Args:
        results_by_model: Dictionary mapping models to lists of result file paths
    """
    print(f"\n{'=' * 70}")
    print("RUNNING CONSISTENCY ANALYSIS")
    print(f"{'=' * 70}")

    command = [
        sys.executable,
        "analyze_consistency.py",
        "--group-by",
        "config.llm.default_model",
        "--verbose",
    ]

    try:
        process = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print("Consistency analysis completed successfully")

        # Print the analysis output for visibility
        if process.stdout:
            print("\nAnalysis Results:")
            print(process.stdout)

    except subprocess.CalledProcessError as e:
        print(f"Consistency analysis failed with code {e.returncode}")
        print(f"Error output: {e.stderr.strip()}")
    except Exception as e:
        print(f"Unexpected error during analysis: {str(e)}")


def check_environment():
    """
    Check that the environment is properly set up.
    Reports on the Python interpreter and available packages.
    """
    print(f"\n{'=' * 70}")
    print("ENVIRONMENT DIAGNOSTICS")
    print(f"{'=' * 70}")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")

    # Check for required packages
    required_packages = ["pydantic", "langchain", "yaml", "numpy", "scipy"]
    for package in required_packages:
        try:
            # Try to import the package
            module = __import__(package)
            # Get version if available
            version = getattr(module, "__version__", "unknown")
            print(f"{package}: Available (version {version})")
        except ImportError:
            print(f"{package}: NOT FOUND - This may cause issues!")

    print(f"{'=' * 70}\n")


def main():
    """Run multiple tournaments and optional analysis."""
    args = parse_arguments()

    print(f"\n{'=' * 70}")
    print("MULTIPLE LLM TOURNAMENT RUNNER")
    print(f"{'=' * 70}")
    print(f"Contenders: {args.contenders}")
    print(f"Framework: {args.framework}")
    print(f"Models: {args.models}")
    print(f"Runs per model: {args.runs}")
    print(f"Output directory: {args.output_dir}")

    # Check environment before running
    check_environment()

    # Run tournaments
    results = run_multiple_tournaments(args)

    # Print summary
    print(f"\n{'=' * 70}")
    print("TOURNAMENT RUNS SUMMARY")
    print(f"{'=' * 70}")

    for model, files in results.items():
        print(f"Model: {model}")
        print(f"  Completed: {len(files)}/{args.runs}")

        if files:
            first_file = files[0]
            with open(first_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    contenders = len(
                        data.get("statistics", {}).get("total_contenders", 0)
                    )
                    matches = data.get("statistics", {}).get("total_matches", 0)
                    print(f"  Contenders: {contenders}")
                    print(f"  Matches per tournament: {matches}")
                except Exception as e:
                    print(f"  Error reading result file: {e}")

        print()

    # Run analysis if requested
    if args.run_analysis:
        run_consistency_analysis(results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
