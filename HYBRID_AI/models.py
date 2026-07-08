from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    session_id: Optional[str] = None
    task_type: Optional[str] = None


class ChatResponse(BaseModel):
    content: str
    model: str = "gemma-4-26b-a4b"
    provider: str = "local"
    usage: Dict[str, int] = Field(default_factory=lambda: {"prompt_tokens": 0, "completion_tokens": 0})
    finish_reason: str = "stop"


class EngineTask(BaseModel):
    task_id: str
    engine: str
    model: str = "gemma-4-26b-a4b"
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GenerationConfig(BaseModel):
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 40
    max_tokens: int = 4096
    repeat_penalty: float = 1.1
    stop: List[str] = Field(default_factory=list)
