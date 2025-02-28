"""
Tournament class for the LLM Tournament application.
"""

import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import itertools

from models.data_models import TournamentResultsModel, TournamentStatsModel, ContenderRankingModel
from models.contender import Contender
from models.match import Match
from models.assessment import AssessmentFramework


class Tournament:
    """
    Manages the tournament lifecycle including planning matches,
    executing the tournament, and calculating results.
    """
    
    def __init__(
        self, 
        contenders: List[Contender], 
        assessment_framework: AssessmentFramework,
        config: Dict[str, Any],
        tournament_id: Optional[str] = None
    ):
        """
        Initialize a tournament with contenders and assessment framework.
        
        Args:
            contenders: List of contenders participating in the tournament
            assessment_framework: Framework for evaluating matches
            config: Tournament configuration
            tournament_id: Optional tournament ID (generated if not provided)
        """
        self.contenders = {contender.id: contender for contender in contenders}
        self.assessment_framework = assessment_framework
        self.config = config
        self.id = tournament_id or f"tournament_{uuid.uuid4().hex[:8]}"
        
        self.start_time = None
        self.end_time = None
        self.status = "initialized"
        
        self.matches = []
        self.current_match_index = 0
        
        # Tournament settings
        self.rounds_per_matchup = config.get("tournament", {}).get("rounds_per_matchup", 1)
        self.reverse_matchups = config.get("tournament", {}).get("reverse_matchups", True)
        self.point_system = config.get("tournament", {}).get("point_system", {
            "win": 3,
            "draw": 1,
            "loss": 0
        })
        
        # Timeouts and retries
        self.max_retries = config.get("llm", {}).get("max_retries", 3)
        self.retry_delay = config.get("llm", {}).get("retry_delay", 5)
    
    def plan_matches(self) -> List[Match]:
        """
        Create round-robin tournament schedule.
        
        Returns:
            List of Match objects for the tournament
        """
        # Clear existing matches
        self.matches = []
        
        # Get all unique pairs of contenders
        contender_ids = list(self.contenders.keys())
        pairs = list(itertools.combinations(contender_ids, 2))
        
        # Create matches for each pair
        for round_num in range(self.rounds_per_matchup):
            for contender1_id, contender2_id in pairs:
                contender1 = self.contenders[contender1_id]
                contender2 = self.contenders[contender2_id]
                
                # Create match with contender1 vs contender2
                match = Match(
                    contender1=contender1,
                    contender2=contender2,
                    assessment_framework=self.assessment_framework
                )
                self.matches.append(match)
                
                # If needed, create reverse match with contender2 vs contender1
                if self.reverse_matchups:
                    reverse_match = Match(
                        contender1=contender2,
                        contender2=contender1,
                        assessment_framework=self.assessment_framework
                    )
                    self.matches.append(reverse_match)
        
        return self.matches
    
    def run_tournament(self, llm_manager, ui_manager=None, headless: bool = False) -> bool:
        """
        Execute all matches in the tournament.
        
        Args:
            llm_manager: LLM manager for evaluating matches
            ui_manager: Optional UI manager for displaying progress
            headless: Whether to run without UI updates
            
        Returns:
            True if tournament completed successfully, False otherwise
        """
        if not self.matches:
            self.plan_matches()
        
        self.start_time = datetime.now()
        self.status = "in_progress"
        
        # Run matches
        for i, match in enumerate(self.matches):
            self.current_match_index = i
            
            # Update UI if available
            if ui_manager and not headless:
                ui_manager.update_display(self)
            
            # Run the match
            success = match.evaluate(llm_manager)
            
            # If failed, retry
            if not success:
                for _ in range(self.max_retries - 1):  # Already tried once
                    time.sleep(self.retry_delay)
                    success = match.evaluate(llm_manager)
                    if success:
                        break
            
            # Update contender stats if successful
            if success and match.result:
                result = match.get_result()
                
                # Update contender statistics
                contender1 = self.contenders[result["contender1_id"]]
                contender2 = self.contenders[result["contender2_id"]]
                
                contender1.update_stats(result, self.point_system)
                contender2.update_stats(result, self.point_system)
            
            # Update UI after match
            if ui_manager and not headless:
                ui_manager.display_match_result(match)
                ui_manager.update_display(self)
        
        self.end_time = datetime.now()
        self.status = "completed"
        
        # Final UI update
        if ui_manager and not headless:
            ui_manager.display_standings(self.get_standings())
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current tournament status.
        
        Returns:
            Dictionary with tournament status information
        """
        total_matches = len(self.matches)
        completed_matches = sum(1 for match in self.matches if match.result is not None)
        
        progress = 0.0
        if total_matches > 0:
            progress = completed_matches / total_matches * 100
        
        return {
            "id": self.id,
            "status": self.status,
            "total_contenders": len(self.contenders),
            "total_matches": total_matches,
            "completed_matches": completed_matches,
            "remaining_matches": total_matches - completed_matches,
            "progress_percentage": progress,
            "current_match_index": self.current_match_index
        }
    
    def get_standings(self) -> List[Dict[str, Any]]:
        """
        Calculate current contender rankings.
        
        Returns:
            List of contenders sorted by points and other metrics
        """
        # Get all contenders with their stats
        contender_stats = []
        for contender in self.contenders.values():
            stats = contender.get_stats()
            contender_stats.append({
                "id": contender.id,
                "content": contender.content,
                "stats": stats
            })
        
        # Sort by points (primary), wins (secondary), and average score (tertiary)
        sorted_contenders = sorted(
            contender_stats,
            key=lambda x: (
                x["stats"]["points"], 
                x["stats"]["wins"], 
                x["stats"].get("average_score", 0)
            ),
            reverse=True
        )
        
        # Add rank
        for i, contender in enumerate(sorted_contenders, 1):
            contender["rank"] = i
        
        return sorted_contenders
    
    def export_results(self) -> TournamentResultsModel:
        """
        Generate tournament results for export.
        
        Returns:
            TournamentResultsModel instance
        """
        # Get tournament status
        status = self.get_status()
        
        # Create stats model
        stats_model = TournamentStatsModel(
            total_contenders=status["total_contenders"],
            total_matches=status["total_matches"],
            completed_matches=status["completed_matches"],
            remaining_matches=status["remaining_matches"],
            progress_percentage=status["progress_percentage"]
        )
        
        # Create rankings models
        rankings = []
        for contender in self.get_standings():
            rankings.append(ContenderRankingModel(
                rank=contender["rank"],
                contender_id=contender["id"],
                content=contender["content"],
                stats=contender["stats"]
            ))
        
        # Create match models
        match_models = [match.to_model() for match in self.matches]
        
        # Create tournament results model
        return TournamentResultsModel(
            id=self.id,
            start_time=self.start_time or datetime.now(),
            end_time=self.end_time,
            status=self.status,
            assessment_framework_id=self.assessment_framework.id,
            config=self.config,
            statistics=stats_model,
            rankings=rankings,
            matches=match_models
        )
