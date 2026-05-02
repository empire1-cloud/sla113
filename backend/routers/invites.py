"""
Public Invites API
Endpoints that don't require authentication for invite acceptance flow.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId
import hashlib

from database import (
    team_invites_collection,
    teams_collection,
    users_collection,
)

router = APIRouter(prefix="/invites", tags=["Invites"])


class InviteValidationResponse(BaseModel):
    valid: bool
    team_name: Optional[str] = None
    team_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    invited_by_name: Optional[str] = None
    expires_at: Optional[str] = None
    error: Optional[str] = None


@router.get("/validate/{token}", response_model=InviteValidationResponse)
async def validate_invite_token(token: str):
    """
    Validate an invite token without requiring authentication.
    Used to show invite details on the accept invite page.
    """
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    now = datetime.now(timezone.utc)
    
    invite = await team_invites_collection().find_one({
        "token_hash": token_hash,
    })
    
    if not invite:
        return InviteValidationResponse(
            valid=False,
            error="Invalid invite token"
        )
    
    # Check if already accepted
    if invite.get("accepted_at"):
        return InviteValidationResponse(
            valid=False,
            error="This invite has already been used"
        )
    
    # Check if revoked
    if not invite.get("is_active", True):
        return InviteValidationResponse(
            valid=False,
            error="This invite has been revoked"
        )
    
    # Check if expired
    expires_at = invite.get("expires_at")
    if expires_at:
        # Handle both naive and aware datetimes
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            return InviteValidationResponse(
                valid=False,
                error="This invite has expired"
            )
    
    # Get team details
    team = await teams_collection().find_one({
        "_id": ObjectId(invite["team_id"])
    })
    
    team_name = team["name"] if team else "Unknown Team"
    
    # Get inviter details
    inviter = await users_collection().find_one({
        "_id": ObjectId(invite["invited_by"])
    })
    
    inviter_name = f"{inviter['first_name']} {inviter['last_name']}" if inviter else "A team member"
    
    return InviteValidationResponse(
        valid=True,
        team_name=team_name,
        team_id=invite["team_id"],
        email=invite["email"],
        role=invite["role"],
        invited_by_name=inviter_name,
        expires_at=expires_at.isoformat() if expires_at else None,
    )


@router.get("/check-email/{token}/{email}")
async def check_invite_email_match(token: str, email: str):
    """
    Check if an email matches the invite.
    Used for login/signup flow on accept page.
    """
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    invite = await team_invites_collection().find_one({
        "token_hash": token_hash,
        "is_active": True,
    })
    
    if not invite:
        return {"matches": False, "error": "Invalid invite"}
    
    return {
        "matches": invite["email"].lower() == email.lower(),
        "invite_email": invite["email"],
    }
