import re
import os
from typing import Dict, List, Any, Tuple, Set

class GameDataTransformer:
    def __init__(self):
        self.template_dir = "Games"
        self.output_dir = "games_input"
        
        # Define subject-specific configurations
        self.subject_configs = {
            "mathematics": {
                "template_file": "MathQuest.lua",
                "injection_points": {
                    "dungeons": "-- [INJECT_DUNGEONS]",
                    "problems": "-- [INJECT_PROBLEMS]"
                },
                "content_type": "problems",
                "required_sections": ["problems"],
                "content_patterns": {
                    "problems": r'{{\s*type\s*=\s*["\']([^"\']+)["\'],\s*template\s*=\s*["\']([^"\']+)["\'],\s*range\s*=\s*{{\s*min\s*=\s*(\d+),\s*max\s*=\s*(\d+)\s*}}'
                }
            },
            "science": {
                "template_file": "BioLabSimulator.lua",
                "injection_points": {
                    "experiments": "-- [INJECT_EXPERIMENTS]",
                    "equipment": "-- [INJECT_EQUIPMENT_SETUP]",
                    "generator": "-- [INJECT_EXPERIMENT_GENERATOR]"
                },
                "content_type": "experiments",
                "required_sections": ["experiments", "equipment", "safety_guidelines"],
                "content_patterns": {
                    "experiments": r'{{\s*type\s*=\s*["\']([^"\']+)["\'],\s*template\s*=\s*["\']([^"\']+)["\'],\s*equipment\s*=\s*{([^}]+)},\s*safety\s*=\s*{([^}]+)}'
                }
            },
            "history": {
                "template_file": "HistoryQuest.lua",
                "injection_points": {
                    "scenarios": "-- [INJECT_SCENARIOS]",
                    "artifacts": "-- [INJECT_ARTIFACTS]",
                    "activities": "-- [INJECT_ACTIVITIES]"
                },
                "content_type": "scenarios",
                "required_sections": ["scenarios", "artifacts", "activities"],
                "content_patterns": {
                    "scenarios": r'{{\s*type\s*=\s*["\']([^"\']+)["\'],\s*template\s*=\s*["\']([^"\']+)["\'],\s*period\s*=\s*["\']([^"\']+)["\'],\s*figures\s*=\s*{([^}]+)}'
                }
            },
            "language_arts": {
                "template_file": "LanguageQuest.lua",
                "injection_points": {
                    "exercises": "-- [INJECT_EXERCISES]",
                    "skills": "-- [INJECT_SKILLS]",
                    "resources": "-- [INJECT_RESOURCES]"
                },
                "content_type": "exercises",
                "required_sections": ["exercises", "skills", "resources"],
                "content_patterns": {
                    "exercises": r'{{\s*type\s*=\s*["\']([^"\']+)["\'],\s*template\s*=\s*["\']([^"\']+)["\'],\s*skills\s*=\s*{([^}]+)},\s*activities\s*=\s*{([^}]+)}'
                }
            }
        }

    def read_input_file(self, file_path: str) -> Dict[str, Any]:
        """Read and parse Lua input file dynamically based on subject type."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract common configuration
            config = self._extract_common_config(content)
            
            # Determine subject from file path
            subject = self._determine_subject_from_path(file_path)
            if not subject:
                raise ValueError("Could not determine subject from file path")
            
            # Extract subject-specific content
            subject_config = self.subject_configs[subject]
            content_type = subject_config["content_type"]
            content_pattern = subject_config["content_patterns"][content_type]
            
            config["content"] = self._extract_subject_content(content, subject, content_pattern)
            
            return config
            
        except Exception as e:
            raise ValueError(f"Error reading input file {file_path}: {str(e)}")

    def _extract_common_config(self, content: str) -> Dict[str, Any]:
        """Extract common configuration elements from Lua content."""
        config = {}
        
        # Extract common fields
        patterns = {
            'title': r'title\s*=\s*["\']([^"\']+)["\']',
            'description': r'description\s*=\s*["\']([^"\']+)["\']',
            'topics': r'topics\s*=\s*{([^}]+)}',
            'difficulty': r'difficulty\s*=\s*(\d+)'
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                if field == 'topics':
                    config[field] = [t.strip(' "\'') for t in match.group(1).split(',')]
                elif field == 'difficulty':
                    config[field] = int(match.group(1))
                else:
                    config[field] = match.group(1)
        
        return config

    def _determine_subject_from_path(self, file_path: str) -> str:
        """Determine subject from file path."""
        for subject in self.subject_configs.keys():
            if subject.lower() in file_path.lower():
                return subject
        return None

    def _extract_subject_content(self, content: str, subject: str, pattern: str) -> Dict[str, Any]:
        """Extract subject-specific content using the provided pattern."""
        subject_config = self.subject_configs[subject]
        content_data = {}
        
        # Extract main content type (problems, experiments, scenarios, exercises)
        content_type = subject_config["content_type"]
        content_items = []
        
        matches = re.finditer(pattern, content)
        for match in matches:
            item = {}
            if subject == "mathematics":
                item = {
                    'type': match.group(1),
                    'template': match.group(2),
                    'range': {
                        'min': int(match.group(3)),
                        'max': int(match.group(4))
                    }
                }
            elif subject == "science":
                item = {
                    'type': match.group(1),
                    'template': match.group(2),
                    'equipment': [e.strip(' "\'') for e in match.group(3).split(',')],
                    'safety': [s.strip(' "\'') for s in match.group(4).split(',')]
                }
            elif subject == "history":
                item = {
                    'type': match.group(1),
                    'template': match.group(2),
                    'period': match.group(3),
                    'figures': [f.strip(' "\'') for f in match.group(4).split(',')]
                }
            elif subject == "language_arts":
                item = {
                    'type': match.group(1),
                    'template': match.group(2),
                    'skills': [s.strip(' "\'') for s in match.group(3).split(',')],
                    'activities': [a.strip(' "\'') for a in match.group(4).split(',')]
                }
            
            content_items.append(item)
        
        content_data[content_type] = content_items
        
        # Extract additional required sections
        for section in subject_config["required_sections"]:
            if section != content_type:
                section_match = re.search(f'{section}\\s*=\\s*{{([^}}]+)}}', content)
                if section_match:
                    content_data[section] = [s.strip(' "\'') for s in section_match.group(1).split(',')]
        
        return content_data

    def validate_input_data(self, data: Dict[str, Any], subject: str) -> bool:
        """Validate input data structure based on subject configuration."""
        # Check common required fields
        common_fields = ['title', 'description', 'topics', 'difficulty']
        for field in common_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Check subject-specific required sections
        subject_config = self.subject_configs.get(subject.lower())
        if not subject_config:
            raise ValueError(f"Unsupported subject: {subject}")
        
        if 'content' not in data:
            raise ValueError(f"{subject} content must include 'content' section")
        
        for section in subject_config["required_sections"]:
            if section not in data['content']:
                raise ValueError(f"{subject} content must include '{section}' section")
        
        return True

    def transform_from_file(self, subject: str, input_file: str) -> str:
        """Transform content from input file and generate game script."""
        # Read and validate input data
        data = self.read_input_file(input_file)
        self.validate_input_data(data, subject)
        
        # Create a clean title for the file name
        clean_title = re.sub(r'[^a-zA-Z0-9]+', '_', data['title'].lower()).strip('_')
        
        # Create initial Lua script with metadata
        lua_script = f"""-- Generated from {input_file}
