from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import os
from enum import Enum

class GenerationStage(Enum):
    """Stages of game generation"""
    INITIALIZING = "initializing"
    TEMPLATE_SELECTION = "template_selection"
    SCRIPT_GENERATION = "script_generation"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    SAVING = "saving"
    COMPLETED = "completed"
    FAILED = "failed"

class GenerationStatus(Enum):
    """Status of each generation stage"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class StageProgress:
    """Progress information for a generation stage"""
    stage: GenerationStage
    status: GenerationStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    details: Optional[str] = None
    error: Optional[str] = None
    
    @property
    def duration(self) -> Optional[float]:
        """Get stage duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

@dataclass
class GenerationProgress:
    """Overall progress of game generation"""
    request_id: str
    teacher_id: str
    subject: str
    topic: str
    start_time: datetime
    stages: Dict[GenerationStage, StageProgress]
    current_stage: GenerationStage
    end_time: Optional[datetime] = None
    
    @property
    def is_completed(self) -> bool:
        """Check if generation is completed"""
        return all(stage.status in [GenerationStatus.COMPLETED, GenerationStatus.SKIPPED]
                  for stage in self.stages.values())
    
    @property
    def is_failed(self) -> bool:
        """Check if generation failed"""
        return any(stage.status == GenerationStatus.FAILED
                  for stage in self.stages.values())
    
    @property
    def duration(self) -> Optional[float]:
        """Get total duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def progress_percentage(self) -> float:
        """Calculate overall progress percentage"""
        total_stages = len(self.stages)
        if total_stages == 0:
            return 0.0
            
        completed_stages = sum(
            1 for stage in self.stages.values()
            if stage.status in [GenerationStatus.COMPLETED, GenerationStatus.SKIPPED]
        )
        
        current_stage_progress = 0.0
        if (self.current_stage != GenerationStage.COMPLETED and
            self.current_stage != GenerationStage.FAILED):
            current_stage = self.stages.get(self.current_stage)
            if current_stage and current_stage.status == GenerationStatus.IN_PROGRESS:
                current_stage_progress = 0.5
                
        return (completed_stages + current_stage_progress) / total_stages * 100

class ProgressTracker:
    def __init__(self, log_dir: str = "generation_logs"):
        """Initialize progress tracker"""
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.active_generations: Dict[str, GenerationProgress] = {}
        
    def start_generation(self, request_id: str, teacher_id: str,
                        subject: str, topic: str) -> GenerationProgress:
        """Start tracking a new generation"""
        progress = GenerationProgress(
            request_id=request_id,
            teacher_id=teacher_id,
            subject=subject,
            topic=topic,
            start_time=datetime.now(),
            stages={
                GenerationStage.INITIALIZING: StageProgress(
                    GenerationStage.INITIALIZING, GenerationStatus.PENDING
                ),
                GenerationStage.TEMPLATE_SELECTION: StageProgress(
                    GenerationStage.TEMPLATE_SELECTION, GenerationStatus.PENDING
                ),
                GenerationStage.SCRIPT_GENERATION: StageProgress(
                    GenerationStage.SCRIPT_GENERATION, GenerationStatus.PENDING
                ),
                GenerationStage.VALIDATION: StageProgress(
                    GenerationStage.VALIDATION, GenerationStatus.PENDING
                ),
                GenerationStage.TRANSFORMATION: StageProgress(
                    GenerationStage.TRANSFORMATION, GenerationStatus.PENDING
                ),
                GenerationStage.SAVING: StageProgress(
                    GenerationStage.SAVING, GenerationStatus.PENDING
                )
            },
            current_stage=GenerationStage.INITIALIZING
        )
        
        self.active_generations[request_id] = progress
        self._save_progress(progress)
        return progress
    
    def start_stage(self, request_id: str, stage: GenerationStage,
                   details: Optional[str] = None) -> None:
        """Start a generation stage"""
        progress = self.active_generations.get(request_id)
        if not progress:
            raise ValueError(f"No active generation found for request {request_id}")
            
        stage_progress = progress.stages.get(stage)
        if not stage_progress:
            raise ValueError(f"Invalid stage {stage} for request {request_id}")
            
        stage_progress.status = GenerationStatus.IN_PROGRESS
        stage_progress.start_time = datetime.now()
        stage_progress.details = details
        progress.current_stage = stage
        
        self._save_progress(progress)
        self._log_progress(progress, f"Started {stage.value}")
    
    def complete_stage(self, request_id: str, stage: GenerationStage,
                      details: Optional[str] = None) -> None:
        """Complete a generation stage"""
        progress = self.active_generations.get(request_id)
        if not progress:
            raise ValueError(f"No active generation found for request {request_id}")
            
        stage_progress = progress.stages.get(stage)
        if not stage_progress:
            raise ValueError(f"Invalid stage {stage} for request {request_id}")
            
        stage_progress.status = GenerationStatus.COMPLETED
        stage_progress.end_time = datetime.now()
        if details:
            stage_progress.details = details
            
        self._save_progress(progress)
        self._log_progress(progress, f"Completed {stage.value}")
    
    def fail_stage(self, request_id: str, stage: GenerationStage,
                   error: str) -> None:
        """Mark a generation stage as failed"""
        progress = self.active_generations.get(request_id)
        if not progress:
            raise ValueError(f"No active generation found for request {request_id}")
            
        stage_progress = progress.stages.get(stage)
        if not stage_progress:
            raise ValueError(f"Invalid stage {stage} for request {request_id}")
            
        stage_progress.status = GenerationStatus.FAILED
        stage_progress.end_time = datetime.now()
        stage_progress.error = error
        progress.current_stage = GenerationStage.FAILED
        
        self._save_progress(progress)
        self._log_progress(progress, f"Failed {stage.value}: {error}")
    
    def skip_stage(self, request_id: str, stage: GenerationStage,
                  reason: Optional[str] = None) -> None:
        """Skip a generation stage"""
        progress = self.active_generations.get(request_id)
        if not progress:
            raise ValueError(f"No active generation found for request {request_id}")
            
        stage_progress = progress.stages.get(stage)
        if not stage_progress:
            raise ValueError(f"Invalid stage {stage} for request {request_id}")
            
        stage_progress.status = GenerationStatus.SKIPPED
        stage_progress.details = reason
        
        self._save_progress(progress)
        self._log_progress(progress, f"Skipped {stage.value}")
    
    def complete_generation(self, request_id: str) -> None:
        """Mark generation as completed"""
        progress = self.active_generations.get(request_id)
        if not progress:
            raise ValueError(f"No active generation found for request {request_id}")
            
        progress.end_time = datetime.now()
        progress.current_stage = GenerationStage.COMPLETED
        
        self._save_progress(progress)
        self._log_progress(progress, "Generation completed")
        
        # Clean up
        del self.active_generations[request_id]
    
    def get_progress(self, request_id: str) -> Optional[GenerationProgress]:
        """Get progress for a generation request"""
        return self.active_generations.get(request_id)
    
    def _save_progress(self, progress: GenerationProgress) -> None:
        """Save progress to file"""
        progress_data = {
            "request_id": progress.request_id,
            "teacher_id": progress.teacher_id,
            "subject": progress.subject,
            "topic": progress.topic,
            "start_time": progress.start_time.isoformat(),
            "end_time": progress.end_time.isoformat() if progress.end_time else None,
            "current_stage": progress.current_stage.value,
            "stages": {
                stage.value: {
                    "status": stage_progress.status.value,
                    "start_time": stage_progress.start_time.isoformat() if stage_progress.start_time else None,
                    "end_time": stage_progress.end_time.isoformat() if stage_progress.end_time else None,
                    "details": stage_progress.details,
                    "error": stage_progress.error
                }
                for stage, stage_progress in progress.stages.items()
            }
        }
        
        file_path = os.path.join(self.log_dir, f"{progress.request_id}.json")
        with open(file_path, 'w') as f:
            json.dump(progress_data, f, indent=2)
    
    def _log_progress(self, progress: GenerationProgress, message: str) -> None:
        """Log progress message"""
        timestamp = datetime.now().isoformat()
        log_message = {
            "timestamp": timestamp,
            "request_id": progress.request_id,
            "message": message,
            "progress": progress.progress_percentage
        }
        
        log_file = os.path.join(self.log_dir, f"{progress.request_id}.log")
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_message) + "\n")
    
    def format_progress(self, progress: GenerationProgress) -> str:
        """Format progress for display"""
        lines = [
            f"Generation Progress for {progress.subject} - {progress.topic}",
            f"Request ID: {progress.request_id}",
            f"Progress: {progress.progress_percentage:.1f}%\n"
        ]
        
        for stage, stage_progress in progress.stages.items():
            status_symbol = {
                GenerationStatus.PENDING: "⏳",
                GenerationStatus.IN_PROGRESS: "🔄",
                GenerationStatus.COMPLETED: "✅",
                GenerationStatus.FAILED: "❌",
                GenerationStatus.SKIPPED: "⏭️"
            }.get(stage_progress.status, "❓")
            
            duration = ""
            if stage_progress.duration is not None:
                duration = f" ({stage_progress.duration:.1f}s)"
                
            error = f"\n  Error: {stage_progress.error}" if stage_progress.error else ""
            details = f"\n  Details: {stage_progress.details}" if stage_progress.details else ""
            
            lines.append(f"{status_symbol} {stage.value.title()}{duration}{error}{details}")
            
        if progress.duration is not None:
            lines.append(f"\nTotal Duration: {progress.duration:.1f}s")
            
        return "\n".join(lines) 