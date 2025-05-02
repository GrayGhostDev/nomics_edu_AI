import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
from teacher_input_handler import TeacherInputHandler, TeacherProfile, GameRequest
from llm_handler import LLMFactory
from game_transformer import GameDataTransformer
from template_manager import TemplateManager
from script_validator import ScriptValidator

class GameGenerator:
    def __init__(self, llm_provider: str = "ollama", **llm_kwargs):
        self.input_handler = TeacherInputHandler()
        self.llm_handler = LLMFactory.create_handler(llm_provider, **llm_kwargs)
        self.transformer = GameDataTransformer()
        self.template_manager = TemplateManager()
        self.validator = ScriptValidator()
        
    def generate_from_manual_input(self, teacher: TeacherProfile, request: GameRequest) -> str:
        """Generate game from manual teacher input"""
        print(f"Processing request for {teacher.name} from {teacher.school}")
        
        # Process input and get game data
        game_data = self.input_handler.process_manual_input(teacher, request)
        
        return self._generate_game(game_data)
        
    def generate_from_lms_data(self, lms_data: Dict[str, Any]) -> str:
        """Generate game from LMS data"""
        print(f"Processing LMS data for teacher {lms_data.get('teacher_name')}")
        
        # Process LMS data
        game_data = self.input_handler.process_lms_data(lms_data)
        
        return self._generate_game(game_data)
        
    def _generate_game(self, game_data: Dict[str, Any]) -> str:
        """Internal method to generate game script"""
        subject = game_data['request']['subject']
        grade_level = int(game_data['request']['grade_level'])
        difficulty = game_data['request']['difficulty']
        print(f"Generating {subject} game...")
        
        # Get compatible templates
        compatible_templates = self.template_manager.get_compatible_templates(
            subject, grade_level, difficulty
        )
        
        if not compatible_templates:
            raise ValueError(f"No compatible templates found for {subject} (grade {grade_level}, difficulty {difficulty})")
            
        # Select template (for now, just use the first compatible one)
        template = compatible_templates[0]
        print(f"Using template: {template.metadata.name} (v{template.metadata.version})")
        
        # Generate script using LLM
        print("Generating script using LLM...")
        script = self.llm_handler.generate_game_script(game_data, template.content)
        
        # Validate generated script
        print("Validating generated script...")
        validation_result = self.validator.validate_script(
            script, subject, grade_level, difficulty
        )
        
        if validation_result.has_errors:
            print("\nValidation errors found:")
            print(validation_result)
            raise ValueError("Generated script failed validation")
            
        if validation_result.has_warnings:
            print("\nValidation warnings:")
            print(validation_result)
            
        # Transform and save the script
        print("Transforming and saving script...")
        output_path = self._save_script(script, game_data)
        
        print(f"Game generated successfully at: {output_path}")
        return output_path
        
    def _save_script(self, script: str, game_data: Dict[str, Any]) -> str:
        """Save generated script to appropriate location"""
        subject = game_data['request']['subject']
        teacher_id = game_data['teacher']['id']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create output directory
        output_dir = os.path.join("games_input", subject)
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename
        topic = game_data['request']['topic'].replace(' ', '_').lower()
        filename = f"{teacher_id}_{topic}_{timestamp}.lua"
        output_path = os.path.join(output_dir, filename)
        
        # Save script
        with open(output_path, 'w') as f:
            f.write(script)
            
        return output_path

def main():
    # Example usage
    teacher = TeacherProfile(
        teacher_id="T123",
        name="John Doe",
        school="Example High School",
        grade_level="9",
        subjects=["Mathematics", "Science"],
        preferred_teaching_style="Interactive"
    )
    
    request = GameRequest(
        subject="Mathematics",
        topic="Algebra Basics",
        learning_objectives=["Understand linear equations", "Solve for variables"],
        grade_level="9",
        difficulty=2,
        custom_content="Focus on real-world applications",
        game_type="MathQuest"
    )
    
    # Create generator with default Ollama
    generator = GameGenerator()
    
    try:
        # Generate game from manual input
        output_path = generator.generate_from_manual_input(teacher, request)
        print(f"Game generated at: {output_path}")
        
        # Example LMS data
        lms_data = {
            "teacher_id": "T456",
            "teacher_name": "Jane Smith",
            "school": "Example Middle School",
            "grade_level": "7",
            "subjects": ["Science"],
            "teaching_style": "Hands-on",
            "subject": "Science",
            "topic": "Basic Chemistry",
            "objectives": ["Understand atoms", "Learn about molecules"],
            "difficulty": 1,
            "custom_content": "Include interactive experiments"
        }
        
        # Generate game from LMS data
        output_path = generator.generate_from_lms_data(lms_data)
        print(f"Game generated at: {output_path}")
        
    except Exception as e:
        print(f"Error generating game: {str(e)}")

if __name__ == "__main__":
    main() 