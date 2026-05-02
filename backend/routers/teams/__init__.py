"""
Team management API routes.
Handles team CRUD, membership, and invites.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List

from models import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamWithRole,
    TeamMemberResponse,
    InviteCreate,
    InviteResponse,
    UpdateMemberRole,
    AcceptInvite,
)
from core.engine_context import get_engine_context, EngineContext
from services.team_service import (
    create_team,
    get_user_teams,
    get_team_by_id,
    update_team,
    get_team_members,
    update_member_role,
    remove_member,
    leave_team,
    create_invite,
    accept_invite,
    get_pending_invites,
    revoke_invite,
    TeamError,
)
from core.dependencies import (
    get_current_user,
    get_current_team,
    require_team_role,
    get_client_info,
)


router = APIRouter(prefix="/teams", tags=["Teams"])


# Team CRUD
@router.post("", response_model=TeamResponse)
async def create_new_team(
    team_data: TeamCreate,
    request: Request,
    user: dict = Depends(get_current_user),
):
    """Create a new team. Current user becomes owner."""
    try:
        client_info = await get_client_info(request)
        return await create_team(
            team_data,
            user_id=user["_id"],
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent"),
        )
    except TeamError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("", response_model=List[TeamWithRole])
async def list_my_teams(user: dict = Depends(get_current_user)):
    """Get all teams current user is a member of."""
    return await get_user_teams(user["_id"])


@router.get("/{team_id}", response_model=TeamWithRole)
async def get_team(
    team_id: str,
    user: dict = Depends(get_current_user),
):
    """Get team details by ID."""
    try:
        return await get_team_by_id(team_id, user["_id"])
    except TeamError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team_details(
    team_id: str,
    team_data: TeamUpdate,
    request: Request,
    user_team: tuple = Depends(require_team_role("owner", "admin")),
):
    """Update team details. Requires owner or admin role."""
    user, team = user_team
    try:
        client_info = await get_client_info(request)
        return await update_team(
            team_id,
            team_data,
            user_id=user["_id"],
            user_role=team["user_role"],
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent"),
        )
    except TeamError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# Members
@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
async def list_team_members(
    team_id: str,
    user: dict = Depends(get_current_user),
):
    """Get all members of a team."""
    # Verify access
    try:
        await get_team_by_id(team_id, user["_id"])
    except TeamError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    
    return await get_team_members(team_id)


@router.put("/{team_id}/members/{member_user_id}/role")
async def change_member_role(
    team_id: str,
    member_user_id: str,
    role_data: UpdateMemberRole,
    request: Request,
    user_team: tuple = Depends(require_team_role("owner", "admin")),
):
    """Change a member's role. Requires owner or admin role."""
    user, team = user_team
    try:
        client_info = await get_client_info(request)
        await update_member_role(
            team_id,
            member_user_id,
            new_role=role_data.role,
            actor_user_id=user["_id"],
            actor_role=team["user_role"],
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent"),
        )
        return {"message": "Role updated"}
    except TeamError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{team_id}/members/{member_user_id}")
async def remove_team_member(
    team_id: str,
    member_user_id: str,
    request: Request,
    user_team: tuple = Depends(require_team_role("owner", "admin")),
):
    """Remove a member from team. Requires owner or admin role."""
    user, team = user_team
    try:
        client_info = await get_client_info(request)
        await remove_member(
            team_id,
            member_user_id,
            actor_user_id=user["_id"],
            actor_role=team["user_role"],
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent"),
        )
        return {"message": "Member removed"}
    except TeamError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{team_id}/leave")
async def leave_current_team(
    team_id: str,
    request: Request,
    user: dict = Depends(get_current_user),
):
    """Leave a team."""
    try:
        client_info = await get_client_info(request)
        await leave_team(
            team_id,
            user_id=user["_id"],
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent"),
        )
        return {"message": "Left team"}
    except TeamError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# Invites
@router.post("/{team_id}/invites")
async def invite_member(
    team_id: str,
    invite_data: InviteCreate,
    request: Request,
    user_team: tuple = Depends(require_team_role("owner", "admin")),
):
    """Invite a new member to team. Requires owner or admin role."""
    user, team = user_team
    try:
        client_info = await get_client_info(request)
        return await create_invite(
            team_id,
            invite_data,
            inviter_id=user["_id"],
            inviter_role=team["user_role"],
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent"),
        )
    except TeamError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{team_id}/invites", response_model=List[InviteResponse])
async def list_pending_invites(
    team_id: str,
    user_team: tuple = Depends(require_team_role("owner", "admin")),
):
    """Get pending invites for team. Requires owner or admin role."""
    return await get_pending_invites(team_id)


@router.delete("/{team_id}/invites/{invite_id}")
async def revoke_team_invite(
    team_id: str,
    invite_id: str,
    request: Request,
    user_team: tuple = Depends(require_team_role("owner", "admin")),
):
    """Revoke a pending invite. Requires owner or admin role."""
    user, team = user_team
    try:
        client_info = await get_client_info(request)
        await revoke_invite(
            team_id,
            invite_id,
            actor_user_id=user["_id"],
            actor_role=team["user_role"],
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent"),
        )
        return {"message": "Invite revoked"}
    except TeamError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/invites/accept")
async def accept_team_invite(
    invite_data: AcceptInvite,
    request: Request,
    user: dict = Depends(get_current_user),
):
    """Accept a team invite using the invite token."""
    try:
        client_info = await get_client_info(request)
        return await accept_invite(
            invite_data.token,
            user_id=user["_id"],
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent"),
        )
    except TeamError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)



@router.get("/{team_id}/activity")
async def get_team_activity(
    team_id: str,
    ctx: EngineContext = Depends(get_engine_context),
):
    """
    Get recent activity log for the team.
    Returns the 20 most recent audit log entries.
    """
    ctx.require_read()
    
    if ctx.team_id != team_id:
        raise HTTPException(status_code=403, detail="Not authorized for this team")
    
    from database import audit_logs_collection, users_collection
    from bson import ObjectId
    
    # Fetch recent audit logs for this team
    logs = await audit_logs_collection().find(
        {"team_id": team_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(20).to_list(20)
    
    # Get user info for actors
    user_ids = list(set(log.get("user_id") for log in logs if log.get("user_id")))
    users_map = {}
    
    if user_ids:
        users = await users_collection().find(
            {"_id": {"$in": [ObjectId(uid) for uid in user_ids if ObjectId.is_valid(uid)]}},
            {"_id": 1, "email": 1, "first_name": 1, "last_name": 1}
        ).to_list(100)
        
        for u in users:
            users_map[str(u["_id"])] = {
                "email": u["email"],
                "name": f"{u.get('first_name', '')} {u.get('last_name', '')}".strip() or u["email"]
            }
    
    # Format response
    activity = []
    for log in logs:
        user_id = log.get("user_id")
        user_info = users_map.get(user_id, {"email": "system", "name": "System"})
        
        activity.append({
            "action": log.get("action", "unknown"),
            "actor": user_info["name"],
            "actor_email": user_info["email"],
            "timestamp": log["created_at"].isoformat() if log.get("created_at") else None,
            "details": log.get("details"),
            "resource_type": log.get("resource_type"),
            "ip_address": log.get("ip_address"),
        })
    
    return {"activity": activity}
