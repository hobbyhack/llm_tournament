"""
Tournament consistency analyzer for the LLM Tournament application.

This module analyzes multiple tournament result files to determine
how consistent the tournament results are across runs.
"""

import os
import json
import glob
from typing import Dict, List, Any, Optional, Tuple
import statistics
import math
import csv
from collections import defaultdict
import datetime

# For statistical analysis
try:
    import numpy as np
    import scipy.stats as stats

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class ConsistencyAnalyzer:
    """
    Analyzes tournament results across multiple runs to determine consistency.
    """

    def __init__(self, results_dir: str = "./results"):
        """
        Initialize the consistency analyzer.

        Args:
            results_dir: Directory containing tournament result JSON files
        """
        self.results_dir = results_dir
        self.tournaments = []
        self.contenders = set()
        self.metrics = {}

    def load_tournaments(
        self, pattern: str = "tournament_*.json", group_by: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Load all tournament result files matching the pattern.

        Args:
            pattern: Glob pattern for tournament result files
            group_by: Optional field to group tournaments by (e.g., "config.llm.default_model")

        Returns:
            Dictionary of tournament results grouped by the specified field, or a single group if not specified
        """
        file_paths = glob.glob(os.path.join(self.results_dir, pattern))

        if not file_paths:
            print(
                f"No tournament result files found matching pattern '{pattern}' in {self.results_dir}"
            )
            return {}

        print(f"Found {len(file_paths)} tournament result files")

        grouped_tournaments = defaultdict(list)

        for file_path in file_paths:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tournament_data = json.load(f)

                # Extract the group key if specified
                group_key = "all"
                if group_by:
                    parts = group_by.split(".")
                    value = tournament_data
                    for part in parts:
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        else:
                            value = "unknown"
                            break
                    group_key = str(value)

                # Add to the appropriate group
                grouped_tournaments[group_key].append(tournament_data)

                # Track all contenders across tournaments
                for ranking in tournament_data.get("rankings", []):
                    self.contenders.add(ranking.get("contender_id"))

            except Exception as e:
                print(f"Error loading tournament result from {file_path}: {e}")

        self.tournaments = list(grouped_tournaments.values())
        print(
            f"Loaded {sum(len(group) for group in grouped_tournaments.values())} tournaments in {len(grouped_tournaments)} groups"
        )

        return dict(grouped_tournaments)

    def calculate_ranking_consistency(
        self, tournament_group: List[Dict]
    ) -> Dict[str, Any]:
        """
        Calculate ranking consistency across tournaments.

        Args:
            tournament_group: List of tournament results

        Returns:
            Dictionary of ranking consistency metrics
        """
        if not tournament_group:
            return {"error": "No tournaments provided"}

        # Extract rankings from each tournament
        rankings_by_tournament = []
        for tournament in tournament_group:
            rankings = {}
            try:
                for ranking in tournament.get("rankings", []):
                    contender_id = ranking.get("contender_id")
                    rank = ranking.get("rank")
                    if contender_id and rank:
                        rankings[contender_id] = rank

                # Only add if we have at least one valid ranking
                if rankings:
                    rankings_by_tournament.append(rankings)
                else:
                    print(f"Warning: Tournament has no valid rankings")
            except Exception as e:
                print(f"Error extracting rankings from tournament: {e}")

        # Skip further processing if we don't have enough data
        if len(rankings_by_tournament) < 2:
            return {
                "overall": {
                    "error": f"Need at least 2 tournaments with rankings, found {len(rankings_by_tournament)}",
                    "avg_stdev": 0,
                    "rank_stability": 0,
                    "contender_count": 0,
                    "tournament_count": len(rankings_by_tournament),
                },
                "contenders": {},
            }

        # Calculate consistency metrics for each contender
        contender_metrics = {}
        for contender_id in self.contenders:
            ranks = [
                rankings.get(contender_id)
                for rankings in rankings_by_tournament
                if contender_id in rankings
            ]
            if len(ranks) >= 2:  # Need at least 2 tournaments for statistics
                contender_metrics[contender_id] = {
                    "ranks": ranks,
                    "mean_rank": statistics.mean(ranks),
                    "median_rank": statistics.median(ranks),
                    "std_dev": statistics.stdev(ranks) if len(ranks) > 1 else 0,
                    "min_rank": min(ranks),
                    "max_rank": max(ranks),
                    "range": max(ranks) - min(ranks),
                    "tournaments": len(ranks),
                }

        # Calculate overall ranking consistency
        overall = {
            "avg_stdev": (
                statistics.mean([m["std_dev"] for m in contender_metrics.values()])
                if contender_metrics
                else 0
            ),
            "rank_stability": 0,  # Will calculate below if scipy is available
            "contender_count": len(contender_metrics),
            "tournament_count": len(tournament_group),
        }

        # Calculate rank correlation coefficients if scipy is available
        if SCIPY_AVAILABLE and len(tournament_group) > 1:
            correlations = []

            # Get all pairs of tournaments
            for i in range(len(rankings_by_tournament)):
                for j in range(i + 1, len(rankings_by_tournament)):
                    t1 = rankings_by_tournament[i]
                    t2 = rankings_by_tournament[j]

                    # Get common contenders
                    common = set(t1.keys()) & set(t2.keys())

                    if len(common) > 2:  # Need at least 3 points for correlation
                        ranks1 = [t1[c] for c in common]
                        ranks2 = [t2[c] for c in common]

                        # Calculate Spearman's rank correlation
                        corr, _ = stats.spearmanr(ranks1, ranks2)
                        if not math.isnan(corr):
                            correlations.append(corr)

            if correlations:
                overall["rank_stability"] = statistics.mean(correlations)
                overall["min_correlation"] = min(correlations)
                overall["max_correlation"] = max(correlations)

        return {"overall": overall, "contenders": contender_metrics}

    def calculate_win_rate_consistency(
        self, tournament_group: List[Dict]
    ) -> Dict[str, Any]:
        """
        Calculate win rate consistency across tournaments.

        Args:
            tournament_group: List of tournament results

        Returns:
            Dictionary of win rate consistency metrics
        """
        if not tournament_group:
            return {"error": "No tournaments provided"}

        # Extract win rates from each tournament
        win_rates_by_tournament = []
        for tournament in tournament_group:
            win_rates = {}
            try:
                for ranking in tournament.get("rankings", []):
                    contender_id = ranking.get("contender_id")
                    if not contender_id:
                        continue

                    stats = ranking.get("stats", {})

                    # Handle different possible structures for stats
                    if isinstance(stats, dict):
                        matches_played = stats.get("matches_played", 0)
                        wins = stats.get("wins", 0)

                        if matches_played > 0:
                            win_rate = wins / matches_played
                        else:
                            win_rate = 0
                    else:
                        # Try to access attributes if stats is not a dict
                        try:
                            matches_played = getattr(stats, "matches_played", 0)
                            wins = getattr(stats, "wins", 0)

                            if matches_played > 0:
                                win_rate = wins / matches_played
                            else:
                                win_rate = 0
                        except Exception:
                            # Skip if we can't extract the stats
                            continue

                    win_rates[contender_id] = win_rate

                # Only add if we have at least one valid win rate
                if win_rates:
                    win_rates_by_tournament.append(win_rates)
                else:
                    print(f"Warning: Tournament has no valid win rates")
            except Exception as e:
                print(f"Error extracting win rates from tournament: {e}")

        # Skip further processing if we don't have enough data
        if len(win_rates_by_tournament) < 2:
            return {
                "overall": {
                    "error": f"Need at least 2 tournaments with win rates, found {len(win_rates_by_tournament)}",
                    "avg_stdev": 0,
                    "avg_coefficient_of_variation": 0,
                    "contender_count": 0,
                    "tournament_count": len(win_rates_by_tournament),
                },
                "contenders": {},
            }

        # Calculate consistency metrics for each contender
        contender_metrics = {}
        for contender_id in self.contenders:
            rates = [
                rates.get(contender_id, 0)
                for rates in win_rates_by_tournament
                if contender_id in rates
            ]
            if len(rates) >= 2:  # Need at least 2 tournaments for statistics
                mean_rate = statistics.mean(rates)
                contender_metrics[contender_id] = {
                    "win_rates": rates,
                    "mean_win_rate": mean_rate,
                    "median_win_rate": statistics.median(rates),
                    "std_dev": statistics.stdev(rates) if len(rates) > 1 else 0,
                    "min_win_rate": min(rates),
                    "max_win_rate": max(rates),
                    "range": max(rates) - min(rates),
                    "coefficient_of_variation": (
                        statistics.stdev(rates) / mean_rate
                        if mean_rate > 0 and len(rates) > 1
                        else 0
                    ),
                    "tournaments": len(rates),
                }

        # Calculate overall win rate consistency
        cv_values = [
            m["coefficient_of_variation"]
            for m in contender_metrics.values()
            if not math.isnan(m["coefficient_of_variation"])
            and m["coefficient_of_variation"] != 0
        ]

        overall = {
            "avg_stdev": (
                statistics.mean([m["std_dev"] for m in contender_metrics.values()])
                if contender_metrics
                else 0
            ),
            "avg_coefficient_of_variation": (
                statistics.mean(cv_values) if cv_values else 0
            ),
            "contender_count": len(contender_metrics),
            "tournament_count": len(tournament_group),
        }

        return {"overall": overall, "contenders": contender_metrics}

    def calculate_matchup_consistency(
        self, tournament_group: List[Dict]
    ) -> Dict[str, Any]:
        """
        Calculate consistency of match outcomes between pairs of contenders.

        Args:
            tournament_group: List of tournament results

        Returns:
            Dictionary of matchup consistency metrics
        """
        if not tournament_group:
            return {"error": "No tournaments provided"}

        # Track matchup outcomes across tournaments
        matchups = defaultdict(list)

        for tournament in tournament_group:
            for match in tournament.get("matches", []):
                contender1_id = match.get("contender1_id")
                contender2_id = match.get("contender2_id")

                # Skip if we don't have both contenders
                if not contender1_id or not contender2_id:
                    continue

                # Create a unique key for this matchup (alphabetically sorted)
                matchup_key = tuple(sorted([contender1_id, contender2_id]))

                # Get the result - handle None case
                result = match.get("result")
                if result is None:
                    # Skip matches with no results
                    continue

                # Check if winner exists and handle both dictionary and direct access
                if isinstance(result, dict):
                    winner = result.get("winner")
                else:
                    # Try attribute access for non-dict objects (like Pydantic models)
                    try:
                        winner = getattr(result, "winner", None)
                    except Exception:
                        # Skip if we can't get the winner
                        continue

                # Record the outcome (1 if first contender won, -1 if second contender won, 0 for tie)
                if winner == contender1_id:
                    if matchup_key[0] == contender1_id:
                        outcome = 1
                    else:
                        outcome = -1
                elif winner == contender2_id:
                    if matchup_key[0] == contender2_id:
                        outcome = 1
                    else:
                        outcome = -1
                else:
                    outcome = 0

                matchups[matchup_key].append(outcome)

        # Calculate consistency for each matchup
        matchup_metrics = {}
        for matchup_key, outcomes in matchups.items():
            if len(outcomes) >= 2:  # Need at least 2 matches
                # Calculate frequency of each outcome
                counts = {
                    1: outcomes.count(1),  # First contender wins
                    -1: outcomes.count(-1),  # Second contender wins
                    0: outcomes.count(0),  # Tie
                }

                # Calculate the dominant outcome and its frequency
                dominant_outcome = max(counts, key=counts.get)
                dominant_freq = counts[dominant_outcome] / len(outcomes)

                # Calculate consistency metrics
                matchup_metrics[f"{matchup_key[0]} vs {matchup_key[1]}"] = {
                    "outcomes": outcomes,
                    "matches": len(outcomes),
                    "dominant_outcome": (
                        "first_win"
                        if dominant_outcome == 1
                        else "second_win" if dominant_outcome == -1 else "tie"
                    ),
                    "dominant_frequency": dominant_freq,
                    "consistency_score": dominant_freq,
                    "outcome_counts": counts,
                }

        # Calculate overall matchup consistency
        overall = {
            "avg_consistency": (
                statistics.mean(
                    [m["consistency_score"] for m in matchup_metrics.values()]
                )
                if matchup_metrics
                else 0
            ),
            "matchup_count": len(matchup_metrics),
            "tournament_count": len(tournament_group),
        }

        return {"overall": overall, "matchups": matchup_metrics}

    def calculate_score_consistency(
        self, tournament_group: List[Dict]
    ) -> Dict[str, Any]:
        """
        Calculate score consistency across tournaments.

        Args:
            tournament_group: List of tournament results

        Returns:
            Dictionary of score consistency metrics
        """
        if not tournament_group:
            return {"error": "No tournaments provided"}

        # Extract average scores from each tournament
        scores_by_tournament = []
        for tournament in tournament_group:
            scores = {}
            try:
                for ranking in tournament.get("rankings", []):
                    contender_id = ranking.get("contender_id")
                    if not contender_id:
                        continue

                    stats = ranking.get("stats", {})

                    # Handle different possible structures for stats
                    score = None
                    if isinstance(stats, dict):
                        if "average_score" in stats:
                            score = stats["average_score"]
                        elif (
                            "total_score" in stats
                            and stats.get("matches_played", 0) > 0
                        ):
                            score = stats["total_score"] / stats["matches_played"]
                    else:
                        # Try to access attributes if stats is not a dict
                        try:
                            if hasattr(stats, "average_score"):
                                score = stats.average_score
                            elif (
                                hasattr(stats, "total_score")
                                and getattr(stats, "matches_played", 0) > 0
                            ):
                                score = stats.total_score / stats.matches_played
                        except Exception:
                            pass

                    if score is not None:
                        scores[contender_id] = score

                # Only add if we have at least one valid score
                if scores:
                    scores_by_tournament.append(scores)
                else:
                    print(f"Warning: Tournament has no valid scores")
            except Exception as e:
                print(f"Error extracting scores from tournament: {e}")

        # Skip further processing if we don't have enough data
        if len(scores_by_tournament) < 2:
            return {
                "overall": {
                    "error": f"Need at least 2 tournaments with scores, found {len(scores_by_tournament)}",
                    "avg_stdev": 0,
                    "avg_coefficient_of_variation": 0,
                    "contender_count": 0,
                    "tournament_count": len(scores_by_tournament),
                },
                "contenders": {},
            }

        # Calculate consistency metrics for each contender
        contender_metrics = {}
        for contender_id in self.contenders:
            scores = [
                scores.get(contender_id, 0)
                for scores in scores_by_tournament
                if contender_id in scores
            ]
            if len(scores) >= 2:  # Need at least 2 tournaments for statistics
                mean_score = statistics.mean(scores)
                contender_metrics[contender_id] = {
                    "scores": scores,
                    "mean_score": mean_score,
                    "median_score": statistics.median(scores),
                    "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0,
                    "min_score": min(scores),
                    "max_score": max(scores),
                    "range": max(scores) - min(scores),
                    "coefficient_of_variation": (
                        statistics.stdev(scores) / mean_score
                        if mean_score > 0 and len(scores) > 1
                        else 0
                    ),
                    "tournaments": len(scores),
                }

        # Calculate overall score consistency
        cv_values = [
            m["coefficient_of_variation"]
            for m in contender_metrics.values()
            if not math.isnan(m["coefficient_of_variation"])
            and m["coefficient_of_variation"] != 0
        ]

        overall = {
            "avg_stdev": (
                statistics.mean([m["std_dev"] for m in contender_metrics.values()])
                if contender_metrics
                else 0
            ),
            "avg_coefficient_of_variation": (
                statistics.mean(cv_values) if cv_values else 0
            ),
            "contender_count": len(contender_metrics),
            "tournament_count": len(tournament_group),
        }

        return {"overall": overall, "contenders": contender_metrics}

    def analyze_all_metrics(
        self, grouped_tournaments: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """
        Calculate all consistency metrics for each tournament group.

        Args:
            grouped_tournaments: Dictionary of tournament groups

        Returns:
            Dictionary of all consistency metrics by group
        """
        results = {}

        for group_name, tournaments in grouped_tournaments.items():
            print(
                f"Analyzing {len(tournaments)} tournaments in group '{group_name}'..."
            )

            try:
                # Calculate each metric with error handling
                try:
                    ranking_consistency = self.calculate_ranking_consistency(
                        tournaments
                    )
                except Exception as e:
                    print(f"Error calculating ranking consistency: {e}")
                    ranking_consistency = {"error": str(e)}

                try:
                    win_rate_consistency = self.calculate_win_rate_consistency(
                        tournaments
                    )
                except Exception as e:
                    print(f"Error calculating win rate consistency: {e}")
                    win_rate_consistency = {"error": str(e)}

                try:
                    matchup_consistency = self.calculate_matchup_consistency(
                        tournaments
                    )
                except Exception as e:
                    print(f"Error calculating matchup consistency: {e}")
                    matchup_consistency = {"error": str(e)}

                try:
                    score_consistency = self.calculate_score_consistency(tournaments)
                except Exception as e:
                    print(f"Error calculating score consistency: {e}")
                    score_consistency = {"error": str(e)}

                group_metrics = {
                    "tournaments": len(tournaments),
                    "ranking_consistency": ranking_consistency,
                    "win_rate_consistency": win_rate_consistency,
                    "matchup_consistency": matchup_consistency,
                    "score_consistency": score_consistency,
                }

                results[group_name] = group_metrics
            except Exception as e:
                print(f"Error analyzing group '{group_name}': {e}")
                results[group_name] = {"tournaments": len(tournaments), "error": str(e)}

        self.metrics = results
        return results

    def export_summary_to_csv(
        self, output_file: str = "consistency_summary.csv"
    ) -> str:
        """
        Export a summary of consistency metrics to a CSV file.

        Args:
            output_file: Path to output CSV file

        Returns:
            Path to the exported file
        """
        if not self.metrics:
            print("No metrics to export. Run analyze_all_metrics first.")
            return ""

        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(
                [
                    "Group",
                    "Tournaments",
                    "Ranking Stability",
                    "Avg Rank StdDev",
                    "Win Rate Consistency",
                    "Avg Win Rate CV",
                    "Matchup Consistency",
                    "Score Consistency",
                    "Avg Score CV",
                ]
            )

            # Write data for each group
            for group_name, metrics in self.metrics.items():
                writer.writerow(
                    [
                        group_name,
                        metrics.get("tournaments", 0),
                        metrics.get("ranking_consistency", {})
                        .get("overall", {})
                        .get("rank_stability", 0),
                        metrics.get("ranking_consistency", {})
                        .get("overall", {})
                        .get("avg_stdev", 0),
                        1
                        - metrics.get("win_rate_consistency", {})
                        .get("overall", {})
                        .get("avg_coefficient_of_variation", 0),
                        metrics.get("win_rate_consistency", {})
                        .get("overall", {})
                        .get("avg_coefficient_of_variation", 0),
                        metrics.get("matchup_consistency", {})
                        .get("overall", {})
                        .get("avg_consistency", 0),
                        1
                        - metrics.get("score_consistency", {})
                        .get("overall", {})
                        .get("avg_coefficient_of_variation", 0),
                        metrics.get("score_consistency", {})
                        .get("overall", {})
                        .get("avg_coefficient_of_variation", 0),
                    ]
                )

        print(f"Exported summary to {output_file}")
        return output_file

    def export_detailed_results(self, output_dir: str = "./analysis_results") -> str:
        """
        Export detailed consistency metrics to JSON files.

        Args:
            output_dir: Directory for output files

        Returns:
            Path to the output directory
        """
        if not self.metrics:
            print("No metrics to export. Run analyze_all_metrics first.")
            return ""

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Add timestamp to filename for uniqueness
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Export each group's metrics to a separate file
        for group_name, metrics in self.metrics.items():
            filename = f"consistency_{group_name.repace(":", "_")}_{timestamp}.json"
            file_path = os.path.join(output_dir, filename)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=2)

            print(f"Exported detailed metrics for group '{group_name}' to {file_path}")

        # Export a combined summary file
        summary = {"timestamp": timestamp, "groups": {}, "overall_comparison": {}}

        for group_name, metrics in self.metrics.items():
            summary["groups"][group_name] = {
                "tournaments": metrics.get("tournaments", 0),
                "ranking_stability": metrics.get("ranking_consistency", {})
                .get("overall", {})
                .get("rank_stability", 0),
                "win_rate_consistency": 1
                - metrics.get("win_rate_consistency", {})
                .get("overall", {})
                .get("avg_coefficient_of_variation", 0),
                "matchup_consistency": metrics.get("matchup_consistency", {})
                .get("overall", {})
                .get("avg_consistency", 0),
                "score_consistency": 1
                - metrics.get("score_consistency", {})
                .get("overall", {})
                .get("avg_coefficient_of_variation", 0),
            }

        # Calculate which group has the best consistency for each metric
        if len(self.metrics) > 1:
            best_ranking = max(
                summary["groups"].items(), key=lambda x: x[1]["ranking_stability"]
            )
            best_win_rate = max(
                summary["groups"].items(), key=lambda x: x[1]["win_rate_consistency"]
            )
            best_matchup = max(
                summary["groups"].items(), key=lambda x: x[1]["matchup_consistency"]
            )
            best_score = max(
                summary["groups"].items(), key=lambda x: x[1]["score_consistency"]
            )

            summary["overall_comparison"] = {
                "best_ranking_stability": {
                    "group": best_ranking[0],
                    "value": best_ranking[1]["ranking_stability"],
                },
                "best_win_rate_consistency": {
                    "group": best_win_rate[0],
                    "value": best_win_rate[1]["win_rate_consistency"],
                },
                "best_matchup_consistency": {
                    "group": best_matchup[0],
                    "value": best_matchup[1]["matchup_consistency"],
                },
                "best_score_consistency": {
                    "group": best_score[0],
                    "value": best_score[1]["score_consistency"],
                },
            }

        summary_file = os.path.join(output_dir, f"consistency_summary_{timestamp}.json")
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        print(f"Exported overall summary to {summary_file}")

        return output_dir
