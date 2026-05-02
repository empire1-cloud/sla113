"""
Usage Service
Tracks and enforces usage limits per team.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Dict
from bson import ObjectId

from database import teams_collection, get_database
from services.billing_service import get_plan_limits
from services.audit_service import create_audit_log


class UsageLimitError(Exception):
    """Exception raised when usage limit is exceeded."""
    def __init__(self, message: str, limit_type: str, current: int, limit: int):
        self.message = message
        self.limit_type = limit_type
        self.current = current
        self.limit = limit
        self.status_code = 429
        super().__init__(self.message)


def usage_records_collection():
    """Get usage records collection."""
    return get_database().usage_records


async def get_current_period_start() -> datetime:
    """Get the start of the current billing period (1st of month)."""
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


async def get_team_usage(team_id: str) -> Dict:
    """Get current usage for a team."""
    team = await teams_collection().find_one({"_id": ObjectId(team_id)})
    
    if not team:
        return {
            "executions_count": 0,
            "tokens_used": 0,
            "api_calls_count": 0,
        }
    
    usage = team.get("usage", {})
    period_start = await get_current_period_start()
    
    # Check if usage needs to be reset (new billing period)
    last_reset = usage.get("period_start")
    if last_reset and isinstance(last_reset, datetime):
        if last_reset.tzinfo is None:
            last_reset = last_reset.replace(tzinfo=timezone.utc)
        
        if last_reset < period_start:
            # Reset usage for new period
            await reset_team_usage(team_id)
            return {
                "executions_count": 0,
                "tokens_used": 0,
                "api_calls_count": 0,
                "period_start": period_start.isoformat(),
            }
    
    return {
        "executions_count": usage.get("executions_count", 0),
        "tokens_used": usage.get("tokens_used", 0),
        "api_calls_count": usage.get("api_calls_count", 0),
        "period_start": usage.get("period_start", period_start).isoformat() if usage.get("period_start") else period_start.isoformat(),
    }


async def get_team_usage_with_limits(team_id: str) -> Dict:
    """Get usage with plan limits for comparison."""
    team = await teams_collection().find_one({"_id": ObjectId(team_id)})
    
    if not team:
        return {
            "usage": {},
            "limits": get_plan_limits("free"),
            "plan": "free",
        }
    
    usage = await get_team_usage(team_id)
    plan = team.get("billing", {}).get("plan", "free")
    limits = get_plan_limits(plan)
    
    # Calculate percentages
    executions_percent = 0
    if limits["executions_per_month"] > 0:
        executions_percent = min(100, (usage["executions_count"] / limits["executions_per_month"]) * 100)
    elif limits["executions_per_month"] == -1:
        executions_percent = 0  # Unlimited
    
    return {
        "usage": usage,
        "limits": limits,
        "plan": plan,
        "percentages": {
            "executions": round(executions_percent, 1),
        },
        "over_limit": {
            "executions": limits["executions_per_month"] > 0 and usage["executions_count"] >= limits["executions_per_month"],
        },
    }


async def reset_team_usage(team_id: str):
    """Reset usage counters for a team (new billing period)."""
    period_start = await get_current_period_start()
    
    await teams_collection().update_one(
        {"_id": ObjectId(team_id)},
        {"$set": {
            "usage.executions_count": 0,
            "usage.tokens_used": 0,
            "usage.api_calls_count": 0,
            "usage.period_start": period_start,
            "usage.updated_at": datetime.now(timezone.utc),
        }}
    )


async def increment_usage(
    team_id: str,
    executions: int = 0,
    tokens: int = 0,
    api_calls: int = 0,
) -> Dict:
    """Increment usage counters for a team."""
    now = datetime.now(timezone.utc)
    period_start = await get_current_period_start()
    
    # First, ensure we're in the current period
    team = await teams_collection().find_one({"_id": ObjectId(team_id)})
    if team:
        usage = team.get("usage", {})
        last_reset = usage.get("period_start")
        
        if last_reset and isinstance(last_reset, datetime):
            if last_reset.tzinfo is None:
                last_reset = last_reset.replace(tzinfo=timezone.utc)
            
            if last_reset < period_start:
                await reset_team_usage(team_id)
    
    # Increment counters
    update = {
        "$inc": {},
        "$set": {
            "usage.updated_at": now,
        },
        "$setOnInsert": {
            "usage.period_start": period_start,
        }
    }
    
    if executions > 0:
        update["$inc"]["usage.executions_count"] = executions
    if tokens > 0:
        update["$inc"]["usage.tokens_used"] = tokens
    if api_calls > 0:
        update["$inc"]["usage.api_calls_count"] = api_calls
    
    await teams_collection().update_one(
        {"_id": ObjectId(team_id)},
        update,
    )
    
    # Return updated usage
    return await get_team_usage(team_id)


async def check_usage_limit(
    team_id: str,
    limit_type: str = "executions",
    increment: int = 1,
) -> bool:
    """
    Check if a usage limit would be exceeded.
    Returns True if within limit, raises UsageLimitError if exceeded.
    """
    team = await teams_collection().find_one({"_id": ObjectId(team_id)})
    
    if not team:
        return True
    
    plan = team.get("billing", {}).get("plan", "free")
    limits = get_plan_limits(plan)
    usage = await get_team_usage(team_id)
    
    if limit_type == "executions":
        limit = limits.get("executions_per_month", 100)
        current = usage.get("executions_count", 0)
        
        if limit == -1:  # Unlimited
            return True
        
        if current + increment > limit:
            raise UsageLimitError(
                f"Monthly execution limit reached ({current}/{limit}). Please upgrade your plan.",
                limit_type="executions",
                current=current,
                limit=limit,
            )
    
    elif limit_type == "team_members":
        limit = limits.get("team_members", 3)
        
        if limit == -1:
            return True
        
        from database import team_memberships_collection
        current = await team_memberships_collection().count_documents({
            "team_id": team_id,
            "is_active": True,
        })
        
        if current + increment > limit:
            raise UsageLimitError(
                f"Team member limit reached ({current}/{limit}). Please upgrade your plan.",
                limit_type="team_members",
                current=current,
                limit=limit,
            )
    
    elif limit_type == "api_keys":
        limit = limits.get("api_keys", 2)
        
        if limit == -1:
            return True
        
        current = await get_database().api_keys.count_documents({
            "team_id": team_id,
            "is_active": True,
        })
        
        if current + increment > limit:
            raise UsageLimitError(
                f"API key limit reached ({current}/{limit}). Please upgrade your plan.",
                limit_type="api_keys",
                current=current,
                limit=limit,
            )
    
    elif limit_type == "pipelines":
        limit = limits.get("pipelines", 5)
        
        if limit == -1:
            return True
        
        from database import pipelines_collection
        current = await pipelines_collection().count_documents({
            "team_id": team_id,
            "is_active": {"$ne": False},
        })
        
        if current + increment > limit:
            raise UsageLimitError(
                f"Pipeline limit reached ({current}/{limit}). Please upgrade your plan.",
                limit_type="pipelines",
                current=current,
                limit=limit,
            )
    
    return True


async def record_execution(
    team_id: str,
    user_id: str,
    engine: str,
    tokens_used: int = 0,
    success: bool = True,
):
    """
    Record an engine execution for usage tracking.
    Call this after each successful engine execution.
    """
    # Check limit first
    await check_usage_limit(team_id, "executions", 1)
    
    # Increment usage
    await increment_usage(
        team_id=team_id,
        executions=1,
        tokens=tokens_used,
    )
    
    # Store detailed record for analytics
    await usage_records_collection().insert_one({
        "team_id": team_id,
        "user_id": user_id,
        "engine": engine,
        "tokens_used": tokens_used,
        "success": success,
        "created_at": datetime.now(timezone.utc),
    })
