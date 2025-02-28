"""
Assessment framework class for the LLM Tournament application.
"""

from typing import Dict, List, Any
from models.data_models import AssessmentFrameworkModel, CriterionModel, ScoringSystemModel


class AssessmentFramework:
    """
    Represents the assessment framework for evaluating contenders.
    Manages criteria, rules, and scoring system.
    """
    
    def __init__(
        self, 
        id: str, 
        description: str, 
        evaluation_criteria: List[Dict[str, Any]], 
        comparison_rules: List[str],
        scoring_system: Dict[str, Any]
    ):
        """
        Initialize an assessment framework.
        
        Args:
            id: Unique identifier for the framework
            description: Description of the framework
            evaluation_criteria: List of criteria for evaluation
            comparison_rules: List of rules for comparing contenders
            scoring_system: Dictionary defining the scoring system
        """
        self.id = id
        self.description = description
        
        # Convert criteria to proper objects
        self.evaluation_criteria = []
        for criterion in evaluation_criteria:
            self.evaluation_criteria.append({
                "name": criterion["name"],
                "description": criterion["description"],
                "weight": criterion["weight"]
            })
        
        self.comparison_rules = comparison_rules
        
        # Setup scoring system
        self.scoring_system = {
            "type": scoring_system.get("type", "points"),
            "scale": scoring_system.get("scale", {"min": 0, "max": 10}),
            "categories": scoring_system.get("categories", [])
        }
    
    def validate(self) -> bool:
        """
        Validate that the framework is properly structured.
        
        Returns:
            True if valid, False otherwise
        """
        # Check that criteria weights sum to approximately 1.0
        total_weight = sum(criterion["weight"] for criterion in self.evaluation_criteria)
        if not (0.99 <= total_weight <= 1.01):  # Allow for small floating point errors
            print(f"Criteria weights must sum to 1.0, got {total_weight}")
            return False
        
        # Check that all criteria have required fields
        for i, criterion in enumerate(self.evaluation_criteria):
            if "name" not in criterion or "description" not in criterion or "weight" not in criterion:
                print(f"Criterion at index {i} is missing required fields")
                return False
        
        # Check scoring system
        if "type" not in self.scoring_system:
            print("Scoring system is missing 'type' field")
            return False
        
        if self.scoring_system["type"] == "points" and "scale" not in self.scoring_system:
            print("Points scoring system is missing 'scale' field")
            return False
        
        return True
    
    def get_formatted_criteria(self) -> str:
        """
        Get criteria formatted for inclusion in prompts.
        
        Returns:
            Formatted string representation of criteria
        """
        criteria_text = "# Evaluation Criteria\n\n"
        
        for criterion in self.evaluation_criteria:
            criteria_text += f"## {criterion['name']} (Weight: {criterion['weight']:.2f})\n"
            criteria_text += f"{criterion['description']}\n\n"
        
        return criteria_text
    
    def get_formatted_rules(self) -> str:
        """
        Get comparison rules formatted for inclusion in prompts.
        
        Returns:
            Formatted string representation of rules
        """
        rules_text = "# Comparison Rules\n\n"
        
        for i, rule in enumerate(self.comparison_rules, 1):
            rules_text += f"{i}. {rule}\n"
        
        return rules_text
    
    def get_formatted_scoring(self) -> str:
        """
        Get scoring system formatted for inclusion in prompts.
        
        Returns:
            Formatted string representation of scoring system
        """
        scoring_text = "# Scoring System\n\n"
        
        scoring_text += f"Type: {self.scoring_system['type']}\n"
        
        if "scale" in self.scoring_system:
            min_val = self.scoring_system["scale"].get("min", 0)
            max_val = self.scoring_system["scale"].get("max", 10)
            scoring_text += f"Scale: {min_val} to {max_val}\n\n"
        
        if "categories" in self.scoring_system and self.scoring_system["categories"]:
            scoring_text += "Categories:\n"
            for category in self.scoring_system["categories"]:
                range_str = f"{category['range'][0]} to {category['range'][1]}"
                scoring_text += f"- {category['name']}: {range_str}\n"
        
        return scoring_text
    
    def to_model(self) -> AssessmentFrameworkModel:
        """
        Convert to a Pydantic model for serialization.
        
        Returns:
            AssessmentFrameworkModel instance
        """
        criteria_models = [
            CriterionModel(
                name=criterion["name"],
                description=criterion["description"],
                weight=criterion["weight"]
            ) for criterion in self.evaluation_criteria
        ]
        
        scoring_model = ScoringSystemModel(
            type=self.scoring_system["type"],
            scale=self.scoring_system["scale"],
            categories=self.scoring_system["categories"]
        )
        
        return AssessmentFrameworkModel(
            id=self.id,
            description=self.description,
            evaluation_criteria=criteria_models,
            comparison_rules=self.comparison_rules,
            scoring_system=scoring_model
        )
    
    @classmethod
    def from_model(cls, model: AssessmentFrameworkModel) -> 'AssessmentFramework':
        """
        Create an AssessmentFramework instance from a Pydantic model.
        
        Args:
            model: AssessmentFrameworkModel instance
            
        Returns:
            AssessmentFramework instance
        """
        # Convert criteria models to dictionaries
        criteria = [{
            "name": c.name,
            "description": c.description,
            "weight": c.weight
        } for c in model.evaluation_criteria]
        
        # Convert scoring system model to dictionary
        scoring_system = {
            "type": model.scoring_system.type,
            "scale": model.scoring_system.scale,
            "categories": model.scoring_system.categories
        }
        
        return cls(
            id=model.id,
            description=model.description,
            evaluation_criteria=criteria,
            comparison_rules=model.comparison_rules,
            scoring_system=scoring_system
        )
