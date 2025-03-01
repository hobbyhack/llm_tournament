#!/usr/bin/env python
"""
Tournament consistency analyzer script.

This script analyzes multiple tournament result files to determine
how consistent the tournament results are across runs.
"""

import os
import sys
import argparse
import glob
from analysis.consistency_analyzer import ConsistencyAnalyzer


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="LLM Tournament Consistency Analyzer")

    parser.add_argument(
        "--results-dir",
        type=str,
        default="./results",
        help="Directory containing tournament result files",
    )

    parser.add_argument(
        "--pattern",
        type=str,
        default="tournament_*.json",
        help="Glob pattern for tournament result files",
    )

    parser.add_argument(
        "--group-by",
        type=str,
        help="Field to group tournaments by (e.g., config.llm.default_model)",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="./analysis_results",
        help="Directory for output files",
    )

    parser.add_argument(
        "--summary-file",
        type=str,
        default="consistency_summary.csv",
        help="Filename for summary CSV",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed information during analysis",
    )

    return parser.parse_args()


def main():
    """Run the consistency analysis."""
    args = parse_arguments()

    # Create the output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Print diagnostic information
    print("\nAnalyzer Diagnostics:")
    print(f"Results directory: {os.path.abspath(args.results_dir)}")
    print(f"Output directory: {os.path.abspath(args.output_dir)}")
    print(
        f"Summary file path: {os.path.abspath(os.path.join(args.output_dir, args.summary_file))}"
    )

    # Count files matching pattern
    files = glob.glob(os.path.join(args.results_dir, args.pattern))
    print(f"Files matching pattern '{args.pattern}': {len(files)}")
    if files:
        print(f"Sample file: {os.path.basename(files[0])}")

    # Create the analyzer
    analyzer = ConsistencyAnalyzer(results_dir=args.results_dir)

    # Print header
    print("\n" + "=" * 70)
    print("LLM TOURNAMENT CONSISTENCY ANALYZER")
    print("=" * 70)

    # Load tournaments
    grouped_tournaments = analyzer.load_tournaments(
        pattern=args.pattern, group_by=args.group_by
    )

    if not grouped_tournaments:
        print("No tournaments found. Exiting.")
        return 1

    # Run analysis
    results = analyzer.analyze_all_metrics(grouped_tournaments)

    # Print summary for each group
    for group_name, metrics in results.items():
        print("\n" + "-" * 70)
        print(f"GROUP: {group_name} ({metrics['tournaments']} tournaments)")
        print("-" * 70)

        # Ranking consistency
        rank_metrics = metrics.get("ranking_consistency", {}).get("overall", {})
        print(f"Ranking Stability: {rank_metrics.get('rank_stability', 0):.3f}")
        print(f"Average Rank StdDev: {rank_metrics.get('avg_stdev', 0):.3f}")

        # Win rate consistency
        win_metrics = metrics.get("win_rate_consistency", {}).get("overall", {})
        win_cv = win_metrics.get("avg_coefficient_of_variation", 0)
        win_consistency = 1 - win_cv
        print(f"Win Rate Consistency: {win_consistency:.3f}")

        # Matchup consistency
        matchup_metrics = metrics.get("matchup_consistency", {}).get("overall", {})
        print(f"Matchup Consistency: {matchup_metrics.get('avg_consistency', 0):.3f}")

        # Score consistency
        score_metrics = metrics.get("score_consistency", {}).get("overall", {})
        score_cv = score_metrics.get("avg_coefficient_of_variation", 0)
        score_consistency = 1 - score_cv
        print(f"Score Consistency: {score_consistency:.3f}")

        if args.verbose:
            # Print details for top contenders by inconsistency
            print("\nMost variable contenders by rank:")
            contender_ranks = metrics.get("ranking_consistency", {}).get(
                "contenders", {}
            )
            sorted_contenders = sorted(
                contender_ranks.items(), key=lambda x: x[1]["std_dev"], reverse=True
            )
            for contender_id, data in sorted_contenders[:3]:
                print(
                    f"  {contender_id}: StdDev = {data['std_dev']:.2f}, Range = {data['range']} (Ranks: {data['ranks']})"
                )

    # If we have multiple groups, compare them
    if len(results) > 1:
        print("\n" + "=" * 70)
        print("GROUP COMPARISON")
        print("=" * 70)

        # Determine which group has the best consistency for each metric
        ranking_stability = [
            (
                group,
                metrics.get("ranking_consistency", {})
                .get("overall", {})
                .get("rank_stability", 0),
            )
            for group, metrics in results.items()
        ]
        best_ranking = max(ranking_stability, key=lambda x: x[1])

        win_rate_consistency = [
            (
                group,
                1
                - metrics.get("win_rate_consistency", {})
                .get("overall", {})
                .get("avg_coefficient_of_variation", 0),
            )
            for group, metrics in results.items()
        ]
        best_win_rate = max(win_rate_consistency, key=lambda x: x[1])

        matchup_consistency = [
            (
                group,
                metrics.get("matchup_consistency", {})
                .get("overall", {})
                .get("avg_consistency", 0),
            )
            for group, metrics in results.items()
        ]
        best_matchup = max(matchup_consistency, key=lambda x: x[1])

        score_consistency = [
            (
                group,
                1
                - metrics.get("score_consistency", {})
                .get("overall", {})
                .get("avg_coefficient_of_variation", 0),
            )
            for group, metrics in results.items()
        ]
        best_score = max(score_consistency, key=lambda x: x[1])

        print(f"Best Ranking Stability: {best_ranking[0]} ({best_ranking[1]:.3f})")
        print(f"Best Win Rate Consistency: {best_win_rate[0]} ({best_win_rate[1]:.3f})")
        print(f"Best Matchup Consistency: {best_matchup[0]} ({best_matchup[1]:.3f})")
        print(f"Best Score Consistency: {best_score[0]} ({best_score[1]:.3f})")

    # Export results
    summary_path = os.path.join(args.output_dir, args.summary_file)
    analyzer.export_summary_to_csv(summary_path)
    analyzer.export_detailed_results(args.output_dir)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"Summary CSV: {summary_path}")
    print(f"Detailed results: {args.output_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
