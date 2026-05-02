from enum import Enum
from typing import Optional
from pydantic import BaseModel

class ErrorType(Enum):
    ROUTING = "routing_error"
    GENERATION = "generation_error"
    CANON = "canon_error"
    DRIFT = "drift_error"
    SYSTEM = "system_error"

class PipelineStage(Enum):
    ROUTING = "routing"
    STRATEGY = "strategy"
    CANON = "canon"
    DRIFT = "drift"
    ORCHESTRATOR = "orchestrator"

class PipelineError(BaseModel):
    """Structured error response for the hybrid pipeline."""
    error: bool = True
    type: str
    message: str
    stage: str

class ErrorHandler:
    """Catches, classifies, and returns structured errors from any pipeline stage."""
    
    # Error classification patterns
    ERROR_PATTERNS = {
        ErrorType.ROUTING: [
            "route", "routing", "model selection", "classify", "task category"
        ],
        ErrorType.GENERATION: [
            "generate", "llm", "api_key", "rate limit", "timeout", "model", 
            "anthropic", "openai", "gemini", "emergent"
        ],
        ErrorType.CANON: [
            "canon", "normalize", "forbidden", "compliance", "clean"
        ],
        ErrorType.DRIFT: [
            "drift", "metrics", "baseline", "deviation", "monitor"
        ]
    }
    
    @classmethod
    def classify_error(cls, error: Exception, stage: PipelineStage = None) -> ErrorType:
        """Classify error type based on exception content and stage."""
        error_str = str(error).lower()
        
        # If stage is provided, use it for classification
        if stage:
            stage_map = {
                PipelineStage.ROUTING: ErrorType.ROUTING,
                PipelineStage.STRATEGY: ErrorType.GENERATION,
                PipelineStage.CANON: ErrorType.CANON,
                PipelineStage.DRIFT: ErrorType.DRIFT,
                PipelineStage.ORCHESTRATOR: ErrorType.SYSTEM
            }
            return stage_map.get(stage, ErrorType.SYSTEM)
        
        # Pattern-based classification
        for error_type, patterns in cls.ERROR_PATTERNS.items():
            for pattern in patterns:
                if pattern in error_str:
                    return error_type
        
        return ErrorType.SYSTEM
    
    @classmethod
    def handle(
        cls, 
        error: Exception, 
        stage: PipelineStage = None,
        message: Optional[str] = None
    ) -> PipelineError:
        """
        Handle an error and return structured response.
        
        Args:
            error: The exception that occurred
            stage: The pipeline stage where error occurred
            message: Optional custom error message
            
        Returns:
            PipelineError with structured error details
        """
        error_type = cls.classify_error(error, stage)
        
        # Generate concise message
        if message:
            error_message = message
        else:
            error_message = cls._generate_message(error, error_type)
        
        # Determine stage name
        stage_name = stage.value if stage else "orchestrator"
        
        return PipelineError(
            error=True,
            type=error_type.value,
            message=error_message,
            stage=stage_name
        )
    
    @classmethod
    def _generate_message(cls, error: Exception, error_type: ErrorType) -> str:
        """Generate a concise, operator-friendly error message."""
        error_str = str(error)
        
        # Truncate long messages
        if len(error_str) > 200:
            error_str = error_str[:200] + "..."
        
        # Add context based on error type
        prefixes = {
            ErrorType.ROUTING: "Routing failed",
            ErrorType.GENERATION: "Strategy generation failed",
            ErrorType.CANON: "Canon enforcement failed",
            ErrorType.DRIFT: "Drift monitoring failed",
            ErrorType.SYSTEM: "System error"
        }
        
        prefix = prefixes.get(error_type, "Error")
        return f"{prefix}: {error_str}"
    
    @classmethod
    def create_error(
        cls,
        error_type: ErrorType,
        stage: PipelineStage,
        message: str
    ) -> PipelineError:
        """Create a structured error directly without an exception."""
        return PipelineError(
            error=True,
            type=error_type.value,
            message=message,
            stage=stage.value
        )
    
    @classmethod
    def routing_error(cls, message: str) -> PipelineError:
        """Shorthand for routing errors."""
        return cls.create_error(ErrorType.ROUTING, PipelineStage.ROUTING, message)
    
    @classmethod
    def generation_error(cls, message: str) -> PipelineError:
        """Shorthand for generation errors."""
        return cls.create_error(ErrorType.GENERATION, PipelineStage.STRATEGY, message)
    
    @classmethod
    def canon_error(cls, message: str) -> PipelineError:
        """Shorthand for canon enforcement errors."""
        return cls.create_error(ErrorType.CANON, PipelineStage.CANON, message)
    
    @classmethod
    def drift_error(cls, message: str) -> PipelineError:
        """Shorthand for drift monitoring errors."""
        return cls.create_error(ErrorType.DRIFT, PipelineStage.DRIFT, message)
    
    @classmethod
    def system_error(cls, message: str) -> PipelineError:
        """Shorthand for system errors."""
        return cls.create_error(ErrorType.SYSTEM, PipelineStage.ORCHESTRATOR, message)
