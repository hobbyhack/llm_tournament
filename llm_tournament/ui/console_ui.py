"""
Console UI for the LLM Tournament application.
"""

import os
import time
import sys
import datetime
from typing import Dict, Any, List, Optional

from models.tournament import Tournament
from models.match import Match


class ConsoleUI:
    """
    Displays tournament progress in a console-based UI.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the console UI with configuration.
        
        Args:
            config: Configuration settings
        """
        self.config = config
        self.ui_config = config.get("ui", {})
        self.enabled = self.ui_config.get("enabled", True)
        self.update_frequency = self.ui_config.get("update_frequency", 1)
        self.display_detailed_matches = self.ui_config.get("display_detailed_matches", True)
        
        self.last_update_time = 0
        self.start_time = None
    
    def display_welcome(self, tournament: Tournament) -> None:
        """
        Display welcome message.
        
        Args:
            tournament: Tournament being run
        """
        if not self.enabled:
            return
        
        self.start_time = time.time()
        
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 70)
        print(f"LLM TOURNAMENT: {tournament.id}")
        print("=" * 70)
        print(f"Assessment Framework: {tournament.assessment_framework.id}")
        print(f"Contenders: {len(tournament.contenders)}")
        print(f"Total Matches: {len(tournament.matches)}")
        print("-" * 70)
        print("Starting tournament...")
        print("=" * 70)
        print()
        
        # Ensure output is displayed
        sys.stdout.flush()
    
    def display_match_result(self, match: Match) -> None:
        """
        Display a match result.
        
        Args:
            match: Match to display
        """
        if not self.enabled or not self.display_detailed_matches:
            return
        
        if not match.result:
            return
        
        winner, score1, score2 = match.get_winner()
        
        print("\n" + "-" * 70)
        print(f"MATCH RESULT: {match.id}")
        print(f"Contender 1: {match.contender1.id}")
        print(f"Contender 2: {match.contender2.id}")
        
        if winner:
            print(f"Winner: {winner.id}")
        else:
            print("Result: Draw")
        
        print(f"Scores: {score1:.1f} vs {score2:.1f}")
        
        # Display criteria scores
        print("\nScores by criteria:")
        for name, scores in match.result.criteria_scores.items():
            print(f"  {name}: {scores.contender1:.1f} vs {scores.contender2:.1f}")
        
        # Display rationale (truncated if long)
        rationale = match.result.rationale
        if len(rationale) > 100:
            rationale = rationale[:100] + "..."
        print(f"\nRationale: {rationale}")
        print("-" * 70)
        
        # Ensure output is displayed
        sys.stdout.flush()
    
    def display_standings(self, standings: List[Dict[str, Any]]) -> None:
        """
        Display current standings.
        
        Args:
            standings: List of contender standings
        """
        if not self.enabled:
            return
        
        print("\n" + "=" * 70)
        print("TOURNAMENT STANDINGS")
        print("-" * 70)
        
        if not standings:
            print("No standings available yet.")
            print("=" * 70)
            return
        
        # Display table header
        print(f"{'Rank':<5} {'Contender':<20} {'Wins':<5} {'Losses':<7} {'Draws':<7} {'Points':<7} {'Win Rate':<8}")
        print("-" * 70)
        
        # Display each contender
        for contender in standings:
            # Truncate long contender names
            display_name = contender["content"]
            if len(display_name) > 17:
                display_name = display_name[:14] + "..."
            
            # Calculate win rate
            win_rate = 0
            if contender["stats"]["matches_played"] > 0:
                win_rate = contender["stats"]["wins"] / contender["stats"]["matches_played"] * 100
            
            print(
                f"{contender['rank']:<5} "
                f"{display_name:<20} "
                f"{contender['stats'].get('wins', 0):<5} "
                f"{contender['stats'].get('losses', 0):<7} "
                f"{contender['stats'].get('draws', 0):<7} "
                f"{contender['stats'].get('points', 0):<7} "
                f"{win_rate:.1f}%"
            )
        
        print("=" * 70)
        
        # Ensure output is displayed
        sys.stdout.flush()
    
    def display_progress(self, tournament: Tournament) -> None:
        """
        Display tournament progress.
        
        Args:
            tournament: Tournament to display progress for
        """
        if not self.enabled:
            return
        
        status = tournament.get_status()
        
        total_matches = status["total_matches"]
        completed = status["completed_matches"]
        remaining = status["remaining_matches"]
        progress = status["progress_percentage"]
        
        # Calculate elapsed time and estimated remaining time
        elapsed_seconds = time.time() - self.start_time if self.start_time else 0
        elapsed = str(datetime.timedelta(seconds=int(elapsed_seconds)))
        
        est_remaining_seconds = 0
        if completed > 0 and remaining > 0:
            seconds_per_match = elapsed_seconds / completed
            est_remaining_seconds = seconds_per_match * remaining
        est_remaining = str(datetime.timedelta(seconds=int(est_remaining_seconds)))
        
        # Create progress bar
        bar_length = 30
        filled_length = int(bar_length * progress / 100)
        bar = '#' * filled_length + '-' * (bar_length - filled_length)
        
        print(f"\rProgress: [{bar}] {progress:.1f}% ({completed}/{total_matches}) | "
              f"Time: {elapsed} | Est. Remaining: {est_remaining}", end='')
        
        # Ensure output is displayed
        sys.stdout.flush()
    
    def update_display(self, tournament: Tournament) -> None:
        """
        Update the display with current tournament status.
        
        Args:
            tournament: Tournament to display
        """
        if not self.enabled:
            return
        
        # Limit update frequency
        current_time = time.time()
        if current_time - self.last_update_time < self.update_frequency:
            return
        
        self.last_update_time = current_time
        
        # Display progress
        self.display_progress(tournament)
    
    def display_completion(self, tournament: Tournament, results_file: Optional[str] = None) -> None:
        """
        Display tournament completion message.
        
        Args:
            tournament: Completed tournament
            results_file: Optional path to results file
        """
        if not self.enabled:
            return
        
        print("\n\n" + "=" * 70)
        print("TOURNAMENT COMPLETED")
        print("-" * 70)
        
        # Display time information
        elapsed_seconds = time.time() - self.start_time if self.start_time else 0
        elapsed = str(datetime.timedelta(seconds=int(elapsed_seconds)))
        print(f"Total time: {elapsed}")
        
        # Display match statistics
        status = tournament.get_status()
        print(f"Total matches: {status['total_matches']}")
        print(f"Successful matches: {status['completed_matches']}")
        
        # Display results file location
        if results_file:
            print(f"Results exported to: {results_file}")
        
        print("=" * 70)
        
        # Display final standings
        self.display_standings(tournament.get_standings())
        
        # Ensure output is displayed
        sys.stdout.flush()
