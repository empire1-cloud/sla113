"""
Team-Scoped Execution Logger Service

Logs all engine calls and pipeline runs to MongoDB with team isolation.
Replaces the old file-based logger with a proper database-backed solution.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from bson import ObjectId

from database import execution_logs_collection, users_collection, pipelines_collection
from models import ExecutionLogCreate, ExecutionLogResponse, ExecutionLogQuery
from services.audit_service import create_audit_log


async def log_execution(
    team_id: str,
    user_id: str,
    engine: str,
    input_data: Dict[str, Any],
    output_data: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None,
    duration_ms: int = 0,
    source: str = "direct",
    pipeline_id: Optional[str] = None,
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
) -> str:
    """
    Log an engine execution to the database.
    Returns the created log ID.
    """
    now = datetime.now(timezone.utc)
    
    log_doc = {
        "team_id": team_id,
        "user_id": user_id,
        "engine": engine,
        "pipeline_id": pipeline_id,
        "input_data": _sanitize_for_mongo(input_data),
        "output_data": _sanitize_for_mongo(output_data) if output_data else None,
        "error_message": error_message,
        "status": "success" if error_message is None else "error",
        "source": source,
        "duration_ms": duration_ms,
        "endpoint": endpoint,
        "method": method,
        "created_at": now,
        "completed_at": now if output_data or error_message else None,
    }
    
    result = await execution_logs_collection().insert_one(log_doc)
    
    # Also create audit log for engine executions
    await create_audit_log(
        user_id=user_id,
        team_id=team_id,
        action="engine.execute",
        resource_type="engine",
        resource_id=engine,
        details={
            "engine": engine,
            "status": log_doc["status"],
            "duration_ms": duration_ms,
            "source": source,
        },
    )
    
    return str(result.inserted_id)


def _sanitize_for_mongo(data: Any) -> Any:
    """Sanitize data for MongoDB storage (handle non-serializable types)."""
    if data is None:
        return None
    if isinstance(data, dict):
        return {k: _sanitize_for_mongo(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_sanitize_for_mongo(item) for item in data]
    if isinstance(data, (str, int, float, bool)):
        return data
    if isinstance(data, datetime):
        return data.isoformat()
    # Convert other types to string
    return str(data)


async def get_team_execution_logs(
    team_id: str,
    query: ExecutionLogQuery,
) -> Dict[str, Any]:
    """
    Get execution logs for a team with filtering and pagination.
    """
    filter_query = {"team_id": team_id}
    
    if query.engine:
        filter_query["engine"] = {"$regex": query.engine, "$options": "i"}
    
    if query.pipeline_id:
        filter_query["pipeline_id"] = query.pipeline_id
    
    if query.status:
        filter_query["status"] = query.status
    
    if query.source:
        filter_query["source"] = query.source
    
    if query.start_date:
        filter_query["created_at"] = {"$gte": query.start_date}
    
    if query.end_date:
        if "created_at" in filter_query:
            filter_query["created_at"]["$lte"] = query.end_date
        else:
            filter_query["created_at"] = {"$lte": query.end_date}
    
    # Get total count
    total = await execution_logs_collection().count_documents(filter_query)
    
    # Get paginated results
    cursor = execution_logs_collection().find(filter_query).sort(
        "created_at", -1
    ).skip(query.offset).limit(query.limit)
    
    logs = await cursor.to_list(length=query.limit)
    
    # Enrich with user emails and pipeline names
    result = []
    for log in logs:
        response = {
            "id": str(log["_id"]),
            "team_id": log["team_id"],
            "user_id": log["user_id"],
            "engine": log["engine"],
            "pipeline_id": log.get("pipeline_id"),
            "input_summary": _summarize_data(log.get("input_data")),
            "output_summary": _summarize_data(log.get("output_data")),
            "error_message": log.get("error_message"),
            "status": log["status"],
            "source": log.get("source", "direct"),
            "duration_ms": log.get("duration_ms", 0),
            "created_at": log["created_at"].isoformat() if isinstance(log["created_at"], datetime) else log["created_at"],
            "completed_at": log["completed_at"].isoformat() if log.get("completed_at") and isinstance(log["completed_at"], datetime) else log.get("completed_at"),
        }
        
        # Get user email
        if log["user_id"]:
            user = await users_collection().find_one(
                {"_id": ObjectId(log["user_id"])},
                {"email": 1}
            )
            if user:
                response["user_email"] = user["email"]
        
        # Get pipeline name
        if log.get("pipeline_id"):
            pipeline = await pipelines_collection().find_one(
                {"_id": ObjectId(log["pipeline_id"])},
                {"name": 1}
            )
            if pipeline:
                response["pipeline_name"] = pipeline["name"]
        
        result.append(response)
    
    return {
        "logs": result,
        "total": total,
        "limit": query.limit,
        "offset": query.offset,
    }


def _summarize_data(data: Any, max_length: int = 100) -> Optional[str]:
    """Create a brief summary of data for display."""
    if data is None:
        return None
    
    if isinstance(data, dict):
        # Get first few keys
        keys = list(data.keys())[:3]
        summary = ", ".join(f"{k}: ..." for k in keys)
        if len(data) > 3:
            summary += f" (+{len(data) - 3} more)"
        return summary
    
    if isinstance(data, str):
        if len(data) > max_length:
            return data[:max_length] + "..."
        return data
    
    return str(data)[:max_length]


async def get_team_execution_stats(team_id: str) -> Dict[str, Any]:
    """
    Get execution statistics for a team.
    """
    # Total counts
    total = await execution_logs_collection().count_documents({"team_id": team_id})
    success = await execution_logs_collection().count_documents({"team_id": team_id, "status": "success"})
    errors = await execution_logs_collection().count_documents({"team_id": team_id, "status": "error"})
    
    if total == 0:
        return {
            "total_executions": 0,
            "success_count": 0,
            "error_count": 0,
            "success_rate": 0,
            "avg_duration_ms": 0,
            "engines": {},
        }
    
    # Average duration
    pipeline = [
        {"$match": {"team_id": team_id}},
        {"$group": {"_id": None, "avg_duration": {"$avg": "$duration_ms"}}}
    ]
    avg_result = await execution_logs_collection().aggregate(pipeline).to_list(1)
    avg_duration = avg_result[0]["avg_duration"] if avg_result else 0
    
    # Count by engine
    engine_pipeline = [
        {"$match": {"team_id": team_id}},
        {"$group": {"_id": "$engine", "count": {"$sum": 1}}}
    ]
    engine_result = await execution_logs_collection().aggregate(engine_pipeline).to_list(100)
    engines = {r["_id"]: r["count"] for r in engine_result if r["_id"]}
    
    return {
        "total_executions": total,
        "success_count": success,
        "error_count": errors,
        "success_rate": round(success / total * 100, 1),
        "avg_duration_ms": round(avg_duration or 0, 0),
        "engines": engines,
    }


async def get_execution_log_detail(team_id: str, log_id: str) -> Optional[Dict[str, Any]]:
    """Get full details of a single execution log."""
    if not ObjectId.is_valid(log_id):
        return None
    
    log = await execution_logs_collection().find_one({
        "_id": ObjectId(log_id),
        "team_id": team_id,
    })
    
    if not log:
        return None
    
    result = {
        "id": str(log["_id"]),
        "team_id": log["team_id"],
        "user_id": log["user_id"],
        "engine": log["engine"],
        "pipeline_id": log.get("pipeline_id"),
        "input_data": log.get("input_data"),
        "output_data": log.get("output_data"),
        "error_message": log.get("error_message"),
        "status": log["status"],
        "source": log.get("source", "direct"),
        "duration_ms": log.get("duration_ms", 0),
        "endpoint": log.get("endpoint"),
        "method": log.get("method"),
        "created_at": log["created_at"].isoformat() if isinstance(log["created_at"], datetime) else log["created_at"],
        "completed_at": log["completed_at"].isoformat() if log.get("completed_at") and isinstance(log["completed_at"], datetime) else log.get("completed_at"),
    }
    
    # Get user email
    if log["user_id"]:
        user = await users_collection().find_one(
            {"_id": ObjectId(log["user_id"])},
            {"email": 1, "first_name": 1, "last_name": 1}
        )
        if user:
            result["user_email"] = user["email"]
            result["user_name"] = f"{user['first_name']} {user['last_name']}"
    
    return result
