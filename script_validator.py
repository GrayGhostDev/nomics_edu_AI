import re
import ast
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import luaparser
from luaparser import ast as lua_ast
from luaparser import astnodes

@dataclass
class ValidationError:
    """Represents a validation error"""
    error_type: str  # 'syntax', 'content', 'structure', 'grade_level', 'safety'
    message: str
    line_number: Optional[int] = None
    severity: str = "error"  # 'error', 'warning', 'info'
    
@dataclass
class ValidationResult:
    """Result of script validation"""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    info: List[ValidationError]
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
        
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
        
    def add_error(self, error: ValidationError):
        if error.severity == "error":
            self.errors.append(error)
        elif error.severity == "warning":
            self.warnings.append(error)
        else:
            self.info.append(error)
            
    def __str__(self) -> str:
        result = []
        if self.errors:
            result.append("Errors:")
            for error in self.errors:
                line_info = f" (line {error.line_number})" if error.line_number else ""
                result.append(f"  - [{error.error_type}]{line_info}: {error.message}")
        if self.warnings:
            result.append("Warnings:")
            for warning in self.warnings:
                line_info = f" (line {warning.line_number})" if warning.line_number else ""
                result.append(f"  - [{warning.error_type}]{line_info}: {warning.message}")
        if self.info:
            result.append("Info:")
            for info in self.info:
                line_info = f" (line {info.line_number})" if info.line_number else ""
                result.append(f"  - [{info.error_type}]{line_info}: {info.message}")
        return "\n".join(result)

