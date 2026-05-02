"""
Team management service.
Handles team creation, invites, membership, and permissions.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List
from bson import ObjectId
import hashlib

from database import (
    teams_collection,
    team_memberships_collection,
    team_invites_collection,
    users_collection,
)
from models import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamWithRole,
    TeamMemberResponse,
    InviteCreate,
    InviteResponse,
    TeamRole,
)
from core.security import generate_slug, generate_invite_token
from services.audit_service import create_audit_log


class TeamError(Exception):
    """Custom exception for team errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def create_team(
    team_data: TeamCreate,
    user_id: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> TeamResponse:
    """
    Create a new team.
    The creating user becomes the owner.
    """
    now = datetime.now(timezone.utc)
    
    team_doc = {
        "name": team_data.name.strip(),
        "slug": generate_slug(team_data.name),
        "type": team_data.type,
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
    
    result = await teams_collection().insert_one(team_doc)
    team_id = str(result.inserted_id)
    
    # Create owner membership
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
    
    # Audit log
    await create_audit_log(
        user_id=user_id,
        team_id=team_id,
        action="team.create",
        resource_type="team",
        resource_id=team_id,
        details={"name": team_data.name, "type": team_data.type},
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    return TeamResponse(
        id=team_id,
        name=team_data.name.strip(),
        slug=team_doc["slug"],
        type=team_data.type,
        owner_id=user_id,
        is_active=True,
        created_at=now,
        member_count=1,
    )


async def get_user_teams(user_id: str) -> List[TeamWithRole]:
    """Get all teams a user is a member of."""
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
            member_count = await team_memberships_collection().count_documents({
                "team_id": membership["team_id"],
                "is_active": True
            })
            
            teams.append(TeamWithRole(
                id=str(team["_id"]),
                name=team["name"],
                slug=team["slug"],
                type=team["type"],
                owner_id=team["owner_id"],
                is_active=True,
                created_at=team["created_at"],
                member_count=member_count,
                role=membership["role"],
                joined_at=membership["joined_at"],
            ))
    
    return teams


async def get_team_by_id(team_id: str, user_id: str) -> TeamWithRole:
    """Get team by ID with user's role."""
    if not ObjectId.is_valid(team_id):
        raise TeamError("Invalid team ID", 400)
    
    team = await teams_collection().find_one({
        "_id": ObjectId(team_id),
        "is_active": True
    })
    
    if not team:
        raise TeamError("Team not found", 404)
    
    membership = await team_memberships_collection().find_one({
        "user_id": user_id,
        "team_id": team_id,
        "is_active": True
    })
    
    if not membership:
        raise TeamError("You are not a member of this team", 403)
    
    member_count = await team_memberships_collection().count_documents({
        "team_id": team_id,
        "is_active": True
    })
    
    return TeamWithRole(
        id=str(team["_id"]),
        name=team["name"],
        slug=team["slug"],
        type=team["type"],
        owner_id=team["owner_id"],
        is_active=True,
        created_at=team["created_at"],
        member_count=member_count,
        role=membership["role"],
        joined_at=membership["joined_at"],
    )


async def update_team(
    team_id: str,
    team_data: TeamUpdate,
    user_id: str,
    user_role: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> TeamResponse:
    """Update team details. Requires owner or admin role."""
    if user_role not in ["owner", "admin"]:
        raise TeamError("Only team owners and admins can update team settings", 403)
    
    update_fields = {"updated_at": datetime.now(timezone.utc)}
    
    if team_data.name is not None:
        update_fields["name"] = team_data.name.strip()
    
    await teams_collection().update_one(
        {"_id": ObjectId(team_id)},
        {"$set": update_fields}
    )
    
    # Audit log
    await create_audit_log(
        user_id=user_id,
        team_id=team_id,
        action="team.update",
        resource_type="team",
        resource_id=team_id,
        details={"changes": team_data.model_dump(exclude_unset=True)},
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    return await get_team_by_id(team_id, user_id)


async def get_team_members(team_id: str) -> List[TeamMemberResponse]:
    """Get all members of a team."""
    memberships = await team_memberships_collection().find({
        "team_id": team_id,
        "is_active": True
    }).to_list(length=500)
    
    members = []
    for membership in memberships:
        user = await users_collection().find_one(
            {"_id": ObjectId(membership["user_id"])},
            {"email": 1, "first_name": 1, "last_name": 1}
        )
        if user:
            members.append(TeamMemberResponse(
                id=str(membership["_id"]),
                user_id=membership["user_id"],
                email=user["email"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                role=membership["role"],
                joined_at=membership["joined_at"],
                is_active=True,
            ))
    
    return members


async def update_member_role(
    team_id: str,
    member_user_id: str,
    new_role: TeamRole,
    actor_user_id: str,
    actor_role: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    """Update a team member's role."""
    if actor_role not in ["owner", "admin"]:
        raise TeamError("Only owners and admins can change member roles", 403)
    
    if new_role == "owner":
        raise TeamError("Cannot assign owner role directly. Use transfer ownership.", 400)
    
    # Can't demote yourself if you're the owner
    membership = await team_memberships_collection().find_one({
        "user_id": member_user_id,
        "team_id": team_id,
        "is_active": True
    })
    
    if not membership:
        raise TeamError("Member not found", 404)
    
    if membership["role"] == "owner" and actor_user_id == member_user_id:
        raise TeamError("Owner cannot change their own role", 400)
    
    # Admin can't change owner's role
    if membership["role"] == "owner" and actor_role != "owner":
        raise TeamError("Only owners can modify the owner's role", 403)
    
    await team_memberships_collection().update_one(
        {"_id": membership["_id"]},
        {"$set": {"role": new_role}}
    )
    
    # Audit log
    await create_audit_log(
        user_id=actor_user_id,
        team_id=team_id,
        action="membership.role_changed",
        resource_type="membership",
        resource_id=str(membership["_id"]),
        details={"target_user_id": member_user_id, "old_role": membership["role"], "new_role": new_role},
        ip_address=ip_address,
        user_agent=user_agent,
    )


async def remove_member(
    team_id: str,
    member_user_id: str,
    actor_user_id: str,
    actor_role: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    """Remove a member from a team."""
    if actor_role not in ["owner", "admin"]:
        raise TeamError("Only owners and admins can remove members", 403)
    
    membership = await team_memberships_collection().find_one({
        "user_id": member_user_id,
        "team_id": team_id,
        "is_active": True
    })
    
    if not membership:
        raise TeamError("Member not found", 404)
    
    if membership["role"] == "owner":
        raise TeamError("Cannot remove the team owner", 400)
    
    # Admin can't remove other admins
    if membership["role"] == "admin" and actor_role == "admin":
        raise TeamError("Admins cannot remove other admins", 403)
    
    await team_memberships_collection().update_one(
        {"_id": membership["_id"]},
        {"$set": {"is_active": False}}
    )
    
    # Audit log
    await create_audit_log(
        user_id=actor_user_id,
        team_id=team_id,
        action="membership.removed",
        resource_type="membership",
        resource_id=str(membership["_id"]),
        details={"removed_user_id": member_user_id},
        ip_address=ip_address,
        user_agent=user_agent,
    )


async def leave_team(
    team_id: str,
    user_id: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    """Leave a team."""
    membership = await team_memberships_collection().find_one({
        "user_id": user_id,
        "team_id": team_id,
        "is_active": True
    })
    
    if not membership:
        raise TeamError("You are not a member of this team", 404)
    
    if membership["role"] == "owner":
        raise TeamError("Owner cannot leave the team. Transfer ownership first.", 400)
    
    await team_memberships_collection().update_one(
        {"_id": membership["_id"]},
        {"$set": {"is_active": False}}
    )
    
    # Audit log
    await create_audit_log(
        user_id=user_id,
        team_id=team_id,
        action="membership.left",
        resource_type="membership",
        resource_id=str(membership["_id"]),
        ip_address=ip_address,
        user_agent=user_agent,
    )


async def create_invite(
    team_id: str,
    invite_data: InviteCreate,
    inviter_id: str,
    inviter_role: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> dict:
    """Create a team invite and send email notification."""
    if inviter_role not in ["owner", "admin"]:
        raise TeamError("Only owners and admins can invite members", 403)
    
    # Check if user already exists and is a member
    existing_user = await users_collection().find_one({"email": invite_data.email.lower()})
    if existing_user:
        existing_membership = await team_memberships_collection().find_one({
            "user_id": str(existing_user["_id"]),
            "team_id": team_id,
            "is_active": True
        })
        if existing_membership:
            raise TeamError("User is already a member of this team", 400)
    
    # Check for existing pending invite
    existing_invite = await team_invites_collection().find_one({
        "team_id": team_id,
        "email": invite_data.email.lower(),
        "is_active": True,
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    
    if existing_invite:
        raise TeamError("An invite has already been sent to this email", 400)
    
    now = datetime.now(timezone.utc)
    token, token_hash = generate_invite_token()
    
    invite_doc = {
        "team_id": team_id,
        "email": invite_data.email.lower(),
        "role": invite_data.role,
        "token_hash": token_hash,
        "invited_by": inviter_id,
        "created_at": now,
        "expires_at": now + timedelta(days=7),
        "accepted_at": None,
        "is_active": True,
    }
    
    result = await team_invites_collection().insert_one(invite_doc)
    
    # Get team and inviter info for email
    team = await teams_collection().find_one({"_id": ObjectId(team_id)})
    inviter = await users_collection().find_one({"_id": ObjectId(inviter_id)})
    
    team_name = team["name"] if team else "Unknown Team"
    inviter_name = f"{inviter['first_name']} {inviter['last_name']}" if inviter else "A team member"
    
    # Send invite email (non-blocking)
    from services.email_service import send_invite_email
    email_result = await send_invite_email(
        to_email=invite_data.email,
        team_name=team_name,
        inviter_name=inviter_name,
        role=invite_data.role,
        token=token,
    )
    
    # Audit log
    await create_audit_log(
        user_id=inviter_id,
        team_id=team_id,
        action="membership.invite_sent",
        resource_type="invite",
        resource_id=str(result.inserted_id),
        details={
            "email": invite_data.email,
            "role": invite_data.role,
            "email_sent": email_result is not None,
        },
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    return {
        "invite_id": str(result.inserted_id),
        "token": token,  # Return for testing/debugging
        "expires_at": invite_doc["expires_at"].isoformat(),
        "email_sent": email_result is not None,
    }


async def accept_invite(
    token: str,
    user_id: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> TeamWithRole:
    """Accept a team invite."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    now = datetime.now(timezone.utc)
    
    invite = await team_invites_collection().find_one({
        "token_hash": token_hash,
        "is_active": True,
        "expires_at": {"$gt": now}
    })
    
    if not invite:
        raise TeamError("Invalid or expired invite", 400)
    
    # Verify user email matches invite
    user = await users_collection().find_one({"_id": ObjectId(user_id)})
    if user["email"].lower() != invite["email"].lower():
        raise TeamError("This invite was sent to a different email address", 403)
    
    # Check not already a member
    existing = await team_memberships_collection().find_one({
        "user_id": user_id,
        "team_id": invite["team_id"],
        "is_active": True
    })
    
    if existing:
        raise TeamError("You are already a member of this team", 400)
    
    # Create membership
    membership_doc = {
        "user_id": user_id,
        "team_id": invite["team_id"],
        "role": invite["role"],
        "invited_by": invite["invited_by"],
        "invited_at": invite["created_at"],
        "joined_at": now,
        "is_active": True,
    }
    
    await team_memberships_collection().insert_one(membership_doc)
    
    # Mark invite as used
    await team_invites_collection().update_one(
        {"_id": invite["_id"]},
        {"$set": {"is_active": False, "accepted_at": now}}
    )
    
    # Audit log
    await create_audit_log(
        user_id=user_id,
        team_id=invite["team_id"],
        action="membership.invite_accepted",
        resource_type="invite",
        resource_id=str(invite["_id"]),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    return await get_team_by_id(invite["team_id"], user_id)


async def get_pending_invites(team_id: str) -> List[InviteResponse]:
    """Get all pending invites for a team."""
    now = datetime.now(timezone.utc)
    
    invites = await team_invites_collection().find({
        "team_id": team_id,
        "is_active": True,
        "expires_at": {"$gt": now}
    }).to_list(length=100)
    
    result = []
    for invite in invites:
        team = await teams_collection().find_one({"_id": ObjectId(team_id)})
        inviter = await users_collection().find_one({"_id": ObjectId(invite["invited_by"])})
        
        result.append(InviteResponse(
            id=str(invite["_id"]),
            team_id=team_id,
            team_name=team["name"] if team else "Unknown",
            email=invite["email"],
            role=invite["role"],
            invited_by_name=f"{inviter['first_name']} {inviter['last_name']}" if inviter else "Unknown",
            created_at=invite["created_at"],
            expires_at=invite["expires_at"],
            is_active=True,
        ))
    
    return result


async def revoke_invite(
    team_id: str,
    invite_id: str,
    actor_user_id: str,
    actor_role: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    """Revoke a pending invite."""
    if actor_role not in ["owner", "admin"]:
        raise TeamError("Only owners and admins can revoke invites", 403)
    
    result = await team_invites_collection().update_one(
        {"_id": ObjectId(invite_id), "team_id": team_id, "is_active": True},
        {"$set": {"is_active": False}}
    )
    
    if result.matched_count == 0:
        raise TeamError("Invite not found", 404)
    
    # Audit log
    await create_audit_log(
        user_id=actor_user_id,
        team_id=team_id,
        action="membership.invite_revoked",
        resource_type="invite",
        resource_id=invite_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
