"""
Admin API Routes
System administration endpoints (system admin only).
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from bson import ObjectId

from models import (
    UserResponse,
    TeamResponse,
    TeamMemberResponse,
)
from core.dependencies import get_current_user, get_client_info
from database import (
    users_collection,
    teams_collection,
    team_memberships_collection,
    execution_logs_collection,
    audit_logs_collection,
)
from services.audit_service import get_audit_logs


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
async def get_admin_overview(
    request: Request,
    user: dict = Depends(require_system_admin)
):
    """
    Get system overview statistics.
    Returns basic counts and recent signups.
    """
    client_info = await get_client_info(request)
    
    # Get total counts
    total_users = await users_collection().count_documents({"is_active": True})
    total_teams = await teams_collection().count_documents({"is_active": True})
    total_executions = await execution_logs_collection().count_documents({})
    
    # Get recent signups (last 10)
    recent_users = await users_collection().find(
        {"is_active": True},
        {"_id": 0, "email": 1, "first_name": 1, "last_name": 1, "created_at": 1, "system_role": 1}
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
            "role": u.get("system_role", "user")
        })
    
    # Get today's stats
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_signups = await users_collection().count_documents({
        "created_at": {"$gte": today_start},
        "is_active": True
    })
    today_executions = await execution_logs_collection().count_documents({
        "created_at": {"$gte": today_start}
    })
    
    # Get system status (basic)
    system_status = {
        "database": "connected",  # Simplified - in reality would check DB connection
        "version": "1.0.0",
        "uptime": "unknown"  # Would need to track startup time
    }
    
    return {
        "total_users": total_users,
        "total_teams": total_teams,
        "total_executions": total_executions,
        "today_signups": today_signups,
        "today_executions": today_executions,
        "recent_signups": recent_signups,
        "system_status": system_status
    }


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    user: dict = Depends(require_system_admin)
):
    """
    List all users with optional filtering and pagination.
    Only accessible by system admins.
    """
    client_info = await get_client_info(request)
    
    # Build query
    query = {"is_active": True}
    
    if role and role in ["admin", "user"]:
        query["system_role"] = role
    
    if search:
        search_regex = {"$regex": search, "$options": "i"}
        query["$or"] = [
            {"email": search_regex},
            {"first_name": search_regex},
            {"last_name": search_regex}
        ]
    
    # Get users
    users_cursor = users_collection().find(
        query,
        {
            "_id": 1,
            "email": 1,
            "first_name": 1,
            "last_name": 1,
            "system_role": 1,
            "email_verified": 1,
            "is_active": 1,
            "created_at": 1,
            "last_login_at": 1
        }
    ).skip(skip).limit(limit).sort("created_at", -1)
    
    users = await users_cursor.to_list(length=limit)
    
    # Convert to response format
    result = []
    for user_doc in users:
        result.append(UserResponse(
            id=str(user_doc["_id"]),
            email=user_doc["email"],
            first_name=user_doc["first_name"],
            last_name=user_doc["last_name"],
            system_role=user_doc.get("system_role", "user"),
            email_verified=user_doc.get("email_verified", False),
            is_active=user_doc.get("is_active", True),
            created_at=user_doc["created_at"],
            last_login_at=user_doc.get("last_login_at")
        ))
    
    return result


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    request: Request,
    user: dict = Depends(require_system_admin)
):
    """
    Get a specific user by ID.
    Only accessible by system admins.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    client_info = await get_client_info(request)
    
    user_doc = await users_collection().find_one(
        {"_id": ObjectId(user_id), "is_active": True},
        {
            "_id": 1,
            "email": 1,
            "first_name": 1,
            "last_name": 1,
            "system_role": 1,
            "email_verified": 1,
            "is_active": 1,
            "created_at": 1,
            "last_login_at": 1
        }
    )
    
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=str(user_doc["_id"]),
        email=user_doc["email"],
        first_name=user_doc["first_name"],
        last_name=user_doc["last_name"],
        system_role=user_doc.get("system_role", "user"),
        email_verified=user_doc.get("email_verified", False),
        is_active=user_doc.get("is_active", True),
        created_at=user_doc["created_at"],
        last_login_at=user_doc.get("last_login_at")
    )


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_data: dict,  # {"role": "admin" or "user"}
    request: Request,
    user: dict = Depends(require_system_admin)
):
    """
    Update a user's system role (admin/user).
    Only accessible by system admins.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    if user_id == user["_id"]:
        raise HTTPException(status_code=400, detail="Cannot modify your own role")
    
    new_role = role_data.get("role")
    if new_role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'admin' or 'user'")
    
    client_info = await get_client_info(request)
    
    # Update user role
    result = await users_collection().update_one(
        {"_id": ObjectId(user_id), "is_active": True},
        {"$set": {"system_role": new_role, "updated_at": datetime.now(timezone.utc)}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Audit log
    await create_audit_log(
        user_id=user["_id"],
        action="admin.user.role_changed",
        resource_type="user",
        resource_id=user_id,
        details={"target_user_id": user_id, "new_role": new_role},
        ip_address=client_info.get("ip_address"),
        user_agent=client_info.get("user_agent")
    )
    
    return {"message": f"User role updated to {new_role}"}


@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    status_data: dict,  # {"is_active": true/false}
    request: Request,
    user: dict = Depends(require_system_admin)
):
    """
    Activate/deactivate a user.
    Only accessible by system admins.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    if user_id == user["_id"]:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    
    is_active = status_data.get("is_active")
    if not isinstance(is_active, bool):
        raise HTTPException(status_code=400, detail="Invalid status. Must be boolean")
    
    client_info = await get_client_info(request)
    
    # Update user status
    result = await users_collection().update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": is_active, "updated_at": datetime.now(timezone.utc)}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Audit log
    await create_audit_log(
        user_id=user["_id"],
        action="admin.user.status_changed",
        resource_type="user",
        resource_id=user_id,
        details={"target_user_id": user_id, "is_active": is_active},
        ip_address=client_info.get("ip_address"),
        user_agent=client_info.get("user_agent")
    )
    
    return {"message": f"User {'activated' if is_active else 'deactivated'}"}


