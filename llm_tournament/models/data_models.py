"""
Pydantic data models for the LLM Tournament application.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class ContenderModel(BaseModel):
    """Model representing a tournament contender."""
    id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    stats: Dict[str, Any] = Field(
        default_factory=lambda: {"wins": 0, "losses": 0, "draws": 0, "points": 0}
    )


class CriterionModel(BaseModel):
    """Model representing an evaluation criterion."""
    name: str
    description: str
    weight: float


class ScoringSystemModel(BaseModel):
    """Model representing the scoring system for the tournament."""
    type: str  # "points", "comparison", etc.
    scale: Dict[str, int] = Field(default_factory=lambda: {"min": 0, "max": 10})
    categories: List[Dict[str, Any]] = Field(default_factory=list)


class AssessmentFrameworkModel(BaseModel):
    """Model representing the assessment framework."""
    id: str
    description: str
    evaluation_criteria: List[CriterionModel]
    comparison_rules: List[str]
    scoring_system: ScoringSystemModel


class CriteriaScoreModel(BaseModel):
    """Model representing scores for a specific criterion."""
    contender1: float
    contender2: float


class MatchResultModel(BaseModel):
    """Model representing the result of a match."""
    winner: Optional[str] = None
    contender1_score: float
    contender2_score: float
    rationale: str
    criteria_scores: Dict[str, CriteriaScoreModel]


class MatchModel(BaseModel):
    """Model representing a match between two contenders."""
    id: str
    contender1_id: str
    contender2_id: str
    result: Optional[MatchResultModel] = None
    timestamp: Optional[datetime] = None
    retries: int = 0


class TournamentStatsModel(BaseModel):
    """Model representing tournament statistics."""
    total_contenders: int
    total_matches: int
    completed_matches: int
    remaining_matches: int
    progress_percentage: float = 0.0


class ContenderRankingModel(BaseModel):
    """Model representing a contender's ranking in the tournament."""
    rank: int
    contender_id: str
    content: str
    stats: Dict[str, Any]


class TournamentResultsModel(BaseModel):
    """Model representing the results of a tournament."""
    id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str  # "in_progress", "completed", "error"
    assessment_framework_id: str
    config: Dict[str, Any]
    statistics: TournamentStatsModel
    rankings: List[ContenderRankingModel] = Field(default_factory=list)
    matches: List[MatchModel] = Field(default_factory=list)
