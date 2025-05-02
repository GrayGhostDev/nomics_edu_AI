from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from game_generator import GameGenerator, TeacherProfile, GameRequest
from template_manager import TemplateManager
import os
import uuid
import json
from datetime import datetime

def get_teacher_info():
    """Get teacher information from user input"""
    print("\nPlease provide your information:")
    teacher_id = str(uuid.uuid4())[:8]  # Generate a unique ID
    name = input("Your name: ")
    school = input("School name: ")
    grade_level = input("What grade do you teach: ")
    subjects = input("Your subjects (comma-separated): ").split(',')
    teaching_style = input("Your preferred teaching style (e.g., Interactive, Traditional, Project-based): ")
    
    return {
        "teacher": {
            "id": teacher_id,
            "name": name,
            "school": school,
            "grade_level": grade_level,
            "subjects": [s.strip() for s in subjects],
            "preferred_teaching_style": teaching_style,
            "timestamp": datetime.now().isoformat()
        }
    }

def get_game_request(subject: str, template_manager: TemplateManager):
    """Get game request details based on subject"""
    print(f"\nPlease provide details about your {subject.title()} game:")
    
    topic = input("Enter specific topic: ")
    objectives = input("Enter learning objectives (comma-separated): ").split(',')
    grade_input = input("Enter target grade level: ")
    # Extract numeric part from grade input (e.g., "4th" -> "4")
    grade_level = int(''.join(filter(str.isdigit, grade_input)))
    difficulty = int(input("Enter difficulty level (1-3): "))
    
    # Get compatible templates
    compatible_templates = template_manager.get_compatible_templates(subject, grade_level, difficulty)
    if not compatible_templates:
        print(f"Warning: No templates found for {subject} (grade {grade_level}, difficulty {difficulty})")
        print("Using default template settings...")
    else:
        print("\nCompatible templates:")
        for i, template in enumerate(compatible_templates, 1):
            print(f"{i}. {template.metadata.name} (v{template.metadata.version})")
            print(f"   Description: {template.metadata.description}")
            print(f"   Tags: {', '.join(template.metadata.tags)}")
    
    # Subject-specific content gathering
    if subject.lower() == "mathematics":
        custom_content = input("Enter any specific math requirements (e.g., 'Include word problems about real-world scenarios'): ")
        if compatible_templates:
            game_type = compatible_templates[0].metadata.name
        else:
            game_type = input("Choose game type (MathQuest/NumberParkour): ")
        problem_types = input("Enter types of problems to include (comma-separated): ").split(',')
        value_ranges = input("Enter number ranges (min-max, e.g., '1-100'): ").split('-')
        
        game_specifics = {
            "problem_types": [p.strip() for p in problem_types],
            "value_ranges": {
                "min": int(value_ranges[0]),
                "max": int(value_ranges[1]) if len(value_ranges) > 1 else 100
            }
        }
    elif subject.lower() == "science":
        custom_content = input("Enter any specific science requirements (e.g., 'Include interactive experiments about chemical reactions'): ")
        if compatible_templates:
            game_type = compatible_templates[0].metadata.name
        else:
            game_type = input("Choose game type (BioLabSimulator/ScienceQuest): ")
        experiment_types = input("Enter types of experiments to include (comma-separated): ").split(',')
        equipment = input("Enter required equipment (comma-separated): ").split(',')
        safety_guidelines = input("Enter safety guidelines (comma-separated): ").split(',')
        
        game_specifics = {
            "experiment_types": [e.strip() for e in experiment_types],
            "equipment": [e.strip() for e in equipment],
            "safety_guidelines": [s.strip() for s in safety_guidelines]
        }
    else:
        custom_content = input(f"Enter any specific {subject} requirements: ")
        game_type = compatible_templates[0].metadata.name if compatible_templates else None
        game_specifics = {}
    
    time_limit = input("Enter time limit in minutes (optional, press Enter to skip): ")
    
    return {
        "game_request": {
            "subject": subject,
            "topic": topic,
            "learning_objectives": [obj.strip() for obj in objectives],
            "grade_level": grade_level,
            "difficulty": difficulty,
            "custom_content": custom_content,
            "game_type": game_type,
            "time_limit": int(time_limit) if time_limit.strip() else None,
            "game_specifics": game_specifics,
            "timestamp": datetime.now().isoformat()
        }
    }

