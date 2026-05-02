"""
Audit logging service for tracking all user and system actions.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId

from database import audit_logs_collection, users_collection, teams_collection
from models import AuditLogCreate, AuditLogResponse, AuditLogQuery


async def create_audit_log(
    user_id: str,
    action: str,
    team_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Dict[str, Any] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> str:
    """
    Create an audit log entry.
    Returns the created log ID.
    """
    log_doc = {
        "user_id": user_id,
        "team_id": team_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": details or {},
        "ip_address": ip_address,
        "user_agent": user_agent,
        "created_at": datetime.now(timezone.utc),
    }
    
    result = await audit_logs_collection().insert_one(log_doc)
    return str(result.inserted_id)


async def get_audit_logs(
    query: AuditLogQuery,
    team_id: Optional[str] = None,
) -> List[AuditLogResponse]:
    """
    Get audit logs with filtering and pagination.
    If team_id is provided, only returns logs for that team.
    """
    filter_query = {}
    
    if team_id:
        filter_query["team_id"] = team_id
    
    if query.user_id:
        filter_query["user_id"] = query.user_id
    
    if query.action:
        filter_query["action"] = {"$regex": f"^{query.action}"}
    
    if query.resource_type:
        filter_query["resource_type"] = query.resource_type
    
    if query.start_date:
        filter_query["created_at"] = {"$gte": query.start_date}
    
    if query.end_date:
        if "created_at" in filter_query:
            filter_query["created_at"]["$lte"] = query.end_date
        else:
            filter_query["created_at"] = {"$lte": query.end_date}
    
    cursor = audit_logs_collection().find(filter_query).sort(
        "created_at", -1
    ).skip(query.offset).limit(query.limit)
    
    logs = await cursor.to_list(length=query.limit)
    
    # Enrich with user and team names
    result = []
    for log in logs:
        response = AuditLogResponse(
            id=str(log["_id"]),
            user_id=log["user_id"],
            team_id=log.get("team_id"),
            action=log["action"],
            resource_type=log.get("resource_type"),
            resource_id=log.get("resource_id"),
            details=log.get("details", {}),
            ip_address=log.get("ip_address"),
            created_at=log["created_at"],
        )
        
        # Get user email
        if log["user_id"]:
            user = await users_collection().find_one(
                {"_id": ObjectId(log["user_id"])},
                {"email": 1}
            )
            if user:
                response.user_email = user["email"]
        
        # Get team name
        if log.get("team_id"):
            team = await teams_collection().find_one(
                {"_id": ObjectId(log["team_id"])},
                {"name": 1}
            )
            if team:
                response.team_name = team["name"]
        
        result.append(response)
    
    return result


async def get_user_activity(
    user_id: str,
    limit: int = 50,
) -> List[AuditLogResponse]:
    """Get recent activity for a specific user."""
    query = AuditLogQuery(user_id=user_id, limit=limit)
    return await get_audit_logs(query)


async def get_team_activity(
    team_id: str,
    limit: int = 50,
) -> List[AuditLogResponse]:
    """Get recent activity for a specific team."""
    query = AuditLogQuery(limit=limit)
    return await get_audit_logs(query, team_id=team_id)
