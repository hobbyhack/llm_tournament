#!/usr/bin/env python
"""
LLM Tournament Application

A Python application for running a round-robin tournament between text contenders,
evaluated by an LLM against an assessment framework.
"""

import os
import sys
import argparse
import time
from typing import Dict, Any, List, Optional, Tuple

from config.app_config import AppConfig
from models.tournament import Tournament
from models.contender import Contender
from models.assessment import AssessmentFramework
from managers.llm_manager import LLMManager
from managers.prompt_manager import PromptManager
from managers.input_handler import InputHandler
from managers.output_handler import OutputHandler
from managers.log_manager import LogManager
from ui.console_ui import ConsoleUI
from utils.helpers import ensure_directory_exists


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="LLM Tournament Application")

    parser.add_argument(
        "--config", type=str, default="config.yaml", help="Path to configuration file"
    )

    parser.add_argument("--contenders", type=str, help="Path to contenders JSON file")

    parser.add_argument(
        "--framework", type=str, help="Path to assessment framework JSON file"
    )

    parser.add_argument(
        "--headless", action="store_true", help="Run without UI (headless mode)"
    )

    parser.add_argument("--output", type=str, help="Path to output results file")

    parser.add_argument("--rounds", type=int, help="Number of rounds per matchup")

    parser.add_argument("--model", type=str, help="LLM model to use")

    return parser.parse_args()


def setup_environment(config: AppConfig) -> None:
    """Set up the environment for the application."""
    # Create necessary directories
    directories = [
        config.get_setting("prompts", "directory", default="./prompts"),
        config.get_setting("output", "match_log_dir", default="./results/matches"),
        os.path.dirname(
            config.get_setting(
                "output", "results_file", default="./results/tournament_results.json"
            )
        ),
        os.path.dirname(
            config.get_setting("logging", "file", default="./logs/tournament.log")
        ),
    ]

    for directory in directories:
        ensure_directory_exists(directory)


def run_tournament(args: argparse.Namespace) -> int:
    """
    Run the tournament using the provided arguments.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Load configuration
    try:
        config = AppConfig(args.config)

        # Override config with command line arguments
        # Override config with command line arguments
        if args.rounds:
            config.config["tournament"]["rounds_per_matchup"] = args.rounds

        if args.model:
            # Update both the default model and all model mappings
            config.config["llm"]["default_model"] = args.model
            # Update all model mappings to use the specified model
            for prompt_type in config.config["llm"]["model_mapping"]:
                config.config["llm"]["model_mapping"][prompt_type] = args.model

        if args.output:
            config.config["output"]["results_file"] = args.output

        if args.headless:
            config.config["ui"]["enabled"] = False
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return 1

    # Set up the environment
    setup_environment(config)

    # Initialize managers
    log_manager = LogManager(config.config)
    log_manager.log_info("Starting LLM Tournament")

    prompt_manager = PromptManager(
        config.get_setting("prompts", "directory"), config.config
    )

    # Create default prompts if they don't exist
    prompt_manager.create_default_prompts()

    input_handler = InputHandler(config.config)
    output_handler = OutputHandler(config.config)

    # Load contenders and framework
    try:
        contenders_path = args.contenders or input("Enter path to contenders file: ")
        framework_path = args.framework or input("Enter path to framework file: ")

        contenders = input_handler.load_contenders(contenders_path)
        framework = input_handler.load_framework(framework_path)

        if not input_handler.validate_input(contenders, framework):
            log_manager.log_error("Invalid input data")
            return 1

        log_manager.log_info(
            f"Loaded {len(contenders)} contenders and assessment framework '{framework.id}'"
        )
    except Exception as e:
        log_manager.log_error(f"Error loading input data: {e}", exc_info=True)
        return 1

    # Initialize LLM manager
    try:
        llm_manager = LLMManager(config.config, prompt_manager)
    except Exception as e:
        log_manager.log_error(f"Error initializing LLM manager: {e}", exc_info=True)
        return 1

    # Initialize UI
    ui_manager = ConsoleUI(config.config)

    # Create tournament
    tournament = Tournament(
        contenders=contenders, assessment_framework=framework, config=config.config
    )

    # Plan matches
    tournament.plan_matches()

    # Display welcome message
    ui_manager.display_welcome(tournament)

    # Run tournament
    log_manager.log_info(f"Starting tournament with {len(tournament.matches)} matches")
    try:
        tournament.run_tournament(
            llm_manager=llm_manager, ui_manager=ui_manager, headless=args.headless
        )
        log_manager.log_info("Tournament completed successfully")
    except Exception as e:
        log_manager.log_error(f"Error running tournament: {e}", exc_info=True)
        return 1

    # Export results
    try:
        results_file = output_handler.export_tournament_results(tournament)
        log_manager.log_info(f"Tournament results exported to {results_file}")

        # Display completion message
        ui_manager.display_completion(tournament, results_file)
    except Exception as e:
        log_manager.log_error(f"Error exporting results: {e}", exc_info=True)
        return 1

    return 0


def main() -> int:
    """Main entry point for the application."""
    args = parse_arguments()
    return run_tournament(args)


if __name__ == "__main__":
    sys.exit(main())
