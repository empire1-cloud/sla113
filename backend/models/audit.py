"""
Audit log model for tracking all user and system actions.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime
from bson import ObjectId


# Audit action categories
AuditAction = Literal[
    # Auth actions
    "auth.signup",
    "auth.login",
    "auth.logout",
    "auth.password_change",
    "auth.password_reset",
    "auth.token_refresh",
    
    # User actions
    "user.update",
    "user.deactivate",
    "user.reactivate",
    
    # Team actions
    "team.create",
    "team.update",
    "team.delete",
    "team.switch",
    
    # Membership actions
    "membership.invite_sent",
    "membership.invite_accepted",
    "membership.invite_revoked",
    "membership.role_changed",
    "membership.removed",
    "membership.left",
    
    # Pipeline actions
    "pipeline.create",
    "pipeline.update",
    "pipeline.delete",
    "pipeline.execute",
    
    # Engine actions
    "engine.execute",
    "engine.configure",
    
    # Admin actions
    "admin.user_role_change",
    "admin.user_deactivate",
    "admin.system_config",
]


class AuditLogCreate(BaseModel):
    """Schema for creating an audit log entry."""
    user_id: str
    team_id: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogInDB(BaseModel):
    """Audit log as stored in database."""
    id: str = Field(alias="_id")
    user_id: str
    team_id: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class AuditLogResponse(BaseModel):
    """Audit log response."""
    id: str
    user_id: str
    user_email: Optional[str] = None
    team_id: Optional[str] = None
    team_name: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    created_at: datetime


class AuditLogQuery(BaseModel):
    """Query parameters for audit logs."""
    user_id: Optional[str] = None
    team_id: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
