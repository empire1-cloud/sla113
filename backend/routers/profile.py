"""
User Profile API endpoints.

Provides:
- Get full profile details with memberships
- Update profile info (name)
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId

from core.dependencies import get_current_user
from database import users_collection, teams_collection, team_memberships_collection

router = APIRouter(prefix="/profile", tags=["Profile"])


class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)


class TeamMembershipResponse(BaseModel):
    id: str
    name: str
    type: str
    role: str
    joined_at: str


class ProfileResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    system_role: str
    created_at: str
    teams: List[TeamMembershipResponse]


@router.get("/me", response_model=ProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's full profile with team memberships."""
    user_id = current_user["_id"]
    
    # Get user details
    user = await users_collection().find_one(
        {"_id": ObjectId(user_id) if isinstance(user_id, str) else user_id},
        {"_id": 0, "password_hash": 0}
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all memberships
    memberships = await team_memberships_collection().find(
        {"user_id": user_id, "is_active": True}
    ).to_list(100)
    
    # Get team details for each membership
    teams = []
    for membership in memberships:
        team = await teams_collection().find_one(
            {"_id": ObjectId(membership["team_id"]) if isinstance(membership["team_id"], str) else membership["team_id"]},
        )
        if team:
            teams.append(TeamMembershipResponse(
                id=str(team["_id"]),
                name=team["name"],
                type=team.get("type", "organization"),
                role=membership["role"],
                joined_at=membership.get("created_at", datetime.now(timezone.utc)).isoformat() if isinstance(membership.get("created_at"), datetime) else str(membership.get("created_at", ""))
            ))
    
    return ProfileResponse(
        id=str(user_id),
        email=user["email"],
        first_name=user.get("first_name"),
        last_name=user.get("last_name"),
        system_role=user.get("system_role", "user"),
        created_at=user.get("created_at", datetime.now(timezone.utc)).isoformat() if isinstance(user.get("created_at"), datetime) else str(user.get("created_at", "")),
        teams=teams
    )


@router.put("/me")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update current user's profile information."""
    user_id = current_user["_id"]
    
    update_data = {}
    if request.first_name is not None:
        update_data["first_name"] = request.first_name
    if request.last_name is not None:
        update_data["last_name"] = request.last_name
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await users_collection().update_one(
        {"_id": ObjectId(user_id) if isinstance(user_id, str) else user_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "Profile updated successfully"}