@router.get("/teams", response_model=List[TeamResponse])
async def list_teams(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    user: dict = Depends(require_system_admin)
):
    """
    List all teams with optional filtering and pagination.
    Only accessible by system admins.
    """
    client_info = await get_client_info(request)
    
    # Build query
    query = {"is_active": True}
    
    if search:
        search_regex = {"$regex": search, "$options": "i"}
        query["name"] = search_regex
    
    # Get teams with member count
    pipeline = [
        {"$match": query},
        {"$lookup": {
            "from": "team_memberships",
            "let": {"team_id": "$_id"},
            "pipeline": [
                {"$match": {"$expr": {"$eq": ["$team_id", "$$team_id"]}, "is_active": True}},
                {"$count": "member_count"}
            ],
            "as": "member_count_result"
        }},
        {"$addFields": {
            "member_count": {"$ifNull": [{"$arrayElemAt": ["$member_count_result.member_count", 0]}, 0]}
        }},
        {"$project": {
            "_id": 1,
            "name": 1,
            "slug": 1,
            "type": 1,
            "owner_id": 1,
            "is_active": 1,
            "created_at": 1,
            "member_count": 1
        }},
        {"$sort": {"created_at": -1}},
        {"$skip": skip},
        {"$limit": limit}
    ]
    
    teams_cursor = teams_collection().aggregate(pipeline)
    teams = await teams_cursor.to_list(length=limit)
    
    # Convert to response format
    result = []
    for team_doc in teams:
        result.append(TeamResponse(
            id=str(team_doc["_id"]),
            name=team_doc["name"],
            slug=team_doc["slug"],
            type=team_doc["type"],
            owner_id=team_doc["owner_id"],
            is_active=team_doc.get("is_active", True),
            created_at=team_doc["created_at"],
            member_count=team_doc.get("member_count", 0)
        ))
    
    return result


