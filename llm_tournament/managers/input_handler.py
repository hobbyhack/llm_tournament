"""
Input handler for the LLM Tournament application.
"""

import json
import os
from typing import Dict, List, Any, Tuple, Optional

from models.contender import Contender
from models.assessment import AssessmentFramework


class InputHandler:
    """
    Handles loading and validating input data.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the input handler with configuration.

        Args:
            config: Configuration settings
        """
        self.config = config

    def load_contenders(self, file_path: str) -> List[Contender]:
        """
        Load contenders from a JSON file.

        Args:
            file_path: Path to JSON file containing contenders

        Returns:
            List of Contender objects

        Raises:
            FileNotFoundError: If file not found
            ValueError: If JSON data is invalid
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Contenders file not found: {file_path}")

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate structure
            if "contenders" not in data or not isinstance(data["contenders"], list):
                raise ValueError(
                    "Invalid contenders file format. Expected 'contenders' array."
                )

            # Create Contender objects
            contenders = []
            for i, contender_data in enumerate(data["contenders"]):
                # Validate required fields
                if "id" not in contender_data:
                    raise ValueError(f"Contender at index {i} missing 'id'")
                if "content" not in contender_data:
                    raise ValueError(f"Contender at index {i} missing 'content'")

                # Create Contender object
                contender = Contender(
                    id=contender_data["id"],
                    content=contender_data["content"],
                    metadata=contender_data.get("metadata", {}),
                )
                contenders.append(contender)

            return contenders
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in contenders file: {e}")

    def load_framework(self, file_path: str) -> AssessmentFramework:
        """
        Load assessment framework from a JSON file.

        Args:
            file_path: Path to JSON file containing framework

        Returns:
            AssessmentFramework object

        Raises:
            FileNotFoundError: If file not found
            ValueError: If JSON data is invalid
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Framework file not found: {file_path}")

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate structure
            if "assessment_framework" not in data:
                raise ValueError(
                    "Invalid framework file format. Expected 'assessment_framework' object."
                )

            framework_data = data["assessment_framework"]

            # Validate required fields
            required_fields = [
                "id",
                "description",
                "evaluation_criteria",
                "comparison_rules",
                "scoring_system",
            ]
            for field in required_fields:
                if field not in framework_data:
                    raise ValueError(
                        f"Assessment framework missing required field: {field}"
                    )

            # Create AssessmentFramework object
            framework = AssessmentFramework(
                id=framework_data["id"],
                description=framework_data["description"],
                evaluation_criteria=framework_data["evaluation_criteria"],
                comparison_rules=framework_data["comparison_rules"],
                scoring_system=framework_data["scoring_system"],
            )

            # Validate framework
            if not framework.validate():
                raise ValueError("Invalid assessment framework")

            return framework
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in framework file: {e}")

    def validate_input(
        self, contenders: List[Contender], framework: AssessmentFramework
    ) -> bool:
        """
        Validate that input data is valid for running a tournament.

        Args:
            contenders: List of contenders
            framework: Assessment framework

        Returns:
            True if valid, False otherwise
        """
        # Check if we have at least 2 contenders
        if len(contenders) < 2:
            print("Tournament requires at least 2 contenders")
            return False

        # Check for duplicate contender IDs
        contender_ids = [c.id for c in contenders]
        if len(contender_ids) != len(set(contender_ids)):
            print("Duplicate contender IDs found")
            return False

        # Validate framework
        if not framework.validate():
            print("Invalid assessment framework")
            return False

        return True

    def load_from_directory(
        self, directory: str
    ) -> Tuple[Optional[List[Contender]], Optional[AssessmentFramework]]:
        """
        Load contenders and framework from a directory.

        Args:
            directory: Directory containing input files

        Returns:
            Tuple of (contenders, framework) or (None, None) if not found
        """
        contenders_file = None
        framework_file = None

        # Check if directory exists
        if not os.path.exists(directory) or not os.path.isdir(directory):
            return None, None

        # Look for input files
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                with open(
                    os.path.join(directory, filename), "r", encoding="utf-8"
                ) as f:
                    try:
                        data = json.load(f)
                        if "contenders" in data:
                            contenders_file = os.path.join(directory, filename)
                        elif "assessment_framework" in data:
                            framework_file = os.path.join(directory, filename)
                    except:
                        continue

        if not contenders_file or not framework_file:
            return None, None

        try:
            contenders = self.load_contenders(contenders_file)
            framework = self.load_framework(framework_file)
            return contenders, framework
        except Exception as e:
            print(f"Error loading input data: {e}")
            return None, None
