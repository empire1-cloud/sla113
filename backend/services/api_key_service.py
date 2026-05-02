"""
API Keys Service
Manages API keys for programmatic access.
"""

import secrets
import hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, List
from bson import ObjectId

from database import get_database
from services.usage_service import check_usage_limit
from services.audit_service import create_audit_log


class APIKeyError(Exception):
    """Custom exception for API key errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def api_keys_collection():
    """Get API keys collection."""
    return get_database().api_keys


def generate_api_key() -> tuple[str, str]:
    """Generate a secure API key and its hash."""
    # Format: hic_<random>  (Hybrid Intelligence Core)
    raw_key = f"hic_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, key_hash


def hash_api_key(key: str) -> str:
    """Hash an API key for storage/lookup."""
    return hashlib.sha256(key.encode()).hexdigest()


def mask_api_key(key: str) -> str:
    """Return masked version of API key for display."""
    if len(key) < 10:
        return "***"
    return f"{key[:7]}...{key[-4:]}"


async def create_api_key(
    team_id: str,
    name: str,
    user_id: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict:
    """
    Create a new API key for a team.
    Returns the raw key - this is the only time it will be visible!
    """
    # Check limit
    await check_usage_limit(team_id, "api_keys", 1)
    
    # Check for duplicate name
    existing = await api_keys_collection().find_one({
        "team_id": team_id,
        "name": name,
        "is_active": True,
    })
    
    if existing:
        raise APIKeyError(f"An API key named '{name}' already exists", 400)
    
    raw_key, key_hash = generate_api_key()
    now = datetime.now(timezone.utc)
    
    key_doc = {
        "team_id": team_id,
        "name": name,
        "key_hash": key_hash,
        "key_prefix": raw_key[:11],  # hic_XXXX for identification
        "created_by": user_id,
        "created_at": now,
        "last_used_at": None,
        "revoked_at": None,
        "is_active": True,
    }
    
    result = await api_keys_collection().insert_one(key_doc)
    
    # Audit log
    await create_audit_log(
        user_id=user_id,
        team_id=team_id,
        action="api_key.created",
        resource_type="api_key",
        resource_id=str(result.inserted_id),
        details={"name": name},
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    return {
        "id": str(result.inserted_id),
        "name": name,
        "key": raw_key,  # Only returned once!
        "key_prefix": raw_key[:11],
        "created_at": now.isoformat(),
    }


async def list_api_keys(team_id: str) -> List[Dict]:
    """List all API keys for a team."""
    keys = await api_keys_collection().find(
        {"team_id": team_id, "is_active": True},
        {"key_hash": 0}  # Never return hash
    ).sort("created_at", -1).to_list(100)
    
    return [
        {
            "id": str(k["_id"]),
            "name": k["name"],
            "key_prefix": k.get("key_prefix", "hic_****"),
            "created_at": k["created_at"].isoformat() if isinstance(k["created_at"], datetime) else k["created_at"],
            "last_used_at": k["last_used_at"].isoformat() if k.get("last_used_at") and isinstance(k["last_used_at"], datetime) else k.get("last_used_at"),
            "created_by": k.get("created_by"),
        }
        for k in keys
    ]


async def revoke_api_key(
    team_id: str,
    key_id: str,
    user_id: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict:
    """Revoke an API key."""
    key = await api_keys_collection().find_one({
        "_id": ObjectId(key_id),
        "team_id": team_id,
        "is_active": True,
    })
    
    if not key:
        raise APIKeyError("API key not found", 404)
    
    now = datetime.now(timezone.utc)
    
    await api_keys_collection().update_one(
        {"_id": ObjectId(key_id)},
        {"$set": {
            "is_active": False,
            "revoked_at": now,
            "revoked_by": user_id,
        }}
    )
    
    # Audit log
    await create_audit_log(
        user_id=user_id,
        team_id=team_id,
        action="api_key.revoked",
        resource_type="api_key",
        resource_id=key_id,
        details={"name": key["name"]},
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    return {"message": f"API key '{key['name']}' revoked"}


async def validate_api_key(key: str) -> Optional[Dict]:
    """
    Validate an API key and return team info if valid.
    Updates last_used_at on successful validation.
    """
    if not key:
        return None
    
    # Handle Bearer prefix
    if key.startswith("Bearer "):
        key = key[7:]
    
    # Validate format
    if not key.startswith("hic_"):
        return None
    
    key_hash = hash_api_key(key)
    
    key_doc = await api_keys_collection().find_one({
        "key_hash": key_hash,
        "is_active": True,
    })
    
    if not key_doc:
        return None
    
    # Update last used
    now = datetime.now(timezone.utc)
    await api_keys_collection().update_one(
        {"_id": key_doc["_id"]},
        {"$set": {"last_used_at": now}}
    )
    
    return {
        "team_id": key_doc["team_id"],
        "key_id": str(key_doc["_id"]),
        "key_name": key_doc["name"],
    }


async def get_api_key_context(key: str) -> Optional[Dict]:
    """
    Get full context for API key authentication.
    Used by auth dependency.
    """
    key_info = await validate_api_key(key)
    
    if not key_info:
        return None
    
    from database import teams_collection, users_collection, team_memberships_collection
    
    team = await teams_collection().find_one({"_id": ObjectId(key_info["team_id"])})
    
    if not team:
        return None
    
    # Get team owner as the effective user
    owner_membership = await team_memberships_collection().find_one({
        "team_id": key_info["team_id"],
        "role": "owner",
        "is_active": True,
    })
    
    user_id = owner_membership["user_id"] if owner_membership else team.get("owner_id")
    
    user = await users_collection().find_one({"_id": ObjectId(user_id)})
    
    return {
        "user_id": user_id,
        "team_id": key_info["team_id"],
        "team_name": team["name"],
        "api_key_id": key_info["key_id"],
        "api_key_name": key_info["key_name"],
        "user_email": user["email"] if user else None,
        "is_api_key_auth": True,
    }
