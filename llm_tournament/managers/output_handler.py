"""
Output handler for the LLM Tournament application.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from models.tournament import Tournament
from models.match import Match
from models.data_models import TournamentResultsModel


class OutputHandler:
    """
    Handles formatting and exporting results.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the output handler with configuration.

        Args:
            config: Configuration settings
        """
        self.config = config
        self.results_file = config.get("output", {}).get(
            "results_file", "./results/tournament_results.json"
        )
        self.match_log_dir = config.get("output", {}).get(
            "match_log_dir", "./results/matches"
        )

        # Create directories if they don't exist
        os.makedirs(os.path.dirname(self.results_file), exist_ok=True)
        os.makedirs(self.match_log_dir, exist_ok=True)

    def export_tournament_results(
        self, tournament: Tournament, file_path: Optional[str] = None
    ) -> str:
        """
        Export tournament results to a JSON file.

        Args:
            tournament: Tournament to export
            file_path: Optional file path (defaults to config setting)

        Returns:
            Path to the exported file
        """
        output_path = file_path or self.results_file

        # Create the results model
        results_model = tournament.export_results()

        # Convert to JSON
        results_json = results_model.model_dump_json(indent=2)

        # Save to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(results_json)

        return output_path

    def export_match_result(self, match: Match, file_path: Optional[str] = None) -> str:
        """
        Export a single match result to a JSON file.

        Args:
            match: Match to export
            file_path: Optional file path (defaults to match_log_dir/match_id.json)

        Returns:
            Path to the exported file
        """
        if file_path is None:
            file_path = os.path.join(self.match_log_dir, f"{match.id}.json")

        # Get the match result
        result = match.get_result()

        if result:
            # Convert to JSON
            result_json = json.dumps(result, indent=2, default=str)

            # Save to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result_json)

        return file_path

    def format_standings(self, standings: List[Dict[str, Any]]) -> str:
        """
        Format standings for display/export.

        Args:
            standings: List of contender standings

        Returns:
            Formatted standings string
        """
        # Determine column widths
        rank_width = max(4, len(str(len(standings))))
        name_width = max(
            10,
            max(
                (
                    len(c["content"])
                    if len(c["content"]) <= 20
                    else len(c["content"][:17] + "...")
                )
                for c in standings
            ),
        )
        stat_width = 8

        # Format header
        header = f"+{'-' * (rank_width + 2)}+{'-' * (name_width + 2)}+{'-' * (stat_width + 2)}+"
        header += f"{'-' * (stat_width + 2)}+{'-' * (stat_width + 2)}+{'-' * (stat_width + 2)}+\n"
        header += f"| {'Rank'.ljust(rank_width)} | {'Contender'.ljust(name_width)} | "
        header += f"{'Wins'.ljust(stat_width)} | {'Losses'.ljust(stat_width)} | "
        header += f"{'Points'.ljust(stat_width)} | {'Win Rate'.ljust(stat_width)} |\n"
        header += f"+{'-' * (rank_width + 2)}+{'-' * (name_width + 2)}+{'-' * (stat_width + 2)}+"
        header += f"{'-' * (stat_width + 2)}+{'-' * (stat_width + 2)}+{'-' * (stat_width + 2)}+\n"

        # Format rows
        rows = ""
        for contender in standings:
            # Truncate long contender names
            display_name = contender["content"]
            if len(display_name) > 20:
                display_name = display_name[:17] + "..."

            # Calculate win rate
            win_rate = 0
            if contender["stats"]["matches_played"] > 0:
                win_rate = (
                    contender["stats"]["wins"]
                    / contender["stats"]["matches_played"]
                    * 100
                )

            # Format row
            row = f"| {str(contender['rank']).ljust(rank_width)} | {display_name.ljust(name_width)} | "
            row += f"{str(contender['stats']['wins']).ljust(stat_width)} | "
            row += f"{str(contender['stats']['losses']).ljust(stat_width)} | "
            row += f"{str(contender['stats']['points']).ljust(stat_width)} | "
            row += f"{f'{win_rate:.1f}%'.ljust(stat_width)} |\n"
            rows += row

        footer = f"+{'-' * (rank_width + 2)}+{'-' * (name_width + 2)}+{'-' * (stat_width + 2)}+"
        footer += f"{'-' * (stat_width + 2)}+{'-' * (stat_width + 2)}+{'-' * (stat_width + 2)}+"

        return header + rows + footer

    def format_match_result(self, match: Match) -> str:
        """
        Format a match result for display.

        Args:
            match: Match to format

        Returns:
            Formatted match result string
        """
        if not match.result:
            return f"Match {match.id}: No result available"

        winner, score1, score2 = match.get_winner()

        if winner:
            winner_str = f"Winner: {winner.id} ({score1:.1f} vs {score2:.1f})"
        else:
            winner_str = f"Draw: ({score1:.1f} vs {score2:.1f})"

        # Format criteria scores
        criteria_scores = []
        for name, scores in match.result.criteria_scores.items():
            criteria_scores.append(
                f"{name}: {scores.contender1:.1f} vs {scores.contender2:.1f}"
            )

        criteria_str = ", ".join(criteria_scores)

        return (
            f"Match {match.id}: {match.contender1.id} vs {match.contender2.id}\n"
            + f"{winner_str}\n"
            + f"Scores by criteria: {criteria_str}\n"
            + f"Rationale: {match.result.rationale[:100]}..."
            if len(match.result.rationale) > 100
            else match.result.rationale
        )
