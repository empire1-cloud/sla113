"""
Session model for JWT refresh token management.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class SessionCreate(BaseModel):
    """Schema for creating a session."""
    user_id: str
    refresh_token_hash: str
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class SessionInDB(BaseModel):
    """Session as stored in database."""
    id: str = Field(alias="_id")
    user_id: str
    refresh_token_hash: str
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    last_used_at: datetime
    revoked_at: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class SessionResponse(BaseModel):
    """Session response (public fields)."""
    id: str
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    last_used_at: datetime
    is_current: bool = False
