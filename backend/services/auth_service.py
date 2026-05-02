"""
Authentication service for user registration, login, and token management.
"""

from datetime import datetime, timezone
from typing import Optional, Tuple
from bson import ObjectId

from database import (
    users_collection,
    sessions_collection,
    teams_collection,
    team_memberships_collection,
)
from models import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserWithTeams,
    TeamWithRole,
    AuthResponse,
)
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
    generate_slug,
    get_token_expiry_seconds,
    get_refresh_token_expiry,
)
from services.audit_service import create_audit_log


class AuthError(Exception):
    """Custom exception for authentication errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def register_user(
    user_data: UserCreate,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuthResponse:
    """
    Register a new user.
    - Creates user account
    - Creates personal team
    - Creates team membership
    - Returns auth tokens
    """
    # Check if email already exists
    existing = await users_collection().find_one({"email": user_data.email.lower()})
    if existing:
        raise AuthError("Email already registered", 409)
    
    now = datetime.now(timezone.utc)
    
    # Create user document
    user_doc = {
        "email": user_data.email.lower(),
        "password_hash": hash_password(user_data.password),
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "system_role": "user",
        "oauth_providers": [],
        "email_verified": False,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "last_login_at": now,
    }
    
    # Insert user
    user_result = await users_collection().insert_one(user_doc)
    user_id = str(user_result.inserted_id)
    
    # Create personal team
    team_name = f"{user_data.first_name}'s Team"
    team_doc = {
        "name": team_name,
        "slug": generate_slug(team_name),
        "type": "personal",
        "owner_id": user_id,
        "settings": {
            "allow_member_invites": False,
            "default_member_role": "member",
            "require_2fa": False,
        },
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    
    team_result = await teams_collection().insert_one(team_doc)
    team_id = str(team_result.inserted_id)
    
    # Create team membership (owner)
    membership_doc = {
        "user_id": user_id,
        "team_id": team_id,
        "role": "owner",
        "invited_by": None,
        "invited_at": None,
        "joined_at": now,
        "is_active": True,
    }
    
    await team_memberships_collection().insert_one(membership_doc)
    
    # Create tokens
    access_token = create_access_token(user_id)
    refresh_token, refresh_token_hash = create_refresh_token(user_id)
    
    # Store session
    session_doc = {
        "user_id": user_id,
        "refresh_token_hash": refresh_token_hash,
        "device_info": None,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "created_at": now,
        "expires_at": get_refresh_token_expiry(),
        "last_used_at": now,
        "revoked_at": None,
        "is_active": True,
    }
    
    await sessions_collection().insert_one(session_doc)
    
    # Audit log
    await create_audit_log(
        user_id=user_id,
        action="auth.signup",
        team_id=team_id,
        details={"email": user_data.email},
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    # Build response
    user_response = {
        "id": user_id,
        "email": user_data.email.lower(),
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "system_role": "user",
        "email_verified": False,
        "is_active": True,
        "created_at": now.isoformat(),
        "last_login_at": now.isoformat(),
        "has_oauth": False,
    }
    
    team_response = {
        "id": team_id,
        "name": team_name,
        "slug": team_doc["slug"],
        "type": "personal",
        "role": "owner",
    }
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=get_token_expiry_seconds(),
        user=user_response,
        current_team=team_response,
    )


async def login_user(
    credentials: UserLogin,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuthResponse:
    """
    Authenticate user with email and password.
    Returns auth tokens and user info.
    """
    # Find user by email
    user = await users_collection().find_one({"email": credentials.email.lower()})
    
    if not user:
        raise AuthError("Invalid email or password", 401)
    
    if not user.get("is_active"):
        raise AuthError("Account is deactivated", 401)
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise AuthError("Invalid email or password", 401)
    
    user_id = str(user["_id"])
    now = datetime.now(timezone.utc)
    
    # Update last login
    await users_collection().update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login_at": now}}
    )
    
    # Create tokens
    access_token = create_access_token(user_id)
    refresh_token, refresh_token_hash = create_refresh_token(user_id)
    
    # Store session
    session_doc = {
        "user_id": user_id,
        "refresh_token_hash": refresh_token_hash,
        "device_info": None,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "created_at": now,
        "expires_at": get_refresh_token_expiry(),
        "last_used_at": now,
        "revoked_at": None,
        "is_active": True,
    }
    
    await sessions_collection().insert_one(session_doc)
    
    # Get user's teams
    memberships = await team_memberships_collection().find({
        "user_id": user_id,
        "is_active": True
    }).to_list(length=100)
    
    current_team = None
    if memberships:
        # Get first team as current
        team = await teams_collection().find_one({
            "_id": ObjectId(memberships[0]["team_id"]),
            "is_active": True
        })
        if team:
            current_team = {
                "id": str(team["_id"]),
                "name": team["name"],
                "slug": team["slug"],
                "type": team["type"],
                "role": memberships[0]["role"],
            }
    
    # Audit log
    await create_audit_log(
        user_id=user_id,
        action="auth.login",
        team_id=current_team["id"] if current_team else None,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    # Build response
    user_response = {
        "id": user_id,
        "email": user["email"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "system_role": user.get("system_role", "user"),
        "email_verified": user.get("email_verified", False),
        "is_active": True,
        "created_at": user["created_at"].isoformat(),
        "last_login_at": now.isoformat(),
        "has_oauth": len(user.get("oauth_providers", [])) > 0,
    }
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=get_token_expiry_seconds(),
        user=user_response,
        current_team=current_team,
    )


async def refresh_tokens(
    refresh_token: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Refresh access and refresh tokens.
    Returns new (access_token, refresh_token) pair.
    """
    # Decode refresh token
    payload = decode_token(refresh_token)
    
    if not payload:
        raise AuthError("Invalid or expired refresh token", 401)
    
    if payload.get("type") != "refresh":
        raise AuthError("Invalid token type", 401)
    
    user_id = payload.get("sub")
    token_hash = hash_token(refresh_token)
    
    # Find and validate session
    session = await sessions_collection().find_one({
        "user_id": user_id,
        "refresh_token_hash": token_hash,
        "is_active": True,
    })
    
    if not session:
        raise AuthError("Session not found or revoked", 401)
    
    now = datetime.now(timezone.utc)
    
    # Handle both offset-naive and offset-aware datetimes from MongoDB
    expires_at = session["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < now:
        raise AuthError("Session expired", 401)
    
    # Verify user is still active
    user = await users_collection().find_one({
        "_id": ObjectId(user_id),
        "is_active": True
    })
    
    if not user:
        raise AuthError("User not found or inactive", 401)
    
    # Revoke old session
    await sessions_collection().update_one(
        {"_id": session["_id"]},
        {"$set": {"is_active": False, "revoked_at": now}}
    )
    
    # Create new tokens
    new_access_token = create_access_token(user_id)
    new_refresh_token, new_refresh_token_hash = create_refresh_token(user_id)
    
    # Store new session
    new_session_doc = {
        "user_id": user_id,
        "refresh_token_hash": new_refresh_token_hash,
        "device_info": session.get("device_info"),
        "ip_address": ip_address,
        "user_agent": user_agent,
        "created_at": now,
        "expires_at": get_refresh_token_expiry(),
        "last_used_at": now,
        "revoked_at": None,
        "is_active": True,
    }
    
    await sessions_collection().insert_one(new_session_doc)
    
    # Audit log
    await create_audit_log(
        user_id=user_id,
        action="auth.token_refresh",
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    return new_access_token, new_refresh_token


async def logout_user(
    user_id: str,
    refresh_token: Optional[str] = None,
    logout_all: bool = False,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    """
    Logout user by revoking session(s).
    If refresh_token provided, revokes that specific session.
    If logout_all is True, revokes all user sessions.
    """
    now = datetime.now(timezone.utc)
    
    if logout_all:
        # Revoke all sessions
        await sessions_collection().update_many(
            {"user_id": user_id, "is_active": True},
            {"$set": {"is_active": False, "revoked_at": now}}
        )
    elif refresh_token:
        # Revoke specific session
        token_hash = hash_token(refresh_token)
        await sessions_collection().update_one(
            {"user_id": user_id, "refresh_token_hash": token_hash},
            {"$set": {"is_active": False, "revoked_at": now}}
        )
    
    # Audit log
    await create_audit_log(
        user_id=user_id,
        action="auth.logout",
        details={"logout_all": logout_all},
        ip_address=ip_address,
        user_agent=user_agent,
    )


async def get_user_with_teams(user_id: str) -> UserWithTeams:
    """Get user with all their team memberships."""
    user = await users_collection().find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise AuthError("User not found", 404)
    
    # Get memberships
    memberships = await team_memberships_collection().find({
        "user_id": user_id,
        "is_active": True
    }).to_list(length=100)
    
    teams = []
    for membership in memberships:
        team = await teams_collection().find_one({
            "_id": ObjectId(membership["team_id"]),
            "is_active": True
        })
        if team:
            teams.append({
                "id": str(team["_id"]),
                "name": team["name"],
                "slug": team["slug"],
                "type": team["type"],
                "role": membership["role"],
                "joined_at": membership["joined_at"].isoformat(),
            })
    
    return UserWithTeams(
        id=str(user["_id"]),
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        system_role=user.get("system_role", "user"),
        email_verified=user.get("email_verified", False),
        is_active=user.get("is_active", True),
        created_at=user["created_at"],
        last_login_at=user.get("last_login_at"),
        has_oauth=len(user.get("oauth_providers", [])) > 0,
        teams=teams,
    )
