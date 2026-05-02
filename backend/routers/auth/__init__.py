"""
Authentication API routes.
Handles signup, login, token refresh, logout, password management, and OAuth.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

from models import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserWithTeams,
    TokenRefresh,
    AuthResponse,
    ChangePassword,
)
from services.auth_service import (
    register_user,
    login_user,
    refresh_tokens,
    logout_user,
    get_user_with_teams,
    AuthError,
)
from services.password_reset_service import (
    request_password_reset,
    validate_reset_token,
    confirm_password_reset,
    PasswordResetError,
)
from services.oauth_service import (
    get_authorization_url,
    handle_oauth_callback,
    generate_oauth_state,
    is_oauth_configured,
    OAuthError,
)
from core.dependencies import get_current_user, get_client_info
from core.security import hash_password, verify_password, get_token_expiry_seconds
from database import users_collection
from services.audit_service import create_audit_log


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse)
async def signup(user_data: UserCreate, request: Request):
    """
    Register a new user account.
    
    - Creates user with hashed password
    - Creates personal team automatically
    - Returns access and refresh tokens
    """
    try:
        client_info = await get_client_info(request)
        result = await register_user(
            user_data,
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent"),
        )
        return result
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin, request: Request):
    """
    Authenticate with email and password.
    
    Returns access token (15 min) and refresh token (7 days).
    """
    try:
        client_info = await get_client_info(request)
        result = await login_user(
            credentials,
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent"),
        )
        return result
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/refresh")
async def refresh(token_data: TokenRefresh, request: Request):
    """
    Refresh access token using refresh token.
    
    Returns new access and refresh token pair.
    Old refresh token is invalidated.
    """
    try:
        client_info = await get_client_info(request)
        access_token, refresh_token = await refresh_tokens(
            token_data.refresh_token,
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent"),
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": get_token_expiry_seconds(),
        }
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/logout")
async def logout(
    request: Request,
    logout_all: bool = False,
    refresh_token: Optional[str] = None,
    user: dict = Depends(get_current_user),
):
    """
    Logout user and revoke session(s).
    
    - If refresh_token provided, revokes that specific session
    - If logout_all is True, revokes all user sessions
    """
    client_info = await get_client_info(request)
    await logout_user(
        user_id=user["_id"],
        refresh_token=refresh_token,
        logout_all=logout_all,
        ip_address=client_info.get("ip_address"),
        user_agent=client_info.get("user_agent"),
    )
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserWithTeams)
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """
    Get current authenticated user's info with team memberships.
    """
    try:
        return await get_user_with_teams(user["_id"])
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/password")
async def change_password(
    password_data: ChangePassword,
    request: Request,
    user: dict = Depends(get_current_user),
):
    """
    Change current user's password.
    
    Requires current password for verification.
    """
    # Verify current password
    if not verify_password(password_data.current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password
    new_hash = hash_password(password_data.new_password)
    await users_collection().update_one(
        {"_id": user["_id"]},
        {"$set": {"password_hash": new_hash}}
    )
    
    # Audit log
    client_info = await get_client_info(request)
    await create_audit_log(
        user_id=user["_id"],
        action="auth.password_change",
        ip_address=client_info.get("ip_address"),
        user_agent=client_info.get("user_agent"),
    )
    
    return {"message": "Password changed successfully"}


@router.get("/sessions")
async def list_sessions(user: dict = Depends(get_current_user)):
    """
    List all active sessions for current user.
    """
    from database import sessions_collection
    from datetime import datetime, timezone
    
    sessions = await sessions_collection().find({
        "user_id": user["_id"],
        "is_active": True,
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    }).to_list(length=50)
    
    return [
        {
            "id": str(s["_id"]),
            "device_info": s.get("device_info"),
            "ip_address": s.get("ip_address"),
            "created_at": s["created_at"].isoformat(),
            "last_used_at": s["last_used_at"].isoformat(),
        }
        for s in sessions
    ]


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    request: Request,
    user: dict = Depends(get_current_user),
):
    """
    Revoke a specific session.
    """
    from database import sessions_collection
    from bson import ObjectId
    from datetime import datetime, timezone
    
    if not ObjectId.is_valid(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    result = await sessions_collection().update_one(
        {"_id": ObjectId(session_id), "user_id": user["_id"]},
        {"$set": {"is_active": False, "revoked_at": datetime.now(timezone.utc)}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session revoked"}


@router.post("/sessions/revoke-all")
async def revoke_all_sessions(
    request: Request,
    keep_current: bool = Query(default=True, description="Keep current session active"),
    user: dict = Depends(get_current_user),
):
    """
    Revoke all sessions for current user.
    Optionally keeps the current session active.
    """
    from database import sessions_collection
    from datetime import datetime, timezone
    
    now = datetime.now(timezone.utc)
    user_id = user["_id"]
    
    # Build query
    query = {"user_id": user_id, "is_active": True}
    
    # Find current session to potentially exclude it
    current_session_id = user.get("session_id")
    if keep_current and current_session_id:
        from bson import ObjectId
        if ObjectId.is_valid(current_session_id):
            query["_id"] = {"$ne": ObjectId(current_session_id)}
    
    result = await sessions_collection().update_many(
        query,
        {"$set": {"is_active": False, "revoked_at": now}}
    )
    
    # Audit log
    client_info = await get_client_info(request)
    await create_audit_log(
        user_id=user_id,
        action="auth.revoke_all_sessions",
        details={"count": result.modified_count, "keep_current": keep_current},
        ip_address=client_info.get("ip_address"),
        user_agent=client_info.get("user_agent"),
    )
    
    return {
        "message": f"Revoked {result.modified_count} session(s)",
        "count": result.modified_count,
    }


# ==================== Password Reset ====================

class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8)
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v


@router.post("/password-reset/request")
async def request_reset(
    data: PasswordResetRequest,
    request: Request,
):
    """
    Request a password reset email.
    Always returns success to prevent email enumeration.
    """
    try:
        client_info = await get_client_info(request)
        result = await request_password_reset(
            email=data.email,
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent"),
        )
        return result
    except PasswordResetError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/password-reset/validate/{token}")
async def validate_reset(token: str):
    """
    Validate a password reset token.
    Used to check if token is valid before showing reset form.
    """
    token_doc = await validate_reset_token(token)
    
    if not token_doc:
        return {"valid": False, "error": "Invalid or expired reset token"}
    
    return {"valid": True}


@router.post("/password-reset/confirm")
async def confirm_reset(
    data: PasswordResetConfirm,
    request: Request,
):
    """
    Confirm password reset with token and new password.
    """
    try:
        client_info = await get_client_info(request)
        result = await confirm_password_reset(
            token=data.token,
            new_password=data.new_password,
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent"),
        )
        return result
    except PasswordResetError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# ==================== OAuth ====================

# Cache for OAuth providers (1 minute TTL - config can change at runtime)
from time import time as get_time
_oauth_cache = {"data": None, "timestamp": 0}
OAUTH_CACHE_TTL = 60  # 1 minute


@router.get("/oauth/providers")
async def get_oauth_providers():
    """
    Get available OAuth providers and their configuration status (cached).
    """
    global _oauth_cache
    
    now = get_time()
    
    # Return cached data if fresh
    if _oauth_cache["data"] and (now - _oauth_cache["timestamp"]) < OAUTH_CACHE_TTL:
        return _oauth_cache["data"]
    
    # Build fresh response
    result = {
        "providers": [
            {
                "name": "google",
                "display_name": "Google",
                "enabled": is_oauth_configured("google"),
            },
            {
                "name": "github",
                "display_name": "GitHub",
                "enabled": is_oauth_configured("github"),
            },
        ]
    }
    
    # Cache the result
    _oauth_cache = {"data": result, "timestamp": now}
    
    return result


@router.get("/oauth/{provider}/redirect")
async def oauth_redirect(provider: str, request: Request):
    """
    Redirect to OAuth provider for authentication.
    """
    if provider not in ["google", "github"]:
        raise HTTPException(status_code=400, detail="Unknown OAuth provider")
    
    if not is_oauth_configured(provider):
        raise HTTPException(status_code=400, detail=f"{provider} OAuth is not configured")
    
    # Generate state for CSRF protection
    state = generate_oauth_state()
    
    # Store state in session/cookie (for production, use secure cookies)
    # For now, we'll include it in the redirect URL and verify on callback
    
    auth_url = get_authorization_url(provider, state)
    
    return RedirectResponse(url=auth_url)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str = Query(None),
    state: str = Query(None),
    error: str = Query(None),
    request: Request = None,
):
    """
    Handle OAuth callback from provider.
    On success, redirects to frontend with tokens.
    """
    from services.email_service import APP_URL
    
    if error:
        return RedirectResponse(
            url=f"{APP_URL}/oauth/callback?error={error}&provider={provider}"
        )
    
    if not code:
        return RedirectResponse(
            url=f"{APP_URL}/oauth/callback?error=missing_code&provider={provider}"
        )
    
    try:
        client_info = await get_client_info(request)
        result = await handle_oauth_callback(
            provider=provider,
            code=code,
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent"),
        )
        
        # Redirect to frontend with tokens
        access_token = result["access_token"]
        refresh_token = result["refresh_token"]
        
        return RedirectResponse(
            url=f"{APP_URL}/oauth/callback?access_token={access_token}&refresh_token={refresh_token}&provider={provider}"
        )
        
    except OAuthError as e:
        return RedirectResponse(
            url=f"{APP_URL}/oauth/callback?error={e.message}&provider={provider}"
        )

