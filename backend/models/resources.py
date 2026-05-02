"""
Team-scoped resource models: Pipelines and Execution Logs.
All resources are scoped to a team for multi-tenant isolation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from bson import ObjectId


# Pipeline models
class PipelineStep(BaseModel):
    """A single step in a pipeline."""
    engine: str
    config: Dict[str, Any] = {}
    order: int


class PipelineCreate(BaseModel):
    """Schema for creating a pipeline."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    steps: List[PipelineStep] = []
    is_template: bool = False


class PipelineUpdate(BaseModel):
    """Schema for updating a pipeline."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    steps: Optional[List[PipelineStep]] = None
    is_template: Optional[bool] = None


class PipelineInDB(BaseModel):
    """Pipeline as stored in database."""
    id: str = Field(alias="_id")
    team_id: str
    created_by: str
    name: str
    description: Optional[str] = None
    steps: List[PipelineStep] = []
    is_template: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    last_executed_at: Optional[datetime] = None
    execution_count: int = 0
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class PipelineResponse(BaseModel):
    """Pipeline response."""
    id: str
    team_id: str
    created_by: str
    created_by_name: Optional[str] = None
    name: str
    description: Optional[str] = None
    steps: List[PipelineStep] = []
    is_template: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_executed_at: Optional[datetime] = None
    execution_count: int = 0


# Execution log models
ExecutionStatus = Literal["pending", "running", "success", "error", "cancelled"]


class ExecutionLogCreate(BaseModel):
    """Schema for creating an execution log."""
    team_id: str
    user_id: str
    engine: str
    pipeline_id: Optional[str] = None
    input_data: Dict[str, Any] = {}
    source: str = "direct"  # direct, pipeline, api


class ExecutionLogInDB(BaseModel):
    """Execution log as stored in database."""
    id: str = Field(alias="_id")
    team_id: str
    user_id: str
    engine: str
    pipeline_id: Optional[str] = None
    input_data: Dict[str, Any] = {}
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    status: ExecutionStatus = "pending"
    source: str = "direct"
    duration_ms: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class ExecutionLogResponse(BaseModel):
    """Execution log response."""
    id: str
    team_id: str
    user_id: str
    user_email: Optional[str] = None
    engine: str
    pipeline_id: Optional[str] = None
    pipeline_name: Optional[str] = None
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    error_message: Optional[str] = None
    status: ExecutionStatus
    source: str
    duration_ms: int
    created_at: datetime
    completed_at: Optional[datetime] = None


class ExecutionLogQuery(BaseModel):
    """Query parameters for execution logs."""
    engine: Optional[str] = None
    pipeline_id: Optional[str] = None
    status: Optional[ExecutionStatus] = None
    source: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