@router.get("/teams/{team_id}", response_model=dict)
async def get_team_details(
    team_id: str,
    request: Request,
    user: dict = Depends(require_system_admin)
):
    """
    Get detailed information about a specific team.
    Only accessible by system admins.
    """
    if not ObjectId.is_valid(team_id):
        raise HTTPException(status_code=400, detail="Invalid team ID")
    
    client_info = await get_client_info(request)
    
    # Get team basic info
    team = await teams_collection().find_one(
        {"_id": ObjectId(team_id), "is_active": True},
        {
            "_id": 1,
            "name": 1,
            "slug": 1,
            "type": 1,
            "owner_id": 1,
            "is_active": 1,
            "created_at": 1,
            "updated_at": 1
        }
    )
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Get member count
    member_count = await team_memberships_collection().count_documents(
        {"team_id": ObjectId(team_id), "is_active": True}
    )
    
    # Get owner info
    owner = await users_collection().find_one(
        {"_id": ObjectId(team["owner_id"])},
        {"_id": 1, "first_name": 1, "last_name": 1, "email": 1}
    )
    
    owner_name = f"{owner.get('first_name', '')} {owner.get('last_name', '')}".strip() if owner else "Unknown"
    
    return {
        "id": str(team["_id"]),
        "name": team["name"],
        "slug": team["slug"],
        "type": team["type"],
        "owner_id": team["owner_id"],
        "owner_name": owner_name,
        "is_active": team.get("is_active", True),
        "created_at": team["created_at"],
        "updated_at": team.get("updated_at"),
        "member_count": member_count
    }


@router.get("/teams/{team_id}/members", response_model=List[TeamMemberResponse])
async def list_team_members_admin(
    team_id: str,
    request: Request,
    user: dict = Depends(require_system_admin)
):
    """
    List all members of a specific team.
    Only accessible by system admins.
    """
    if not ObjectId.is_valid(team_id):
        raise HTTPException(status_code=400, detail="Invalid team ID")
    
    client_info = await get_client_info(request)
    
    # Verify team exists
    team = await teams_collection().find_one(
        {"_id": ObjectId(team_id), "is_active": True}
    )
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Get members
    members = await team_memberships_collection().find(
        {"team_id": ObjectId(team_id), "is_active": True}
    ).to_list(length=None)
    
    # Get user details for each member
    member_ids = [ObjectId(m["user_id"]) for m in members]
    users_cursor = users_collection().find(
        {"_id": {"$in": member_ids}},
        {"_id": 1, "email": 1, "first_name": 1, "last_name": 1}
    )
    users = await users_cursor.to_list(length=None)
    user_map = {str(u["_id"]): u for u in users}
    
    # Build response
    result = []
    for member in members:
        user_doc = user_map.get(str(member["user_id"]))
        if user_doc:
            result.append(TeamMemberResponse(
                id=str(member["_id"]),
                user_id=member["user_id"],
                email=user_doc["email"],
                first_name=user_doc["first_name"],
                last_name=user_doc["last_name"],
                role=member["role"],
                joined_at=member["joined_at"],
                is_active=True
            ))
    
    return result


@router.get("/stats")
async def get_system_stats(
    request: Request,
    user: dict = Depends(require_system_admin)
):
    """
    Get detailed system statistics.
    Only accessible by system admins.
    """
    client_info = await get_client_info(request)
    
    # User stats
    total_users = await users_collection().count_documents({})
    active_users = await users_collection().count_documents({"is_active": True})
    admin_users = await users_collection().count_documents({"system_role": "admin", "is_active": True})
    verified_users = await users_collection().count_documents({"email_verified": True, "is_active": True})
    
    # Team stats
    total_teams = await teams_collection().count_documents({})
    active_teams = await teams_collection().count_documents({"is_active": True})
    team_types = await teams_collection().aggregate([
        {"$match": {"is_active": True}},
        {"$group": {"_id": "$type", "count": {"$sum": 1}}}
    ]).to_list(length=None)
    
    # Membership stats
    total_memberships = await team_memberships_collection().count_documents({"is_active": True})
    avg_members_per_team = total_memberships / max(active_teams, 1)
    
    # Recent activity (last 24 hours)
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    new_users_today = await users_collection().count_documents({
        "created_at": {"$gte": yesterday},
        "is_active": True
    })
    new_teams_today = await teams_collection().count_documents({
        "created_at": {"$gte": yesterday},
        "is_active": True
    })
    
    # Execution stats
    total_executions = await execution_logs_collection().count_documents({})
    executions_today = await execution_logs_collection().count_documents({
        "created_at": {"$gte": datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)}
    })
    
    # Storage stats (approximate)
    # In a real system, you'd get actual storage stats from your DB
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "admins": admin_users,
            "verified": verified_users,
            "new_today": new_users_today
        },
        "teams": {
            "total": total_teams,
            "active": active_teams,
            "types": {item["_id"]: item["count"] for item in team_types},
            "new_today": new_teams_today,
            "avg_members_per_team": round(avg_members_per_team, 2)
        },
        "memberships": {
            "total": total_memberships
        },
        "executions": {
            "total": total_executions,
            "today": executions_today
        }
    }


