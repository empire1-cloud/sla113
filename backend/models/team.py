"""
Team and membership models for multi-tenant architecture.
Supports multiple teams per user with role-based access.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime
from bson import ObjectId
import re


# Enums
TeamType = Literal["personal", "organization"]
TeamRole = Literal["owner", "admin", "member", "viewer"]


class TeamBase(BaseModel):
    """Base team fields."""
    name: str = Field(..., min_length=1, max_length=100)


class TeamCreate(TeamBase):
    """Schema for creating a new team."""
    type: TeamType = "organization"
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) < 1:
            raise ValueError("Team name cannot be empty")
        return v.strip()


class TeamUpdate(BaseModel):
    """Schema for updating team."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class TeamSettings(BaseModel):
    """Team settings and preferences."""
    allow_member_invites: bool = False
    default_member_role: TeamRole = "member"
    require_2fa: bool = False


class TeamInDB(TeamBase):
    """Team as stored in database."""
    id: str = Field(alias="_id")
    slug: str
    type: TeamType
    owner_id: str
    settings: TeamSettings = TeamSettings()
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class TeamResponse(BaseModel):
    """Team response (public fields)."""
    id: str
    name: str
    slug: str
    type: TeamType
    owner_id: str
    is_active: bool
    created_at: datetime
    member_count: int = 0
    
    class Config:
        from_attributes = True


class TeamWithRole(TeamResponse):
    """Team response with user's role."""
    role: TeamRole
    joined_at: Optional[datetime] = None


# Membership models
class MembershipBase(BaseModel):
    """Base membership fields."""
    role: TeamRole = "member"


class MembershipCreate(MembershipBase):
    """Schema for creating membership (internal use)."""
    user_id: str
    team_id: str
    invited_by: Optional[str] = None


class MembershipInDB(MembershipBase):
    """Membership as stored in database."""
    id: str = Field(alias="_id")
    user_id: str
    team_id: str
    invited_by: Optional[str] = None
    invited_at: Optional[datetime] = None
    joined_at: datetime
    is_active: bool = True
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class TeamMemberResponse(BaseModel):
    """Team member with user details."""
    id: str
    user_id: str
    email: str
    first_name: str
    last_name: str
    role: TeamRole
    joined_at: datetime
    is_active: bool


class UpdateMemberRole(BaseModel):
    """Schema for updating member role."""
    role: TeamRole
    
    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v == "owner":
            raise ValueError("Cannot set role to owner directly. Use transfer ownership.")
        return v


# Invite models
class InviteCreate(BaseModel):
    """Schema for creating team invite."""
    email: str = Field(..., pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    role: TeamRole = "member"
    
    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v == "owner":
            raise ValueError("Cannot invite as owner")
        return v


class InviteInDB(BaseModel):
    """Invite as stored in database."""
    id: str = Field(alias="_id")
    team_id: str
    email: str
    role: TeamRole
    token_hash: str
    invited_by: str
    created_at: datetime
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class InviteResponse(BaseModel):
    """Invite response (public fields)."""
    id: str
    team_id: str
    team_name: str
    email: str
    role: TeamRole
    invited_by_name: str
    created_at: datetime
    expires_at: datetime
    is_active: bool


class AcceptInvite(BaseModel):
    """Schema for accepting invite."""
    token: str
