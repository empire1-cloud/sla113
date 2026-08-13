"""
Admin API Routes
System administration endpoints (system admin only).
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone, timedelta
from typing import List

from core.dependencies import get_current_user
from database import (
    users_collection,
    teams_collection,
    execution_logs_collection,
)


router = APIRouter(prefix="/admin", tags=["Admin"])


def require_system_admin(user: dict = Depends(get_current_user)):
    """Dependency that requires system admin role."""
    if user.get("system_role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="System admin access required"
        )
    return user


@router.get("/overview")
async def get_admin_overview(user: dict = Depends(require_system_admin)):
    """
    Get system overview statistics.
    Returns basic counts and recent signups.
    """
    # Get total counts
    total_users = await users_collection().count_documents({"is_active": True})
    total_teams = await teams_collection().count_documents({"is_active": True})
    total_executions = await execution_logs_collection().count_documents({})
    
    # Get recent signups (last 10)
    recent_users = await users_collection().find(
        {"is_active": True},
        {"_id": 0, "email": 1, "first_name": 1, "last_name": 1, "created_at": 1}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    recent_signups = []
    for u in recent_users:
        name = f"{u.get('first_name', '')} {u.get('last_name', '')}".strip()
        created_at = u.get("created_at")
        if created_at and isinstance(created_at, datetime):
            created_at = created_at.isoformat()
        
        recent_signups.append({
            "email": u["email"],
            "name": name or u["email"],
            "created_at": created_at,
        })
    
    # Get today's stats
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_signups = await users_collection().count_documents({
        "created_at": {"$gte": today_start}
    })
    today_executions = await execution_logs_collection().count_documents({
        "created_at": {"$gte": today_start}
    })
    
    return {
        "total_users": total_users,
        "total_teams": total_teams,
        "total_executions": total_executions,
        "today_signups": today_signups,
        "today_executions": today_executions,
        "recent_signups": recent_signups,
    }
