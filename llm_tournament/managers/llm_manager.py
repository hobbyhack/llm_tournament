"""
LLM manager for handling LLM API calls in the LLM Tournament application.
"""

import json
import time
from typing import Dict, Any, Optional, List
import traceback

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.llms import Ollama

from models.match import Match
from models.data_models import MatchResultModel, CriteriaScoreModel


class LLMManager:
    """
    Manages interactions with language models.
    Handles sending prompts and processing responses.
    """
    
    def __init__(self, config: Dict[str, Any], prompt_manager):
        """
        Initialize the LLM manager with configuration.
        
        Args:
            config: Configuration settings
            prompt_manager: Prompt manager instance
        """
        self.config = config
        self.prompt_manager = prompt_manager
        
        # Timeouts and retries
        self.timeout = config.get("llm", {}).get("timeout", 60)
        self.max_retries = config.get("llm", {}).get("max_retries", 3)
        self.retry_delay = config.get("llm", {}).get("retry_delay", 5)
        
        # Initialize LLM clients
        self._initialize_llm_clients()
    
    def _initialize_llm_clients(self) -> None:
        """Initialize LLM clients based on configuration."""
        provider = self.config.get("llm", {}).get("provider", "ollama")
        default_model = self.config.get("llm", {}).get("default_model", "phi4")
        
        self.llm_clients = {}
        
        # Setup Ollama client
        if provider == "ollama":
            self.llm_clients[default_model] = Ollama(
                model=default_model,
                callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
                temperature=0.1,
            )
            
            # Create clients for any different models in model_mapping
            model_mapping = self.config.get("llm", {}).get("model_mapping", {})
            for prompt_name, model_name in model_mapping.items():
                if model_name != default_model and model_name not in self.llm_clients:
                    self.llm_clients[model_name] = Ollama(
                        model=model_name,
                        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
                        temperature=0.1,
                    )
    
    def evaluate_match(self, match: Match) -> MatchResultModel:
        """
        Evaluate a match using the appropriate LLM.
        
        Args:
            match: Match to evaluate
            
        Returns:
            MatchResultModel with the evaluation result
            
        Raises:
            Exception: If evaluation fails and exceeds maximum retries
        """
        # Prepare the prompt variables
        prompt_vars = {
            "framework_description": match.assessment_framework.description,
            "formatted_criteria": match.assessment_framework.get_formatted_criteria(),
            "formatted_rules": match.assessment_framework.get_formatted_rules(),
            "formatted_scoring": match.assessment_framework.get_formatted_scoring(),
            "contender1_id": match.contender1.id,
            "contender1_content": match.contender1.content,
            "contender2_id": match.contender2.id,
            "contender2_content": match.contender2.content
        }
        
        # Get the prompt template
        prompt_content = self.prompt_manager.get_prompt("match_evaluation", **prompt_vars)
        if not prompt_content:
            raise ValueError("Failed to load match_evaluation prompt")
        
        # Get the model to use
        model_name = self.prompt_manager.get_model_for_prompt("match_evaluation")
        llm = self.llm_clients.get(model_name)
        if not llm:
            raise ValueError(f"LLM model not configured: {model_name}")
        
        # Create the prompt chain
        prompt = PromptTemplate.from_template(prompt_content)
        chain = (
            {"prompt": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # Execute the chain
        try:
            response = chain.invoke({"prompt": ""})
            
            # Extract JSON from response (may be surrounded by markdown code blocks)
            json_data = self._extract_json(response)
            
            # Convert to MatchResultModel
            result = self._parse_match_result(json_data, match)
            
            return result
        except Exception as e:
            print(f"Error evaluating match {match.id}: {e}")
            print(traceback.format_exc())
            raise
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from response text, handling markdown code blocks.
        
        Args:
            text: Response text that may contain JSON
            
        Returns:
            Parsed JSON data
            
        Raises:
            ValueError: If JSON cannot be parsed
        """
        # Try to extract JSON from markdown code blocks
        json_matches = re.findall(r'```(?:json)?\s*([\s\S]*?)```', text)
        if json_matches:
            for json_text in json_matches:
                try:
                    return json.loads(json_text.strip())
                except:
                    continue
        
        # If no JSON found in code blocks, try parsing the entire text
        try:
            return json.loads(text.strip())
        except:
            pass
        
        # Look for parts that might be JSON (between curly braces)
        json_matches = re.findall(r'{[\s\S]*}', text)
        if json_matches:
            for json_text in json_matches:
                try:
                    return json.loads(json_text.strip())
                except:
                    continue
        
        raise ValueError("Could not extract valid JSON from response")
    
    def _parse_match_result(self, json_data: Dict[str, Any], match: Match) -> MatchResultModel:
        """
        Parse JSON data into a MatchResultModel.
        
        Args:
            json_data: Parsed JSON data
            match: Match being evaluated
            
        Returns:
            MatchResultModel instance
            
        Raises:
            ValueError: If JSON data is invalid
        """
        # Validate required fields
        required_fields = ["criteria_scores", "contender1_score", "contender2_score", "rationale"]
        for field in required_fields:
            if field not in json_data:
                raise ValueError(f"Missing required field in LLM response: {field}")
        
        # Parse criteria scores
        criteria_scores = {}
        for criterion_name, scores in json_data["criteria_scores"].items():
            if "contender1" not in scores or "contender2" not in scores:
                raise ValueError(f"Invalid scores for criterion {criterion_name}")
            
            criteria_scores[criterion_name] = CriteriaScoreModel(
                contender1=float(scores["contender1"]),
                contender2=float(scores["contender2"])
            )
        
        # Determine winner if not provided
        winner = json_data.get("winner")
        if winner is None:
            # In case of a tie
            if json_data["contender1_score"] == json_data["contender2_score"]:
                winner = None
            elif json_data["contender1_score"] > json_data["contender2_score"]:
                winner = match.contender1.id
            else:
                winner = match.contender2.id
        
        # Create MatchResultModel
        return MatchResultModel(
            winner=winner,
            contender1_score=float(json_data["contender1_score"]),
            contender2_score=float(json_data["contender2_score"]),
            rationale=json_data["rationale"],
            criteria_scores=criteria_scores
        )
    
    def retry_evaluation(self, match: Match) -> Optional[MatchResultModel]:
        """
        Retry evaluation with exponential backoff.
        
        Args:
            match: Match to evaluate
            
        Returns:
            MatchResultModel if successful, None otherwise
        """
        retries = 0
        max_retries = self.max_retries
        
        while retries < max_retries:
            try:
                return self.evaluate_match(match)
            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    print(f"Failed to evaluate match {match.id} after {max_retries} retries")
                    return None
                
                # Exponential backoff
                delay = self.retry_delay * (2 ** (retries - 1))
                print(f"Retry {retries}/{max_retries} for match {match.id} in {delay} seconds. Error: {e}")
                time.sleep(delay)
    
    def validate_response(self, response: str, expected_format: str) -> Dict[str, Any]:
        """
        Validate LLM response against expected format.
        
        Args:
            response: LLM response to validate
            expected_format: Expected format description
            
        Returns:
            Dictionary with validation result
        """
        # Prepare prompt variables
        prompt_vars = {
            "response": response,
            "expected_format": expected_format
        }
        
        # Get the prompt
        prompt_content = self.prompt_manager.get_prompt("validation", **prompt_vars)
        if not prompt_content:
            raise ValueError("Failed to load validation prompt")
        
        # Get the model
        model_name = self.prompt_manager.get_model_for_prompt("validation")
        llm = self.llm_clients.get(model_name)
        if not llm:
            raise ValueError(f"LLM model not configured: {model_name}")
        
        # Create the prompt chain
        prompt = PromptTemplate.from_template(prompt_content)
        chain = (
            {"prompt": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # Execute the chain
        try:
            validation_response = chain.invoke({"prompt": ""})
            json_data = self._extract_json(validation_response)
            
            # Check if validation was successful
            if json_data.get("is_valid", False):
                return {"success": True, "data": json_data.get("corrected_response", {})}
            else:
                return {
                    "success": False, 
                    "error": json_data.get("error_message", "Unknown validation error")
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
