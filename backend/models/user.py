"""
User model and schemas for authentication.
Supports email/password auth with future OAuth provider support.
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List, Literal
from datetime import datetime
from bson import ObjectId
import re


class PyObjectId(str):
    """Custom ObjectId type for Pydantic."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")


# Enums
SystemRole = Literal["admin", "user"]


class OAuthProvider(BaseModel):
    """OAuth provider connection for future OAuth support."""
    provider: Literal["google", "github", "microsoft"]
    provider_id: str
    email: Optional[str] = None
    connected_at: datetime = Field(default_factory=lambda: datetime.utcnow())


class UserBase(BaseModel):
    """Base user fields."""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)


class UserInDB(UserBase):
    """User as stored in database."""
    id: str = Field(alias="_id")
    password_hash: str
    system_role: SystemRole = "user"
    oauth_providers: List[OAuthProvider] = []
    email_verified: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class UserResponse(BaseModel):
    """User response (public fields only)."""
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    system_role: SystemRole
    email_verified: bool
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    has_oauth: bool = False
    
    class Config:
        from_attributes = True


class UserWithTeams(UserResponse):
    """User response with team memberships."""
    teams: List[dict] = []
    current_team_id: Optional[str] = None


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class ChangePassword(BaseModel):
    """Schema for changing password."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v