class ScriptValidator:
    def __init__(self):
        self.grade_level_keywords = self._load_grade_level_keywords()
        self.subject_validators = {
            "Mathematics": self._validate_math_script,
            "Science": self._validate_science_script,
            "History": self._validate_history_script,
            "LanguageArts": self._validate_language_arts_script
        }
        
    def _load_grade_level_keywords(self) -> Dict[str, List[str]]:
        """Load grade-level appropriate keywords and concepts"""
        return {
            "elementary": [
                "basic", "simple", "fun", "game", "play", "learn",
                "easy", "beginner", "start", "help"
            ],
            "middle": [
                "intermediate", "challenge", "explore", "discover",
                "investigate", "analyze", "practice"
            ],
            "high": [
                "advanced", "complex", "theoretical", "abstract",
                "research", "evaluate", "synthesize"
            ]
        }
        
    def validate_script(self, script: str, subject: str, grade_level: int,
                       difficulty: int) -> ValidationResult:
        """Validate a generated Lua script"""
        result = ValidationResult(True, [], [], [])
        
        # Basic validation
        if not script or not script.strip():
            result.add_error(ValidationError(
                "content", "Script is empty", None, "error"
            ))
            result.is_valid = False
            return result
            
        # Syntax validation
        syntax_result = self._validate_syntax(script)
        if not syntax_result.is_valid:
            result.errors.extend(syntax_result.errors)
            result.is_valid = False
            return result
            
        # Structure validation
        structure_result = self._validate_structure(script)
        if not structure_result.is_valid:
            result.errors.extend(structure_result.errors)
            result.warnings.extend(structure_result.warnings)
            result.is_valid = False
            
        # Grade level appropriateness
        grade_result = self._validate_grade_level(script, grade_level)
        if not grade_result.is_valid:
            result.warnings.extend(grade_result.warnings)
            
        # Difficulty appropriateness
        difficulty_result = self._validate_difficulty(script, difficulty)
        if not difficulty_result.is_valid:
            result.warnings.extend(difficulty_result.warnings)
            
        # Subject-specific validation
        if subject in self.subject_validators:
            subject_result = self.subject_validators[subject](script)
            if not subject_result.is_valid:
                result.errors.extend(subject_result.errors)
                result.warnings.extend(subject_result.warnings)
                result.is_valid = False
                
        # Safety validation
        safety_result = self._validate_safety(script)
        if not safety_result.is_valid:
            result.errors.extend(safety_result.errors)
            result.is_valid = False
            
        return result
        
    def _validate_syntax(self, script: str) -> ValidationResult:
        """Validate Lua syntax"""
        result = ValidationResult(True, [], [], [])
        try:
            tree = luaparser.ast.parse(script)
            
            # Check for common syntax issues
            visitor = SyntaxErrorVisitor()
            visitor.visit(tree)
            
            if visitor.errors:
                result.errors.extend(visitor.errors)
                result.is_valid = False
                
        except Exception as e:
            result.add_error(ValidationError(
                "syntax", f"Syntax error: {str(e)}", None, "error"
            ))
            result.is_valid = False
            
        return result
        
    def _validate_structure(self, script: str) -> ValidationResult:
        """Validate script structure"""
        result = ValidationResult(True, [], [], [])
        
        # Check for required Lua elements
        required_elements = {
            "function": "Missing function definitions",
            "local": "Missing local variable declarations",
            "end": "Missing block endings",
            "return": "Missing return statements"
        }
        
        for element, message in required_elements.items():
            if element not in script:
                result.add_error(ValidationError(
                    "structure", message, None, "error"
                ))
                result.is_valid = False
                
        # Check for proper initialization
        if "function init()" not in script and "function start()" not in script:
            result.add_error(ValidationError(
                "structure", "Missing initialization function (init or start)",
                None, "error"
            ))
            result.is_valid = False
            
        return result
        
    def _validate_grade_level(self, script: str, grade_level: int) -> ValidationResult:
        """Validate grade-level appropriateness"""
        result = ValidationResult(True, [], [], [])
        
        # Determine grade category
        if grade_level <= 5:
            category = "elementary"
        elif grade_level <= 8:
            category = "middle"
        else:
            category = "high"
            
        # Check for grade-appropriate keywords
        appropriate_keywords = self.grade_level_keywords[category]
        found_keywords = sum(1 for keyword in appropriate_keywords if keyword in script.lower())
        
        if found_keywords < 3:
            result.add_error(ValidationError(
                "grade_level",
                f"Script may not be appropriate for grade {grade_level}. "
                f"Expected more grade-appropriate content.",
                None, "warning"
            ))
            result.is_valid = False
            
        # Check for inappropriate content
        if category == "elementary":
            complex_keywords = self.grade_level_keywords["high"]
            for keyword in complex_keywords:
                if keyword in script.lower():
                    result.add_error(ValidationError(
                        "grade_level",
                        f"Found complex concept '{keyword}' in elementary-level script",
                        None, "warning"
                    ))
                    result.is_valid = False
                    
        return result
        
    def _validate_difficulty(self, script: str, difficulty: int) -> ValidationResult:
        """Validate difficulty level appropriateness"""
        result = ValidationResult(True, [], [], [])
        
        # Check for difficulty-appropriate features
        if difficulty == 1:  # Easy
            if "while" in script or "for" in script:
                result.add_error(ValidationError(
                    "difficulty",
                    "Easy difficulty should avoid complex loops",
                    None, "warning"
                ))
                result.is_valid = False
        elif difficulty == 3:  # Hard
            if "while" not in script and "for" not in script:
                result.add_error(ValidationError(
                    "difficulty",
                    "Hard difficulty should include more complex logic",
                    None, "warning"
                ))
                result.is_valid = False
                
        return result
        
    def _validate_math_script(self, script: str) -> ValidationResult:
        """Validate mathematics-specific elements"""
        result = ValidationResult(True, [], [], [])
        
        required_elements = {
            "generateProblem": "Missing problem generation function",
            "checkAnswer": "Missing answer validation function",
            "difficulty": "Missing difficulty handling"
        }
        
        for element, message in required_elements.items():
            if element not in script:
                result.add_error(ValidationError(
                    "subject", message, None, "error"
                ))
                result.is_valid = False
                
        return result
        
    def _validate_science_script(self, script: str) -> ValidationResult:
        """Validate science-specific elements"""
        result = ValidationResult(True, [], [], [])
        
        required_elements = {
            "setupExperiment": "Missing experiment setup function",
            "checkResults": "Missing results validation",
            "safetyChecks": "Missing safety checks"
        }
        
        for element, message in required_elements.items():
            if element not in script:
                result.add_error(ValidationError(
                    "subject", message, None, "error"
                ))
                result.is_valid = False
                
        return result
        
    def _validate_history_script(self, script: str) -> ValidationResult:
        """Validate history-specific elements"""
        result = ValidationResult(True, [], [], [])
        
        required_elements = {
            "loadHistoricalData": "Missing historical data loading",
            "displayTimeline": "Missing timeline display",
            "checkHistoricalAccuracy": "Missing historical accuracy checks"
        }
        
        for element, message in required_elements.items():
            if element not in script:
                result.add_error(ValidationError(
                    "subject", message, None, "error"
                ))
                result.is_valid = False
                
        return result
        
    def _validate_language_arts_script(self, script: str) -> ValidationResult:
        """Validate language arts-specific elements"""
        result = ValidationResult(True, [], [], [])
        
        required_elements = {
            "processText": "Missing text processing function",
            "checkGrammar": "Missing grammar checking",
            "vocabularyCheck": "Missing vocabulary validation"
        }
        
        for element, message in required_elements.items():
            if element not in script:
                result.add_error(ValidationError(
                    "subject", message, None, "error"
                ))
                result.is_valid = False
                
        return result
        
    def _validate_safety(self, script: str) -> ValidationResult:
        """Validate script safety"""
        result = ValidationResult(True, [], [], [])
        
        # Check for potentially dangerous functions
        dangerous_patterns = [
            (r"os\.", "Operating system access"),
            (r"io\.", "File system access"),
            (r"require\s*\(", "External module loading"),
            (r"loadfile\s*\(", "File loading"),
            (r"dofile\s*\(", "File execution")
        ]
        
        for pattern, description in dangerous_patterns:
            matches = re.finditer(pattern, script)
            for match in matches:
                result.add_error(ValidationError(
                    "safety",
                    f"Potentially unsafe operation: {description}",
                    None, "error"
                ))
                result.is_valid = False
                
        return result

class SyntaxErrorVisitor(lua_ast.ASTVisitor):
    """Visit AST nodes to find syntax errors"""
    def __init__(self):
        self.errors = []
        
    def visit_Name(self, node):
        # Check for common naming issues
        if len(node.id) < 2:
            self.errors.append(ValidationError(
                "syntax",
                f"Variable name '{node.id}' is too short",
                node.lineno, "warning"
            ))
            
    def visit_Call(self, node):
        # Check for function call issues
        if isinstance(node.func, lua_ast.Name):
            if node.func.id.startswith('_'):
                self.errors.append(ValidationError(
                    "syntax",
                    f"Calling private function '{node.func.id}'",
                    node.lineno, "warning"
                ))
                
    def visit_Function(self, node):
        # Check function definition issues
        if not hasattr(node, 'name') or not node.name:
            self.errors.append(ValidationError(
                "syntax",
                "Anonymous function found",
                node.lineno, "warning"
            ))
            
    def generic_visit(self, node):
        super().generic_visit(node) 