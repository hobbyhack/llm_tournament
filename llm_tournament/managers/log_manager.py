"""
Logging manager for the LLM Tournament application.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, Optional

from models.tournament import Tournament
from models.match import Match


class LogManager:
    """
    Manages logging throughout the application.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the logging manager with configuration.
        
        Args:
            config: Configuration settings
        """
        self.config = config
        self.logger = None
        
        # Configure logging
        self.configure(config)
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure logging based on configuration.
        
        Args:
            config: Configuration settings
        """
        logging_config = config.get("logging", {})
        
        # Get log level
        level_name = logging_config.get("level", "INFO")
        level = getattr(logging, level_name.upper(), logging.INFO)
        
        # Get log file
        log_file = logging_config.get("file", "./logs/tournament.log")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("llm_tournament")
        self.logger.setLevel(level)
        
        # Clear existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_formatter = logging.Formatter(
            logging_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Create console handler if enabled
        if logging_config.get("console", True):
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter("%(levelname)s: %(message)s")
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
    
    def log_info(self, message: str) -> None:
        """
        Log an info message.
        
        Args:
            message: Message to log
        """
        if self.logger:
            self.logger.info(message)
    
    def log_warning(self, message: str) -> None:
        """
        Log a warning message.
        
        Args:
            message: Message to log
        """
        if self.logger:
            self.logger.warning(message)
    
    def log_error(self, message: str, exc_info: Optional[bool] = False) -> None:
        """
        Log an error message.
        
        Args:
            message: Message to log
            exc_info: Whether to include exception info
        """
        if self.logger:
            self.logger.error(message, exc_info=exc_info)
    
    def log_match_result(self, match: Match) -> None:
        """
        Log a match result.
        
        Args:
            match: Match to log
        """
        if not self.logger or not match.result:
            return
        
        winner, score1, score2 = match.get_winner()
        
        if winner:
            self.logger.info(
                f"Match {match.id}: {match.contender1.id} vs {match.contender2.id} - "
                f"Winner: {winner.id} ({score1:.1f} vs {score2:.1f})"
            )
        else:
            self.logger.info(
                f"Match {match.id}: {match.contender1.id} vs {match.contender2.id} - "
                f"Draw ({score1:.1f} vs {score2:.1f})"
            )
    
    def log_tournament_status(self, tournament: Tournament) -> None:
        """
        Log tournament status.
        
        Args:
            tournament: Tournament to log
        """
        if not self.logger:
            return
        
        status = tournament.get_status()
        
        self.logger.info(
            f"Tournament {tournament.id} status: "
            f"{status['completed_matches']}/{status['total_matches']} matches completed "
            f"({status['progress_percentage']:.1f}%)"
        )
    
    def log_tournament_complete(self, tournament: Tournament) -> None:
        """
        Log tournament completion.
        
        Args:
            tournament: Tournament to log
        """
        if not self.logger:
            return
        
        self.logger.info(f"Tournament {tournament.id} completed")
        
        # Log top contenders
        standings = tournament.get_standings()
        for i, contender in enumerate(standings[:3], 1):
            self.logger.info(
                f"Rank {i}: {contender['id']} - "
                f"Wins: {contender['stats']['wins']}, "
                f"Points: {contender['stats']['points']}"
            )
