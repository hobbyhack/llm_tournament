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
        
        # Extract my score from the result
        if result["contender1_id"] == self.id:
            my_score = result["result"]["contender1_score"]
            opponent_score = result["result"]["contender2_score"]
        else:
            my_score = result["result"]["contender2_score"]
            opponent_score = result["result"]["contender1_score"]
        
        # Update total score
        self.stats["total_score"] += my_score
        
        # Update win/loss/draw record
        if result["result"]["winner"] == self.id:
            self.stats["wins"] += 1
            self.stats["points"] += point_system.get("win", 3)
        elif result["result"]["winner"] is None:
            self.stats["draws"] += 1
            self.stats["points"] += point_system.get("draw", 1)
        else:
            self.stats["losses"] += 1
            self.stats["points"] += point_system.get("loss", 0)
    
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