-- Title: {data['title']}
-- Description: {data['description']}
local topics = {{{', '.join(f'"{topic}"' for topic in data['topics'])}}}
local difficulty = {data['difficulty']}
"""
        
        # Transform and inject using the data
        return self.transform_and_inject(subject, data['title'], lua_script)

    def calculate_difficulty(self, content: str) -> int:
        """Calculate difficulty level based on content complexity."""
        # Basic difficulty calculation based on keywords
        difficulty_keywords = {
            'basic': 1, 'simple': 1, 'elementary': 1,
            'intermediate': 2, 'advanced': 3, 'complex': 3,
            'multiplication': 2, 'division': 2,
            'algebra': 3, 'calculus': 3
        }
        
        content_lower = content.lower()
        max_difficulty = 1
        
        for keyword, level in difficulty_keywords.items():
            if keyword in content_lower:
                max_difficulty = max(max_difficulty, level)
        
        return max_difficulty

    def extract_topics(self, lua_script: str) -> List[str]:
        """Extract mathematical topics from the Lua script."""
        topics = []
        # Look for topic-related keywords in the script
        topic_patterns = [
            r'topic\s*=\s*["\'](\w+)["\']',
            r'topics\s*=\s*{([^}]+)}',
        ]
        
        for pattern in topic_patterns:
            matches = re.findall(pattern, lua_script)
            for match in matches:
                if isinstance(match, tuple):
                    # Handle multi-topic match
                    topics.extend([t.strip(' "\'') for t in match[0].split(',')])
                else:
                    # Handle single topic match
                    topics.append(match.strip(' "\''))
        
        # Clean up topics
        cleaned_topics = []
        for topic in topics:
            # Remove any remaining quotes and spaces
            clean_topic = re.sub(r'["\']', '', topic).strip()
            if clean_topic:
                cleaned_topics.append(clean_topic)
        
        return list(set(cleaned_topics)) if cleaned_topics else ["basic_math"]

    def generate_problems(self, content: str) -> List[Dict[str, Any]]:
        """Generate sample problems based on content."""
        problems = []
        content_lower = content.lower()
        
        # Problem patterns by difficulty
        patterns = {
            'addition': {
                1: [
                    {'template': '{a} + {b} = ?', 'range': {'min': 1, 'max': 10}},
                    {'template': '? + {b} = {result}', 'range': {'min': 1, 'max': 10}},
                ],
                2: [
                    {'template': '{a} + {b} + {c} = ?', 'range': {'min': 10, 'max': 50}},
                    {'template': '{a} + ? = {result}', 'range': {'min': 10, 'max': 50}},
                ],
                3: [
                    {'template': '{a} + {b} + {c} + {d} = ?', 'range': {'min': 50, 'max': 100}},
                    {'template': '? + {b} + {c} = {result}', 'range': {'min': 50, 'max': 100}},
                ]
            },
            'subtraction': {
                1: [
                    {'template': '{a} - {b} = ?', 'range': {'min': 1, 'max': 10}},
                    {'template': '{a} - ? = {result}', 'range': {'min': 1, 'max': 10}},
                ],
                2: [
                    {'template': '{a} - {b} - {c} = ?', 'range': {'min': 10, 'max': 50}},
                    {'template': '{a} - ? = {result}', 'range': {'min': 10, 'max': 50}},
                ],
                3: [
                    {'template': '{a} - {b} - {c} = ?', 'range': {'min': 50, 'max': 100}},
                    {'template': '{a} - ? - {c} = {result}', 'range': {'min': 50, 'max': 100}},
                ]
            },
            'multiplication': {
                1: [
                    {'template': '{a} × {b} = ?', 'range': {'min': 1, 'max': 5}},
                    {'template': '? × {b} = {result}', 'range': {'min': 1, 'max': 5}},
                ],
                2: [
                    {'template': '{a} × {b} = ?', 'range': {'min': 5, 'max': 12}},
                    {'template': '{a} × ? = {result}', 'range': {'min': 5, 'max': 12}},
                ],
                3: [
                    {'template': '({a} × {b}) + {c} = ?', 'range': {'min': 10, 'max': 20}},
                    {'template': '{a} × ? + {c} = {result}', 'range': {'min': 10, 'max': 20}},
                ]
            },
            'division': {
                1: [
                    {'template': '{result} ÷ {b} = ?', 'range': {'min': 1, 'max': 5}},
                    {'template': '{result} ÷ ? = {a}', 'range': {'min': 1, 'max': 5}},
                ],
                2: [
                    {'template': '{result} ÷ {b} = ?', 'range': {'min': 5, 'max': 12}},
                    {'template': '{result} ÷ ? = {a}', 'range': {'min': 5, 'max': 12}},
                ],
                3: [
                    {'template': '({result} ÷ {b}) + {c} = ?', 'range': {'min': 10, 'max': 20}},
                    {'template': '{result} ÷ ? + {c} = {a}', 'range': {'min': 10, 'max': 20}},
                ]
            }
        }
        
        difficulty = self.calculate_difficulty(content)
        
        # Add problems based on content keywords
        for topic, topic_patterns in patterns.items():
            if topic in content_lower:
                level_patterns = topic_patterns.get(difficulty, topic_patterns[1])
                for pattern in level_patterns:
                    problems.append({
                        'type': topic,
                        'template': pattern['template'],
                        'range': pattern['range']
                    })
        
        # Add word problem templates
        word_problems = {
            'addition': [
                "There are {a} apples and {b} oranges in the basket. How many fruits are there in total?",
                "{name} has {a} marbles. If they get {b} more, how many marbles will they have?",
            ],
            'subtraction': [
                "{name} has {a} cookies. If they give {b} to their friend, how many cookies will they have left?",
                "There are {a} birds in a tree. {b} birds fly away. How many birds are left?",
            ],
            'multiplication': [
                "Each bag has {a} candies. If there are {b} bags, how many candies are there in total?",
                "{name} needs {a} pencils for each student. If there are {b} students, how many pencils are needed?",
            ],
            'division': [
                "{name} has {result} stickers to share equally among {b} friends. How many stickers will each friend get?",
                "There are {result} cookies that need to be put into {b} boxes equally. How many cookies should go in each box?",
            ]
        }
        
        # Add word problems if content suggests it
        if 'word' in content_lower or 'story' in content_lower:
            for topic, templates in word_problems.items():
                if topic in content_lower:
                    for template in templates:
                        problems.append({
                            'type': f'{topic}_word',
                            'template': template,
                            'range': patterns[topic][difficulty]['range']
                        })
        
        # Add a default problem if none found
        if not problems:
            problems.append({
                'type': 'basic',
                'template': '{a} + {b} = ?',
                'range': {'min': 1, 'max': 10}
            })
        
        return problems

    def transform_math_content(self, content: str, lua_script: str) -> Dict[str, Any]:
        """Transform mathematics content into game data structure."""
        difficulty = self.calculate_difficulty(content)
        topics = self.extract_topics(lua_script)
        
        # Generate problems based on content
        problems = self.generate_problems(content)
        
        # Create problem generator function
        problem_generator = """
        -- Problem generator function
        function MathQuestArena:generateProblem(topic, difficulty)
            local problem = {
                question = "",
                answer = 0,
                topic = topic
            }
            
            -- Random name generator for word problems
            local names = {"Alex", "Sam", "Jordan", "Taylor", "Casey"}
            local function getRandomName()
                return names[math.random(1, #names)]
            end
            
            if topic == "addition" then
                local a = math.random(1, 10 * difficulty)
                local b = math.random(1, 10 * difficulty)
                problem.question = a .. " + " .. b .. " = ?"
                problem.answer = a + b
                
            elseif topic == "subtraction" then
                local a = math.random(10 * difficulty, 20 * difficulty)
                local b = math.random(1, a)
                problem.question = a .. " - " .. b .. " = ?"
                problem.answer = a - b
                
            elseif topic == "multiplication" then
                local a = math.random(1, 5 * difficulty)
                local b = math.random(1, 5 * difficulty)
                problem.question = a .. " × " .. b .. " = ?"
                problem.answer = a * b
                
            elseif topic == "division" then
                local b = math.random(1, 5 * difficulty)
                local answer = math.random(1, 5 * difficulty)
                local a = b * answer
                problem.question = a .. " ÷ " .. b .. " = ?"
                problem.answer = answer
            end
            
            return problem
        end
        """
        
        # Create dungeons based on topics
        dungeons = {}
        for i, topic in enumerate(topics):
            clean_topic = re.sub(r'[^a-zA-Z0-9]+', '_', topic.lower())
            dungeons[clean_topic] = {
                "name": f"{topic.title()} Challenge",
                "difficulty": difficulty,
                "monsters": [
                    f"{topic.title()} Novice",
                    f"{topic.title()} Adept",
                    f"{topic.title()} Master"
                ],
                "boss": f"{topic.title()} Grandmaster",
                "topics": [topic]
            }
        
        # Create dungeon initialization code
        dungeon_init = """
        -- Initialize dungeons
        self.dungeons = {
"""
        
        for dungeon_id, dungeon in dungeons.items():
            monsters_str = "{" + ", ".join(f'"{m}"' for m in dungeon["monsters"]) + "}"
            topics_str = "{" + ", ".join(f'"{t}"' for t in dungeon["topics"]) + "}"
            
            dungeon_init += f"""
            {dungeon_id} = {{
                name = "{dungeon['name']}",
                difficulty = {dungeon['difficulty']},
                monsters = {monsters_str},
                boss = "{dungeon['boss']}",
                topics = {topics_str}
            }},
"""
        
        dungeon_init += """
        }
"""
        
        return {
            "dungeons": dungeon_init,
            "problems": problem_generator
        }

    def inject_math_data(self, template_path: str, game_data: Dict[str, Any], output_path: str):
        """Inject mathematics game data into template."""
        try:
            # Read the template
            with open(template_path, 'r') as f:
                template_content = f.read()
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Replace injection points
            modified_content = template_content
            
            # Replace dungeons
            if "dungeons" in game_data:
                dungeon_marker = self.subject_configs["mathematics"]["injection_points"]["dungeons"]
                modified_content = modified_content.replace(dungeon_marker, game_data["dungeons"])
            
            # Replace problem generator
            if "problems" in game_data:
                problem_marker = self.subject_configs["mathematics"]["injection_points"]["problems"]
                # Find the entire generateProblem function and replace it
                pattern = r'function MathQuestArena:generateProblem\([^)]*\).*?end'
                if re.search(pattern, modified_content, re.DOTALL):
                    modified_content = re.sub(pattern, game_data["problems"].strip(), modified_content, flags=re.DOTALL)
                else:
                    # If function not found, just replace the marker
                    modified_content = modified_content.replace(problem_marker, game_data["problems"])
            
            # Validate the modified content
            if not self._validate_lua_syntax(modified_content):
                raise ValueError("Generated Lua script has invalid syntax")
            
            # Write the modified content
            with open(output_path, 'w') as f:
                f.write(modified_content)
            
            return output_path
            
        except Exception as e:
            raise ValueError(f"Error injecting math data: {str(e)}")

    def _generate_answer_calculation(self, problem_type: str) -> str:
        """Generate the Lua code for calculating the answer."""
        calculations = {
            'addition': 'a + b',
            'addition_word': 'a + b',
            'subtraction': 'a - b',
            'subtraction_word': 'a - b',
            'multiplication': 'a * b',
            'multiplication_word': 'a * b',
            'division': 'a',  # a is pre-calculated as result/b
            'division_word': 'a',
            'basic': 'a + b'
        }
        return calculations.get(problem_type, 'a + b')

    def transform_science_content(self, content: str, lua_script: str) -> Dict[str, Any]:
        """Transform science content into game data structure."""
        difficulty = self.calculate_difficulty(content)
        topics = self.extract_science_topics(lua_script)
        
        # Create experiment name from content
        experiment_name = re.sub(r'[^a-zA-Z0-9]+', '_', content.lower()).strip('_')
        
        # Get experiments and equipment from content
        experiments = []
        if isinstance(content, dict) and 'content' in content:
            if 'experiments' in content['content']:
                experiments = content['content']['experiments']
            equipment = content['content'].get('equipment', [])
        else:
            # Generate default equipment based on difficulty
            basic_equipment = ["Microscope", "Test Tubes", "Beakers", "Safety Goggles"]
            advanced_equipment = ["Centrifuge", "Spectrophotometer", "Bunsen Burner"]
            equipment = basic_equipment if difficulty <= 2 else basic_equipment + advanced_equipment
        
        return {
            "experimentName": experiment_name,
            "displayName": content['title'] if isinstance(content, dict) else content,
            "difficulty": difficulty,
            "topics": topics,
            "equipment": equipment,
            "experiments": experiments,
            "safetyLevel": "Advanced" if difficulty > 2 else "Basic"
        }

    def extract_science_topics(self, lua_script: str) -> List[str]:
        """Extract science topics from the Lua script."""
        topics = []
        topic_patterns = [
            r'topic\s*=\s*["\'](\w+)["\']',
            r'topics\s*=\s*{([^}]+)}',
        ]
        
        for pattern in topic_patterns:
            matches = re.findall(pattern, lua_script)
            for match in matches:
                if isinstance(match, tuple):
                    # Handle multi-topic match
                    topics.extend([t.strip(' "\'') for t in match[0].split(',')])
                else:
                    # Handle single topic match
                    topics.append(match.strip(' "\''))
        
        # Clean up topics
        cleaned_topics = []
        for topic in topics:
            # Remove any remaining quotes and spaces
            clean_topic = re.sub(r'["\']', '', topic).strip()
            if clean_topic:
                cleaned_topics.append(clean_topic)
        
        return list(set(cleaned_topics)) if cleaned_topics else ["basic_science"]

    def generate_experiments(self, content: str) -> List[Dict[str, Any]]:
        """Generate sample experiments based on content."""
        experiments = []
        content_lower = content.lower()
        
        # Basic experiment templates
        if 'microscope' in content_lower or 'cell' in content_lower:
            experiments.append({
                'type': 'microscopy',
                'template': 'Observe {specimen} under {magnification}x magnification',
                'equipment': ['Microscope', 'Slides', 'Cover Slips'],
                'safety': ['Handle slides carefully', 'Keep workspace clean']
            })
        if 'chemical' in content_lower or 'reaction' in content_lower:
            experiments.append({
                'type': 'chemical_reaction',
                'template': 'Mix {reagent1} with {reagent2} to observe {reaction}',
                'equipment': ['Test Tubes', 'Beakers', 'Safety Goggles'],
                'safety': ['Wear safety goggles', 'Handle chemicals carefully']
            })
        if 'dna' in content_lower or 'genetics' in content_lower:
            experiments.append({
                'type': 'dna_extraction',
                'template': 'Extract DNA from {sample} using {method}',
                'equipment': ['Test Tubes', 'Centrifuge', 'Pipettes'],
                'safety': ['Handle biological materials carefully', 'Maintain sterile conditions']
            })
        
        # Add a default experiment if none found
        if not experiments:
            experiments.append({
                'type': 'observation',
                'template': 'Observe and record changes in {specimen}',
                'equipment': ['Notebook', 'Magnifying Glass'],
                'safety': ['Follow basic lab safety']
            })
        
        return experiments

    def inject_science_data(self, template_path: str, game_data: Dict[str, Any], output_path: str):
        """Inject science game data into the Lua template."""
        # Read the template
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Prepare the experiments data in Lua format
        experiments_data = f"""
        [{game_data['experimentName']}] = {{
            name = "{game_data['displayName']}",
            difficulty = {game_data['difficulty']},
            equipment = {{{', '.join(f'"{e}"' for e in game_data['equipment'])}}},
            safetyLevel = "{game_data['safetyLevel']}",
            topics = {{{', '.join(f'"{t}"' for t in game_data['topics'])}}}
        }},"""
        
        # Prepare the experiment generators
        experiment_generators = []
        for experiment in game_data['experiments']:
            generator = f"""
    if topic == "{experiment['type']}" then
        return {{
            instructions = "{experiment['template']}",
            equipment = {{{', '.join(f'"{e}"' for e in experiment['equipment'])}}},
            safety = {{{', '.join(f'"{s}"' for s in experiment['safety'])}}},
            difficulty = {game_data['difficulty']}
        }}"""
            experiment_generators.append(generator)
        
        # Insert the experiments data
        template = template.replace(
            "-- [INJECT_EXPERIMENTS]",
            f"-- [INJECT_EXPERIMENTS]\n        {experiments_data}"
        )
        
        # Insert the experiment generators
        template = template.replace(
            "-- [INJECT_EXPERIMENT_GENERATOR]",
            f"-- [INJECT_EXPERIMENT_GENERATOR]\n{''.join(experiment_generators)}"
        )
        
        # Insert equipment setup
        equipment_setup = f"""
    if experimentType == "basic" then
        return {{
            required = {{{', '.join(f'"{e}"' for e in game_data['equipment'][:4])}}},
            optional = {{{', '.join(f'"{e}"' for e in game_data['equipment'][4:])}}}
        }}"""
        
        template = template.replace(
            "-- [INJECT_EQUIPMENT_SETUP]",
            f"-- [INJECT_EQUIPMENT_SETUP]\n{equipment_setup}"
        )
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write the modified template
        with open(output_path, 'w') as f:
            f.write(template)

    def validate_template(self, template_path: str, subject: str) -> bool:
        """Validate that a template contains all required injection points."""
        try:
            with open(template_path, 'r') as f:
                content = f.read()
            
            # Get required injection points for this subject
            subject_config = self.subject_configs.get(subject.lower())
            if not subject_config:
                raise ValueError(f"Unsupported subject: {subject}")
            
            # Check each required injection point
            for point_name, point_marker in subject_config["injection_points"].items():
                if point_marker not in content:
                    raise ValueError(f"Missing required injection point '{point_name}' in template {template_path}")
            
            # Basic Lua syntax validation
            self._validate_lua_syntax(content)
            
            return True
        except Exception as e:
            raise ValueError(f"Template validation failed for {template_path}: {str(e)}")

    def validate_generated_script(self, script_content: str, subject: str) -> bool:
        """Validate that a generated script has all injection points filled and is syntactically correct."""
        subject_config = self.subject_configs.get(subject.lower())
        if not subject_config:
            raise ValueError(f"Unsupported subject: {subject}")
        
        # Check for any remaining injection point markers
        for point_marker in subject_config["injection_points"].values():
            if point_marker in script_content:
                raise ValueError(f"Unfilled injection point found: {point_marker}")
        
        # Basic Lua syntax validation
        try:
            self._validate_lua_syntax(script_content)
            return True
        except Exception as e:
            raise ValueError(f"Lua syntax validation failed: {str(e)}")

    def _validate_lua_syntax(self, content: str) -> bool:
        """Basic Lua syntax validation."""
        # Check for matching curly braces
        if content.count('{') != content.count('}'):
            raise ValueError("Mismatched curly braces in Lua script")
        
        # Check for matching parentheses
        if content.count('(') != content.count(')'):
            raise ValueError("Mismatched parentheses in Lua script")
        
        # Check for common Lua syntax patterns
        patterns = {
            'function_def': r'function\s+\w+[:\.]?\w*\s*\([^)]*\)',
            'table_def': r'local\s+\w+\s*=\s*{',
            'if_statement': r'if\s+.+\s+then',
            'end_statement': r'end(?:\s*$|\s+\w+)',
            'assignment': r'\w+\s*=\s*.+'
        }
        
        # Count opening and closing patterns
        function_count = len(re.findall(patterns['function_def'], content))
        end_count = len(re.findall(patterns['end_statement'], content))
        if_count = len(re.findall(patterns['if_statement'], content))
        
        # Only validate end statements for complete files
        if not any(marker in content for marker in self.subject_configs["mathematics"]["injection_points"].values()) and \
           not any(marker in content for marker in self.subject_configs["science"]["injection_points"].values()):
            if function_count > end_count:
                raise ValueError("Missing 'end' statement for function definition")
            if if_count > end_count - function_count:
                raise ValueError("Missing 'end' statement for if block")
        
        return True

    def transform_and_inject(self, subject: str, content: str, lua_script: str) -> str:
        """Main method to transform content and inject into template."""
        subject_lower = subject.lower()
        subject_config = self.subject_configs.get(subject_lower)
        
        if not subject_config:
            raise ValueError(f"Subject {subject} not yet implemented")
        
        # Get template path
        template_path = os.path.join(self.template_dir, subject.capitalize(), subject_config["template_file"])
        
        # Validate template
        self.validate_template(template_path, subject_lower)
        
        # Generate output path
        clean_title = re.sub(r'[^a-zA-Z0-9]+', '_', content.lower()).strip('_')
        output_path = os.path.join(self.output_dir, subject.capitalize(), f"{clean_title}.lua")
        
        # Transform and inject the data
        transform_method = getattr(self, f"transform_{subject_lower}_content")
        game_data = transform_method(content, lua_script)
        
        inject_method = getattr(self, f"inject_{subject_lower}_data")
        inject_method(template_path, game_data, output_path)
        
        # Validate generated script
        with open(output_path, 'r') as f:
            generated_content = f.read()
        self.validate_generated_script(generated_content, subject_lower)
        
        return output_path

# Example usage:
if __name__ == "__main__":
    transformer = GameDataTransformer()
    # Test with input files
    math_file = "games_input/Mathematics/example_addition.txt"
    science_file = "games_input/Science/example_microscopy.txt"
    
    try:
        print("Generating Mathematics game...")
        math_output = transformer.transform_from_file("Mathematics", math_file)
        print(f"Generated mathematics game at: {math_output}")
        
        print("\nGenerating Science game...")
        science_output = transformer.transform_from_file("Science", science_file)
        print(f"Generated science game at: {science_output}")
    except Exception as e:
        print(f"Error: {str(e)}") 