@router.get("/logs")
async def get_system_logs(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    action: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    user: dict = Depends(require_system_admin)
):
    """
    Get system audit logs with filtering and pagination.
    Only accessible by system admins.
    """
    client_info = await get_client_info(request)
    
    # Build query
    query = {}
    
    if action:
        query["action"] = action
    
    if user_id:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        query["user_id"] = user_id
    
    if resource_type:
        query["resource_type"] = resource_type
    
    # Date range filtering
    date_conditions = []
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            date_conditions.append({"created_at": {"$gte": start_dt}})
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            date_conditions.append({"created_at": {"$lte": end_dt}})
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")
    
    if date_conditions:
        if len(date_conditions) == 1:
            query.update(date_conditions[0])
        else:
            query["$and"] = date_conditions
    
    # Use the audit service to get logs
    skip = (page - 1) * limit
    logs_result = await get_audit_logs(
        skip=skip,
        limit=limit,
        filters=query
    )
    
    # Enhance logs with user info
    user_ids = list(set(
        log.get("user_id") for log in logs_result.get("logs", []) 
        if log.get("user_id")
    ))
    
    if user_ids:
        # Convert string IDs to ObjectId for query
        object_ids = []
        for uid in user_ids:
            if ObjectId.is_valid(uid):
                object_ids.append(ObjectId(uid))
        
        if object_ids:
            users_cursor = users_collection().find(
                {"_id": {"$in": object_ids}},
                {"_id": 1, "email": 1, "first_name": 1, "last_name": 1}
            )
            users = await users_cursor.to_list(length=None)
            user_map = {str(u["_id"]): f"{u.get('first_name', '')} {u.get('last_name', '')}".strip() or u["email"] 
                       for u in users}
        else:
            user_map = {}
    else:
        user_map = {}
    
    # Format logs for response
    formatted_logs = []
    for log in logs_result.get("logs", []):
        user_id = log.get("user_id")
        user_name = user_map.get(user_id, "System") if user_id else "System"
        
        formatted_logs.append({
            "id": str(log.get("_id")),
            "action": log.get("action"),
            "user_id": user_id,
            "user_name": user_name,
            "resource_type": log.get("resource_type"),
            "resource_id": log.get("resource_id"),
            "details": log.get("details"),
            "ip_address": log.get("ip_address"),
            "user_agent": log.get("user_agent"),
            "created_at": log.get("created_at").isoformat() if log.get("created_at") else None
        })
    
    return {
        "logs": formatted_logs,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": logs_result.get("total", 0),
            "pages": (logs_result.get("total", 0) + limit - 1) // limit
        }
    }


@router.get("/health")
async def get_system_health(
    request: Request,
    user: dict = Depends(require_system_admin)
):
    """
    Get detailed system health metrics.
    Only accessible by system admins.
    """
    client_info = await get_client_info(request)
    
    # Database connectivity checks (simplified)
    try:
        # Ping database
        await users_collection().find_one({})
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    # Check collections
    collections_status = {}
    try:
        collections = await users_collection().database.list_collection_names()
        collections_status = {
            "users": "ok" if "users" in collections else "missing",
            "teams": "ok" if "teams" in collections else "missing",
            "team_memberships": "ok" if "team_memberships" in collections else "missing",
            "execution_logs": "ok" if "execution_logs" in collections else "missing",
            "audit_logs": "ok" if "audit_logs" in collections else "missing"
        }
    except Exception as e:
        collections_status = {"error": str(e)}
    
    # Get recent error rate (from audit logs)
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    recent_errors = await audit_logs_collection().count_documents({
        "action": {"$regex": "error|\.fail", "$options": "i"},
        "created_at": {"$gte": one_hour_ago}
    })
    
    recent_total = await audit_logs_collection().count_documents({
        "created_at": {"$gte": one_hour_ago}
    })
    
    error_rate = (recent_errors / max(recent_total, 1)) * 100
    
    return {
        "status": "healthy" if db_status == "connected" and error_rate < 5 else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {
            "status": db_status,
            "collections": collections_status
        },
        "error_rate": {
            "percentage": round(error_rate, 2),
            "errors_last_hour": recent_errors,
            "total_requests_last_hour": recent_total
        },
        "version": "1.0.0"
    }
