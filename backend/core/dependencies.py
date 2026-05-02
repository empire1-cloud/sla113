"""
Authentication dependencies for FastAPI routes.
Provides current user, team context, and permission checks.
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Tuple
from bson import ObjectId

from core.security import decode_token
from database import users_collection, teams_collection, team_memberships_collection
from models import UserInDB, TeamInDB, TeamRole


# HTTP Bearer token extractor
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Get the current authenticated user from JWT token.
    Raises 401 if not authenticated.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    user = await users_collection().find_one({
        "_id": ObjectId(user_id),
        "is_active": True
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user["_id"] = str(user["_id"])
    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[dict]:
    """
    Get current user if authenticated, None otherwise.
    Does not raise exceptions.
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


async def get_current_team(
    request: Request,
    user: dict = Depends(get_current_user)
) -> dict:
    """
    Get the current team context from X-Team-ID header.
    Validates user has access to the team.
    """
    team_id = request.headers.get("X-Team-ID")
    
    if not team_id:
        # Get user's default team (first team they're a member of)
        membership = await team_memberships_collection().find_one({
            "user_id": user["_id"],
            "is_active": True
        })
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No team context. Please specify X-Team-ID header.",
            )
        
        team_id = membership["team_id"]
    
    # Validate team exists and user has access
    if not ObjectId.is_valid(team_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid team ID format",
        )
    
    team = await teams_collection().find_one({
        "_id": ObjectId(team_id),
        "is_active": True
    })
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    
    # Check membership
    membership = await team_memberships_collection().find_one({
        "user_id": user["_id"],
        "team_id": team_id,
        "is_active": True
    })
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this team",
        )
    
    team["_id"] = str(team["_id"])
    team["user_role"] = membership["role"]
    return team


async def get_user_and_team(
    request: Request,
    user: dict = Depends(get_current_user)
) -> Tuple[dict, dict]:
    """Get both current user and team context."""
    team = await get_current_team(request, user)
    return user, team


def require_team_role(*allowed_roles: TeamRole):
    """
    Dependency factory for requiring specific team roles.
    Usage: Depends(require_team_role("owner", "admin"))
    """
    async def check_role(
        request: Request,
        user: dict = Depends(get_current_user)
    ) -> Tuple[dict, dict]:
        team = await get_current_team(request, user)
        
        if team["user_role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of these roles: {', '.join(allowed_roles)}",
            )
        
        return user, team
    
    return check_role


def require_system_admin():
    """Dependency for requiring system admin role."""
    async def check_admin(user: dict = Depends(get_current_user)) -> dict:
        if user.get("system_role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This action requires system admin privileges",
            )
        return user
    
    return check_admin


async def get_client_info(request: Request) -> dict:
    """Extract client information from request for audit logging."""
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("User-Agent"),
    }
