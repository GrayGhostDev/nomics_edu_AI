from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import os
import json
from datetime import datetime

@dataclass
class TemplateMetadata:
    """Metadata for a game template"""
    name: str
    version: str
    subject: str
    min_grade: int
    max_grade: int
    supported_difficulties: List[int]
    description: str
    last_updated: str
    author: str
    tags: List[str]
    dependencies: List[str]
    
@dataclass
class Template:
    """Game template with metadata and content"""
    metadata: TemplateMetadata
    content: str
    path: str

class TemplateManager:
    def __init__(self, templates_dir: str = "Games"):
        self.templates_dir = templates_dir
        self.templates: Dict[str, Template] = {}
        self.load_templates()
    
    def load_templates(self):
        """Load all templates from the templates directory"""
        for subject in os.listdir(self.templates_dir):
            subject_dir = os.path.join(self.templates_dir, subject)
            if not os.path.isdir(subject_dir):
                continue
                
            for template_file in os.listdir(subject_dir):
                if not template_file.endswith('.lua'):
                    continue
                    
                template_path = os.path.join(subject_dir, template_file)
                metadata_path = template_path.replace('.lua', '.json')
                
                try:
                    # Load template content
                    with open(template_path, 'r') as f:
                        content = f.read()
                        
                    # Load or create metadata
                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'r') as f:
                            metadata_dict = json.load(f)
                    else:
                        # Create default metadata
                        metadata_dict = {
                            "name": template_file[:-4],
                            "version": "1.0.0",
                            "subject": subject,
                            "min_grade": 1,
                            "max_grade": 12,
                            "supported_difficulties": [1, 2, 3],
                            "description": f"Default template for {subject}",
                            "last_updated": datetime.now().isoformat(),
                            "author": "System",
                            "tags": [subject.lower()],
                            "dependencies": []
                        }
                        # Save default metadata
                        with open(metadata_path, 'w') as f:
                            json.dump(metadata_dict, f, indent=2)
                    
                    metadata = TemplateMetadata(**metadata_dict)
                    template = Template(metadata=metadata, content=content, path=template_path)
                    self.templates[f"{subject}/{template_file}"] = template
                    
                except Exception as e:
                    print(f"Error loading template {template_path}: {str(e)}")
    
    def get_template(self, subject: str, name: str) -> Optional[Template]:
        """Get a template by subject and name"""
        key = f"{subject}/{name}.lua"
        return self.templates.get(key)
    
    def get_templates_for_subject(self, subject: str) -> List[Template]:
        """Get all templates for a subject"""
        return [t for k, t in self.templates.items() if k.startswith(f"{subject}/")]
    
    def get_compatible_templates(self, subject: str, grade_level: int, difficulty: int) -> List[Template]:
        """Get templates compatible with grade level and difficulty"""
        return [
            t for t in self.get_templates_for_subject(subject)
            if (t.metadata.min_grade <= grade_level <= t.metadata.max_grade and
                difficulty in t.metadata.supported_difficulties)
        ]
    
    def update_template_metadata(self, subject: str, name: str, metadata_updates: Dict[str, Any]) -> bool:
        """Update template metadata"""
        template = self.get_template(subject, name)
        if not template:
            return False
            
        # Update metadata
        metadata_dict = {
            "name": template.metadata.name,
            "version": template.metadata.version,
            "subject": template.metadata.subject,
            "min_grade": template.metadata.min_grade,
            "max_grade": template.metadata.max_grade,
            "supported_difficulties": template.metadata.supported_difficulties,
            "description": template.metadata.description,
            "last_updated": datetime.now().isoformat(),
            "author": template.metadata.author,
            "tags": template.metadata.tags,
            "dependencies": template.metadata.dependencies
        }
        metadata_dict.update(metadata_updates)
        
        # Save updated metadata
        metadata_path = template.path.replace('.lua', '.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata_dict, f, indent=2)
            
        # Reload template
        self.load_templates()
        return True 