from typing import Dict, Any, Optional, Union
import os
import json
from abc import ABC, abstractmethod
import requests
import openai
from cache_manager import CacheManager

class LLMHandler(ABC):
    def __init__(self):
        self.cache_manager = CacheManager()
        
    @abstractmethod
    def _generate_script_uncached(self, game_data: Dict[str, Any], template_content: str) -> str:
        pass
        
    def generate_game_script(self, game_data: Dict[str, Any], template_content: str) -> str:
        """Generate game script with caching"""
        # Try to get from cache first
        cached_response = self.cache_manager.get(game_data, template_content)
        if cached_response:
            print("Using cached response...")
            return cached_response
            
        # Generate new response
        print("Generating new response...")
        response = self._generate_script_uncached(game_data, template_content)
        
        # Cache the response
        self.cache_manager.set(game_data, template_content, response)
        
        return response

class OllamaHandler(LLMHandler):
    def __init__(self, model: str = "llama2"):
        super().__init__()
        self.model = model
        self.api_base = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
        
    def _generate_script_uncached(self, game_data: Dict[str, Any], template_content: str) -> str:
        # Read template
        prompt = self._prepare_prompt(game_data, template_content)
        
        # Call Ollama API
        response = requests.post(
            f"{self.api_base}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.text}")
            
        return response.json()['response']
        
    def _prepare_prompt(self, game_data: Dict[str, Any], template: str) -> str:
        return f"""
        You are a Roblox educational game generator. Generate a Lua script based on the following template and requirements:
        
        Teacher Info:
        - Name: {game_data['teacher']['name']}
        - School: {game_data['teacher']['school']}
        - Grade Level: {game_data['teacher']['grade_level']}
        - Teaching Style: {game_data['teacher']['preferred_teaching_style']}
        
        Game Requirements:
        - Subject: {game_data['request']['subject']}
        - Topic: {game_data['request']['topic']}
        - Learning Objectives: {', '.join(game_data['request']['objectives'])}
        - Grade Level: {game_data['request']['grade_level']}
        - Difficulty: {game_data['request']['difficulty']}
        
        Custom Content:
        {game_data['request']['custom_content']}
        
        Template:
        {template}
        
        Generate a complete Lua script that follows the template structure but is personalized for this teacher and their requirements.
        Ensure all game mechanics and content are appropriate for the specified grade level and difficulty.
        """

class OpenAIHandler(LLMHandler):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        openai.api_key = self.api_key
        
    def _generate_script_uncached(self, game_data: Dict[str, Any], template_content: str) -> str:
        # Prepare messages
        messages = self._prepare_messages(game_data, template_content)
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
        
    def _prepare_messages(self, game_data: Dict[str, Any], template: str) -> list:
        return [
            {"role": "system", "content": "You are a Roblox educational game generator that creates personalized Lua scripts based on templates and teacher requirements."},
            {"role": "user", "content": f"""
            Generate a Lua script based on the following template and requirements:
            
            Teacher Info:
            - Name: {game_data['teacher']['name']}
            - School: {game_data['teacher']['school']}
            - Grade Level: {game_data['teacher']['grade_level']}
            - Teaching Style: {game_data['teacher']['preferred_teaching_style']}
            
            Game Requirements:
            - Subject: {game_data['request']['subject']}
            - Topic: {game_data['request']['topic']}
            - Learning Objectives: {', '.join(game_data['request']['objectives'])}
            - Grade Level: {game_data['request']['grade_level']}
            - Difficulty: {game_data['request']['difficulty']}
            
            Custom Content:
            {game_data['request']['custom_content']}
            
            Template:
            {template}
            """}
        ]

class LLMFactory:
    @staticmethod
    def create_handler(provider: str = "ollama", **kwargs) -> LLMHandler:
        if provider.lower() == "ollama":
            return OllamaHandler(**kwargs)
        elif provider.lower() == "openai":
            return OpenAIHandler(**kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

# Validation functions
def validate_generated_script(script: str, subject: str) -> bool:
    """Validate generated Lua script"""
    # Basic validation
    if not script or not script.strip():
        return False
        
    # Check for required Lua elements
    required_elements = [
        "function",
        "local",
        "end"
    ]
    
    for element in required_elements:
        if element not in script:
            return False
            
    # Subject-specific validation
    subject_validators = {
        "Mathematics": _validate_math_script,
        "Science": _validate_science_script,
        # Add more subject validators as needed
    }
    
    validator = subject_validators.get(subject)
    if validator:
        return validator(script)
        
    return True

def _validate_math_script(script: str) -> bool:
    """Validate mathematics-specific elements"""
    required_math_elements = [
        "generateProblem",
        "checkAnswer",
        "difficulty"
    ]
    
    return all(element in script for element in required_math_elements)

def _validate_science_script(script: str) -> bool:
    """Validate science-specific elements"""
    required_science_elements = [
        "setupExperiment",
        "checkResults",
        "safetyChecks"
    ]
    
    return all(element in script for element in required_science_elements) 