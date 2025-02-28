"""
Contender class for the LLM Tournament application.
"""

from typing import Dict, Any, Optional
from models.data_models import ContenderModel


class Contender:
    """
    Represents a contender in the tournament.
    Manages contender data and statistics.
    """
    
    def __init__(self, id: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a contender with its content and optional metadata.
        
        Args:
            id: Unique identifier for the contender
            content: The actual text content of the contender
            metadata: Optional metadata about the contender
        """
        self.id = id
        self.content = content
        self.metadata = metadata or {}
        
        # Initialize statistics
        self.stats = {
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "points": 0,
            "total_score": 0,
            "matches_played": 0
        }
    
    def update_stats(self, result: Dict[str, Any], point_system: Dict[str, int]) -> None:
        """
        Update contender statistics based on a match result.
        
        Args:
            result: Match result containing winner and scores
            point_system: Dictionary mapping outcome to points (win/draw/loss)
        """
        self.stats["matches_played"] += 1
        
        try:
            # Verify we have the necessary data
            if not isinstance(result, dict) or "contender1_id" not in result or "contender2_id" not in result:
                print(f"Warning: Invalid result format in update_stats: {type(result)}")
                return
                
            result_obj = result.get("result", {})
            if not result_obj:
                print(f"Warning: Empty result object in update_stats")
                return
                
            # Extract scores and winner based on which contender we are
            if result["contender1_id"] == self.id:
                # We're contender1
                my_score = float(result_obj.get("contender1_score", 5.0))
                opponent_score = float(result_obj.get("contender2_score", 5.0))
            else:
                # We're contender2
                my_score = float(result_obj.get("contender2_score", 5.0))
                opponent_score = float(result_obj.get("contender1_score", 5.0))
                
            winner_id = result_obj.get("winner")
                
            # Update total score
            self.stats["total_score"] += my_score
            
            # Update win/loss/draw record
            if winner_id == self.id:
                self.stats["wins"] += 1
                self.stats["points"] += point_system.get("win", 3)
            elif winner_id is None:
                self.stats["draws"] += 1
                self.stats["points"] += point_system.get("draw", 1)
            else:
                self.stats["losses"] += 1
                self.stats["points"] += point_system.get("loss", 0)
                
            print(f"Updated stats for {self.id}: W-{self.stats['wins']} L-{self.stats['losses']} D-{self.stats.get('draws', 0)} Pts-{self.stats['points']}")
        
        except Exception as e:
            print(f"Error updating stats for contender {self.id}: {e}")
            # Don't increment stats in case of error to avoid inconsistencies
            
    def get_stats(self) -> Dict[str, Any]:
        """
        Get the current statistics for this contender.
        
        Returns:
            Dictionary of contender statistics
        """
        # Calculate derived statistics
        if self.stats["matches_played"] > 0:
            win_percentage = self.stats["wins"] / self.stats["matches_played"]
            avg_score = self.stats["total_score"] / self.stats["matches_played"]
        else:
            win_percentage = 0.0
            avg_score = 0.0
        
        return {
            **self.stats,
            "win_percentage": win_percentage,
            "average_score": avg_score
        }
    
    def to_model(self) -> ContenderModel:
        """
        Convert to a Pydantic model for serialization.
        
        Returns:
            ContenderModel instance
        """
        return ContenderModel(
            id=self.id,
            content=self.content,
            metadata=self.metadata,
            stats=self.get_stats()
        )
    
    @classmethod
    def from_model(cls, model: ContenderModel) -> 'Contender':
        """
        Create a Contender instance from a Pydantic model.
        
        Args:
            model: ContenderModel instance
            
        Returns:
            Contender instance
        """
        contender = cls(
            id=model.id,
            content=model.content,
            metadata=model.metadata
        )
        
        # Restore stats if present
        if hasattr(model, 'stats') and model.stats:
            contender.stats.update(model.stats)
        
        return contender