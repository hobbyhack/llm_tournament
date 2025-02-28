"""
Prompt manager for the LLM Tournament application.
"""

import os
import re
from typing import Dict, Any, Optional
from string import Template


class PromptManager:
    """
    Manages prompt templates for LLM interactions.
    Handles loading templates from files and formatting them with variables.
    """
    
    def __init__(self, prompt_directory: str, config: Dict[str, Any]):
        """
        Initialize with the directory containing prompt templates.
        
        Args:
            prompt_directory: Path to directory containing prompt markdown files
            config: Configuration settings
        """
        self.prompt_directory = prompt_directory
        self.config = config
        self.prompt_templates = {}
        self.model_mapping = config.get("llm", {}).get("model_mapping", {})
        self.default_model = config.get("llm", {}).get("default_model", "llama3")
        
        # Load all prompt templates
        self._load_prompt_templates()
    
    def _load_prompt_templates(self) -> None:
        """Load all prompt templates from the prompt directory."""
        if not os.path.exists(self.prompt_directory):
            raise FileNotFoundError(f"Prompt directory not found: {self.prompt_directory}")
        
        for filename in os.listdir(self.prompt_directory):
            if filename.endswith(".md"):
                prompt_name = os.path.splitext(filename)[0]
                file_path = os.path.join(self.prompt_directory, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        template_content = f.read()
                    
                    self.prompt_templates[prompt_name] = template_content
                except Exception as e:
                    print(f"Error loading prompt template {filename}: {e}")
    
    def get_prompt(self, prompt_name: str, **kwargs: Any) -> Optional[str]:
        """
        Get a prompt with variables filled in.
        
        Args:
            prompt_name: Name of the prompt (without extension)
            **kwargs: Variables to substitute in the template
            
        Returns:
            Formatted prompt string or None if not found
        """
        if prompt_name not in self.prompt_templates:
            print(f"Prompt template not found: {prompt_name}")
            return None
        
        template = self.prompt_templates[prompt_name]
        
        # Replace $variable with value
        template_obj = Template(template)
        try:
            return template_obj.substitute(**kwargs)
        except KeyError as e:
            print(f"Missing variable in prompt template {prompt_name}: {e}")
            return None
    
    def get_model_for_prompt(self, prompt_name: str) -> str:
        """
        Get the model to use for a specific prompt.
        
        Args:
            prompt_name: Name of the prompt
            
        Returns:
            Model name to use for this prompt
        """
        return self.model_mapping.get(prompt_name, self.default_model)
    
    def create_default_prompts(self) -> None:
        """Create default prompt templates if they don't exist."""
        if not os.path.exists(self.prompt_directory):
            os.makedirs(self.prompt_directory)
        
        default_prompts = {
            "match_evaluation.md": self._get_default_match_evaluation_prompt(),
            "contender_comparison.md": self._get_default_contender_comparison_prompt(),
            "scoring.md": self._get_default_scoring_prompt(),
            "validation.md": self._get_default_validation_prompt()
        }
        
        for filename, content in default_prompts.items():
            file_path = os.path.join(self.prompt_directory, filename)
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Created default prompt template: {filename}")
                except Exception as e:
                    print(f"Error creating default prompt template {filename}: {e}")
    
    def _get_default_match_evaluation_prompt(self) -> str:
        """Get the default match evaluation prompt template."""
        return """# Tournament Match Evaluation

## Assessment Framework
$framework_description

$formatted_criteria

$formatted_rules

$formatted_scoring

## Contenders

### Contender 1
$contender1_content

### Contender 2
$contender2_content

## Task
Evaluate these two contenders based on the assessment framework. Compare them directly against each other for each criterion.

## Response Format
Respond with a JSON object in the following format:
```json
{
  "criteria_scores": {
    "[criterion_name]": {
      "contender1": [score],
      "contender2": [score]
    },
    // Repeat for each criterion
  },
  "contender1_score": [overall_score],
  "contender2_score": [overall_score],
  "winner": "[contender1_id or contender2_id]",
  "rationale": "[detailed explanation]"
}
```

Set the "winner" field to the ID of the winning contender. If it's a tie, you can set this to null.
The "rationale" should explain your reasoning in detail, highlighting the key differentiating factors.
"""
    
    def _get_default_contender_comparison_prompt(self) -> str:
        """Get the default contender comparison prompt template."""
        return """# Contender Comparison

## Criteria
$formatted_criteria

## Contenders

### Contender 1: $contender1_id
$contender1_content

### Contender 2: $contender2_id
$contender2_content

## Task
Compare these two contenders directly against each other using the provided criteria. For each criterion, determine which contender is stronger and explain why.

## Response Format
Respond with a JSON object in the following format:
```json
{
  "comparisons": [
    {
      "criterion": "[criterion_name]",
      "winner": "[contender1_id or contender2_id]",
      "explanation": "[detailed explanation]"
    },
    // Repeat for each criterion
  ],
  "overall_winner": "[contender1_id or contender2_id]",
  "rationale": "[detailed explanation]"
}
```
"""
    
    def _get_default_scoring_prompt(self) -> str:
        """Get the default scoring prompt template."""
        return """# Scoring Evaluation

## Scoring System
$formatted_scoring

## Evaluation
$evaluation

## Task
Based on the provided evaluation, assign scores according to the scoring system.

## Response Format
Respond with a JSON object in the following format:
```json
{
  "scores": {
    "[criterion_name]": {
      "contender1": [score],
      "contender2": [score]
    },
    // Repeat for each criterion
  },
  "overall_scores": {
    "contender1": [weighted_score],
    "contender2": [weighted_score]
  },
  "winner": "[contender1_id or contender2_id]"
}
```
"""
    
    def _get_default_validation_prompt(self) -> str:
        """Get the default validation prompt template."""
        return """# Response Validation

## Expected Format
$expected_format

## Actual Response
$response

## Task
Validate whether the response matches the expected format. If not, correct it to match the expected format.

## Response Format
Respond with a JSON object in the following format:
```json
{
  "is_valid": [true/false],
  "corrected_response": {
    // The corrected response in the expected format
  },
  "error_message": "[explanation of errors if any]"
}
```
"""
