"""
Authentication tokens and responses.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TokenPair(BaseModel):
    """Access and refresh token pair."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires


class TokenRefresh(BaseModel):
    """Schema for refreshing tokens."""
    refresh_token: str


class TokenResponse(BaseModel):
    """Token response with user info."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class AuthResponse(BaseModel):
    """Full authentication response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict
    current_team: Optional[dict] = None