def get_template_content(subject: str, game_type: str) -> str:
    """Get the content of the template file"""
    template_path = os.path.join("Games", subject, f"{game_type}.lua")
    try:
        with open(template_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading template: {e}")
        return ""

def create_llm_prompt(llm_input: dict, template_content: str) -> str:
    """Create the prompt for the LLM"""
    teacher = llm_input["teacher_info"]
    game = llm_input["game_request"]
    
    prompt = f"""You are an expert Roblox educational game designer. Create a Lua script for an educational game based on the following requirements:

Teacher Information:
- Name: {teacher["name"]}
- School: {teacher["school"]}
- Grade Level: {teacher["grade_level"]}
- Teaching Style: {teacher["preferred_teaching_style"]}

Game Requirements:
- Subject: {game["subject"]}
- Topic: {game["topic"]}
- Learning Objectives: {', '.join(game["learning_objectives"])}
- Grade Level: {game["grade_level"]}
- Difficulty: {game["difficulty"]}
- Custom Content: {game["custom_content"]}
"""

    if "game_specifics" in game:
        if game["subject"].lower() == "mathematics":
            prompt += f"""
Mathematics Specific Requirements:
- Problem Types: {', '.join(game["game_specifics"]["problem_types"])}
- Value Ranges: {game["game_specifics"]["value_ranges"]["min"]} to {game["game_specifics"]["value_ranges"]["max"]}
"""
        elif game["subject"].lower() == "science":
            prompt += f"""
Science Specific Requirements:
- Experiment Types: {', '.join(game["game_specifics"]["experiment_types"])}
- Equipment: {', '.join(game["game_specifics"]["equipment"])}
- Safety Guidelines: {', '.join(game["game_specifics"]["safety_guidelines"])}
"""

    prompt += f"""
Base Template:
{template_content}

Instructions:
1. Use the provided template as a base structure
2. Modify the template to incorporate the teacher's requirements and style
3. Ensure the content is appropriate for the specified grade level
4. Include all necessary Lua functions and game logic
5. Maintain proper Lua syntax and structure
6. Include appropriate comments and documentation

Generate ONLY the Lua code. Do not include any explanations or markdown formatting.
"""
    return prompt

def main():
    print("Welcome to the Roblox Educational Game Generator!")
    
    # Initialize Ollama LLM
    try:
        llm = OllamaLLM(
            model="llama3.2",
            temperature=0.7,
            base_url="http://localhost:11434"
        )
    except Exception as e:
        print(f"Error initializing Ollama: {str(e)}")
        print("Please make sure Ollama is running locally (http://localhost:11434)")
        return
    
    # Initialize template manager
    template_manager = TemplateManager()
    
    # Get available subjects
    subjects = [t.metadata.subject for t in template_manager.templates.values()]
    subjects = list(set(subjects))  # Remove duplicates
    
    # Display subject options
    print("\nAvailable subjects:")
    for i, subject in enumerate(subjects, 1):
        print(f"{i}. {subject}")
        templates = template_manager.get_templates_for_subject(subject)
        print(f"   Available templates: {', '.join(t.metadata.name for t in templates)}")
    
    # Get subject choice
    while True:
        try:
            choice = int(input("\nSelect a subject number: "))
            if 1 <= choice <= len(subjects):
                selected_subject = subjects[choice - 1]
                break
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get teacher and game information
    teacher_data = get_teacher_info()
    game_data = get_game_request(selected_subject, template_manager)
    
    # Format data for LLM
    llm_input = {
        "metadata": {
            "version": "1.0",
            "generation_time": datetime.now().isoformat()
        },
        "teacher_info": teacher_data["teacher"],
        "game_request": game_data["game_request"]
    }
    
    # Save the input data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    input_file = f"llm_input_{timestamp}.json"
    with open(input_file, 'w') as f:
        json.dump(llm_input, f, indent=2)
    
    print("\nData collection complete!")
    print(f"Input data saved to: {input_file}")
    
    try:
        print("\nGenerating your educational game...")
        
        # Get template
        grade_level = int(game_data["game_request"]["grade_level"])
        difficulty = game_data["game_request"]["difficulty"]
        compatible_templates = template_manager.get_compatible_templates(
            selected_subject, grade_level, difficulty
        )
        
        if not compatible_templates:
            raise ValueError(f"No compatible templates found for {selected_subject} (grade {grade_level}, difficulty {difficulty})")
            
        template = compatible_templates[0]
        print(f"Using template: {template.metadata.name} (v{template.metadata.version})")
        
        # Create LLM prompt
        prompt = create_llm_prompt(llm_input, template.content)
        
        # Create prompt template
        prompt_template = PromptTemplate.from_template(prompt)
        
        # Generate the game script
        print("Generating script using LLM...")
        response = llm.invoke(prompt)
        generated_script = str(response).strip()
        
        # Save the generated script
        output_dir = os.path.join("games_input", selected_subject)
        os.makedirs(output_dir, exist_ok=True)
        
        script_file = os.path.join(output_dir, f"{teacher_data['teacher']['id']}_{timestamp}.lua")
        with open(script_file, 'w') as f:
            f.write(generated_script)
        
        print("\nSuccess! 🎮")
        print(f"Your game has been generated at: {script_file}")
        print("\nNext steps:")
        print("1. Open Roblox Studio")
        print("2. Import the generated Lua script")
        print("3. Test and customize as needed")
        
    except Exception as e:
        print(f"\nError generating game: {str(e)}")
        print("Please try again or contact support if the issue persists.")

if __name__ == "__main__":
    main()

