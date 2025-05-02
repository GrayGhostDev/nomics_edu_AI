from typing import Dict, Any, Optional
import json
import os
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TeacherProfile:
    teacher_id: str
    name: str
    school: str
    grade_level: str
    subjects: list[str]
    preferred_teaching_style: Optional[str] = None
    
@dataclass
class GameRequest:
    subject: str
    topic: str
    learning_objectives: list[str]
    grade_level: str
    difficulty: int
    custom_content: Optional[str] = None
    game_type: Optional[str] = None
    time_limit: Optional[int] = None
    
class TeacherInputHandler:
    def __init__(self):
        self.games_input_dir = "games_input"
        self.supported_subjects = self._get_supported_subjects()
        
    def _get_supported_subjects(self) -> list[str]:
        """Get list of supported subjects from Games directory"""
        return [d for d in os.listdir("Games") 
                if os.path.isdir(os.path.join("Games", d))]
    
    def validate_subject(self, subject: str) -> bool:
        """Validate if subject is supported"""
        return subject in self.supported_subjects
    
    def process_manual_input(self, teacher: TeacherProfile, request: GameRequest) -> Dict[str, Any]:
        """Process manual form input from teacher"""
        if not self.validate_subject(request.subject):
            raise ValueError(f"Subject {request.subject} is not supported")
            
        # Create output directory if needed
        subject_dir = os.path.join(self.games_input_dir, request.subject)
        os.makedirs(subject_dir, exist_ok=True)
        
        # Prepare data for LLM
        game_data = {
            "teacher": {
                "id": teacher.teacher_id,
                "name": teacher.name,
                "school": teacher.school,
                "grade_level": teacher.grade_level,
                "teaching_style": teacher.preferred_teaching_style
            },
            "request": {
                "subject": request.subject,
                "topic": request.topic,
                "objectives": request.learning_objectives,
                "grade_level": request.grade_level,
                "difficulty": request.difficulty,
                "custom_content": request.custom_content,
                "game_type": request.game_type,
                "time_limit": request.time_limit
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Save request data
        filename = f"{teacher.teacher_id}_{request.subject}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(subject_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(game_data, f, indent=2)
            
        return game_data
    
    def process_lms_data(self, lms_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process uploaded LMS data"""
        # Extract teacher profile from LMS data
        teacher = TeacherProfile(
            teacher_id=lms_data.get('teacher_id'),
            name=lms_data.get('teacher_name'),
            school=lms_data.get('school'),
            grade_level=lms_data.get('grade_level'),
            subjects=lms_data.get('subjects', []),
            preferred_teaching_style=lms_data.get('teaching_style')
        )
        
        # Extract game request from LMS data
        request = GameRequest(
            subject=lms_data.get('subject'),
            topic=lms_data.get('topic'),
            learning_objectives=lms_data.get('objectives', []),
            grade_level=lms_data.get('grade_level'),
            difficulty=lms_data.get('difficulty', 1),
            custom_content=lms_data.get('custom_content'),
            game_type=lms_data.get('game_type'),
            time_limit=lms_data.get('time_limit')
        )
        
        return self.process_manual_input(teacher, request) 