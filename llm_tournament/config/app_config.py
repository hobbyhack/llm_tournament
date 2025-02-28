"""
Application configuration management.
"""

import os
import yaml
from typing import Any, Dict, Optional


class AppConfig:
    """
    Centralized configuration management for the LLM Tournament application.
    Handles loading from YAML files and environment variables.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration with optional path to config file."""
        self.config = {
            "tournament": {
                "rounds_per_matchup": 1,
                "reverse_matchups": True,
                "point_system": {"win": 3, "draw": 1, "loss": 0},
            },
            "llm": {
                "provider": "ollama",
                "default_model": "phi4",
                "timeout": 60,
                "max_retries": 3,
                "retry_delay": 5,
                "model_mapping": {
                    "match_evaluation": "phi4",
                    "contender_comparison": "phi4",
                    "scoring": "phi4",
                    "validation": "phi4",
                },
            },
            "prompts": {"directory": "./prompts", "format": "markdown"},
            "ui": {
                "enabled": True,
                "update_frequency": 1,
                "display_detailed_matches": True,
            },
            "output": {
                "results_file": "./results/tournament_results.json",
                "match_log_dir": "./results/matches",
            },
            "logging": {
                "level": "INFO",
                "file": "./logs/tournament.log",
                "console": True,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        }

        if config_path:
            self.load_from_file(config_path)

        self.load_from_env()

    def load_from_file(self, file_path: str) -> None:
        """Load configuration from a YAML file."""
        try:
            with open(file_path, "r") as f:
                file_config = yaml.safe_load(f)
                self._merge_configs(self.config, file_config)
        except Exception as e:
            # Log this error once we have logging set up
            print(f"Error loading config from {file_path}: {e}")

    def load_from_env(self) -> None:
        """Override configuration with environment variables."""
        # Example: LLM_TOURNAMENT_LLM_DEFAULT_MODEL=llamav2 would override config["llm"]["default_model"]
        prefix = "LLM_TOURNAMENT_"

        for key in os.environ:
            if key.startswith(prefix):
                # Remove prefix and split into config path
                config_path = key[len(prefix) :].lower().split("_")

                # Navigate to the correct position in the config
                current = self.config
                for part in config_path[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

                # Set the value
                current[config_path[-1]] = self._convert_value(os.environ[key])

    def get_setting(self, *keys: str, default: Any = None) -> Any:
        """
        Get a setting from the configuration.

        Args:
            *keys: The path to the setting (e.g., "llm", "default_model").
            default: Default value if setting not found.

        Returns:
            The setting value or default if not found.
        """
        current = self.config
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current

    def validate_config(self) -> bool:
        """
        Validate that all required settings are present.

        Returns:
            True if valid, False otherwise.
        """
        # Check required top-level keys
        required_keys = ["tournament", "llm", "prompts", "output", "logging"]
        for key in required_keys:
            if key not in self.config:
                print(f"Missing required configuration section: {key}")
                return False

        # Check specific required settings
        if not self.get_setting("llm", "default_model"):
            print("Missing required setting: llm.default_model")
            return False

        if not self.get_setting("prompts", "directory"):
            print("Missing required setting: prompts.directory")
            return False

        return True

    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursively merge override config into base config."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value

    def _convert_value(self, value: str) -> Any:
        """Convert string values from environment variables to appropriate types."""
        # Try to convert to bool
        if value.lower() in ("true", "yes", "1"):
            return True
        if value.lower() in ("false", "no", "0"):
            return False

        # Try to convert to int
        try:
            return int(value)
        except ValueError:
            pass

        # Try to convert to float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value
