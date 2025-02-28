"""
Match class for the LLM Tournament application.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

from models.data_models import MatchModel, MatchResultModel, CriteriaScoreModel
from models.contender import Contender
from models.assessment import AssessmentFramework


class Match:
    """
    Represents a match between two contenders.
    Manages match evaluation and results.
    """
    
    def __init__(
        self, 
        contender1: Contender, 
        contender2: Contender, 
        assessment_framework: AssessmentFramework,
        match_id: Optional[str] = None
    ):
        """
        Initialize a match between two contenders.
        
        Args:
            contender1: First contender
            contender2: Second contender
            assessment_framework: Framework for evaluating the match
            match_id: Optional match ID (generated if not provided)
        """
        self.contender1 = contender1
        self.contender2 = contender2
        self.assessment_framework = assessment_framework
        self.id = match_id or f"match_{uuid.uuid4().hex[:8]}"
        self.result = None
        self.timestamp = None
        self.retries = 0
    
    def evaluate(self, llm_manager) -> bool:
        """
        Evaluate the match using the LLM manager.
        
        Args:
            llm_manager: LLM manager for making evaluation requests
            
        Returns:
            True if evaluation was successful, False otherwise
        """
        try:
            # Increment retry counter
            self.retries += 1
            
            # Send to LLM for evaluation
            result = llm_manager.evaluate_match(self)
            
            # Set timestamp for when the match was evaluated
            self.timestamp = datetime.now()
            
            # Store the result
            self.result = result
            
            return True
        except Exception as e:
            # Log the error (when we have logging)
            print(f"Error evaluating match {self.id}: {e}")
            return False
    
    def retry_evaluation(self, llm_manager, max_retries: int) -> bool:
        """
        Retry evaluation up to max_retries times.
        
        Args:
            llm_manager: LLM manager for making evaluation requests
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if evaluation was eventually successful, False otherwise
        """
        # If already at or beyond max retries, fail immediately
        if self.retries >= max_retries:
            return False
        
        # Try evaluating until success or max retries
        while self.retries < max_retries:
            if self.evaluate(llm_manager):
                return True
        
        return False
    
    def get_result(self) -> Optional[Dict[str, Any]]:
        """
        Get the match result if available.
        
        Returns:
            Dictionary containing match result data, or None if not evaluated
        """
        if not self.result:
            return None
        
        # Create a result dictionary that is easy to work with
        return {
            "id": self.id,
            "contender1_id": self.contender1.id,
            "contender2_id": self.contender2.id,
            "result": self.result,  # This is a MatchResultModel
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
    
    def get_winner(self) -> Tuple[Optional[Contender], Optional[float], Optional[float]]:
        """
        Get the winning contender and scores if the match has been evaluated.
        
        Returns:
            Tuple of (winning_contender, score1, score2) or (None, None, None) if not evaluated
        """
        if not self.result:
            return None, None, None
        
        if self.result.winner == self.contender1.id:
            return self.contender1, self.result.contender1_score, self.result.contender2_score
        elif self.result.winner == self.contender2.id:
            return self.contender2, self.result.contender1_score, self.result.contender2_score
        else:
            # Draw
            return None, self.result.contender1_score, self.result.contender2_score
    
    def to_model(self) -> MatchModel:
        """
        Convert to a Pydantic model for serialization.
        
        Returns:
            MatchModel instance
        """
        return MatchModel(
            id=self.id,
            contender1_id=self.contender1.id,
            contender2_id=self.contender2.id,
            result=self.result,
            timestamp=self.timestamp,
            retries=self.retries
        )
    
    @classmethod
    def from_model(
        cls, 
        model: MatchModel, 
        contenders: Dict[str, Contender], 
        assessment_framework: AssessmentFramework
    ) -> 'Match':
        """
        Create a Match instance from a Pydantic model.
        
        Args:
            model: MatchModel instance
            contenders: Dictionary mapping contender IDs to Contender instances
            assessment_framework: Assessment framework to use
            
        Returns:
            Match instance
        """
        # Get contenders by ID
        contender1 = contenders.get(model.contender1_id)
        contender2 = contenders.get(model.contender2_id)
        
        if not contender1 or not contender2:
            raise ValueError(f"Contender not found: {model.contender1_id if not contender1 else model.contender2_id}")
        
        # Create match
        match = cls(
            contender1=contender1,
            contender2=contender2,
            assessment_framework=assessment_framework,
            match_id=model.id
        )
        
        # Restore result if present
        if model.result:
            criteria_scores = {}
            for name, scores in model.result.criteria_scores.items():
                criteria_scores[name] = CriteriaScoreModel(
                    contender1=scores.contender1,
                    contender2=scores.contender2
                )
            
            match.result = MatchResultModel(
                winner=model.result.winner,
                contender1_score=model.result.contender1_score,
                contender2_score=model.result.contender2_score,
                rationale=model.result.rationale,
                criteria_scores=criteria_scores
            )
        
        match.timestamp = model.timestamp
        match.retries = model.retries
        
        return match