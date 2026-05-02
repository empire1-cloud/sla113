"""
Database connection and initialization for MongoDB.
Production-ready with connection pooling and error handling.
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Global database client
_client: Optional[AsyncIOMotorClient] = None
_db = None


def get_mongo_url() -> str:
    """Get MongoDB URL from environment."""
    url = os.environ.get("MONGO_URL")
    if not url:
        raise ValueError("MONGO_URL environment variable is required")
    return url


def get_db_name() -> str:
    """Get database name from environment."""
    name = os.environ.get("DB_NAME")
    if not name:
        raise ValueError("DB_NAME environment variable is required")
    return name


async def connect_to_database():
    """Initialize database connection with connection pooling."""
    global _client, _db
    
    if _client is not None:
        return
    
    mongo_url = get_mongo_url()
    db_name = get_db_name()
    
    logger.info(f"Connecting to MongoDB database: {db_name}")
    
    _client = AsyncIOMotorClient(
        mongo_url,
        maxPoolSize=50,
        minPoolSize=10,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
    )
    
    _db = _client[db_name]
    
    # Create indexes
    await create_indexes()
    
    logger.info("Database connection established successfully")


async def close_database_connection():
    """Close database connection."""
    global _client, _db
    
    if _client is not None:
        _client.close()
        _client = None
        _db = None
        logger.info("Database connection closed")


def get_database():
    """Get database instance."""
    if _db is None:
        raise RuntimeError("Database not initialized. Call connect_to_database() first.")
    return _db


async def create_indexes():
    """Create all required database indexes."""
    db = get_database()
    
    # Users collection indexes
    await db.users.create_indexes([
        IndexModel([("email", ASCENDING)], unique=True),
        IndexModel([("system_role", ASCENDING)]),
        IndexModel([("is_active", ASCENDING)]),
        IndexModel([("created_at", DESCENDING)]),
    ])
    
    # Teams collection indexes
    await db.teams.create_indexes([
        IndexModel([("slug", ASCENDING)], unique=True),
        IndexModel([("owner_id", ASCENDING)]),
        IndexModel([("type", ASCENDING)]),
        IndexModel([("is_active", ASCENDING)]),
    ])
    
    # Team memberships indexes
    await db.team_memberships.create_indexes([
        IndexModel([("user_id", ASCENDING), ("team_id", ASCENDING)], unique=True),
        IndexModel([("user_id", ASCENDING)]),
        IndexModel([("team_id", ASCENDING)]),
        IndexModel([("role", ASCENDING)]),
        IndexModel([("is_active", ASCENDING)]),
    ])
    
    # Sessions indexes
    await db.sessions.create_indexes([
        IndexModel([("user_id", ASCENDING)]),
        IndexModel([("refresh_token_hash", ASCENDING)], unique=True),
        IndexModel([("expires_at", ASCENDING)]),
        IndexModel([("is_active", ASCENDING)]),
    ])
    
    # Team invites indexes
    await db.team_invites.create_indexes([
        IndexModel([("token_hash", ASCENDING)], unique=True),
        IndexModel([("team_id", ASCENDING)]),
        IndexModel([("email", ASCENDING)]),
        IndexModel([("expires_at", ASCENDING)]),
        IndexModel([("is_active", ASCENDING)]),
    ])
    
    # Audit logs indexes
    await db.audit_logs.create_indexes([
        IndexModel([("user_id", ASCENDING)]),
        IndexModel([("team_id", ASCENDING)]),
        IndexModel([("action", ASCENDING)]),
        IndexModel([("resource_type", ASCENDING)]),
        IndexModel([("created_at", DESCENDING)]),
    ])
    
    # Pipelines indexes (team-scoped)
    await db.pipelines.create_indexes([
        IndexModel([("team_id", ASCENDING)]),
        IndexModel([("created_by", ASCENDING)]),
        IndexModel([("is_active", ASCENDING)]),
        IndexModel([("created_at", DESCENDING)]),
    ])
    
    # Execution logs indexes (team-scoped)
    await db.execution_logs.create_indexes([
        IndexModel([("team_id", ASCENDING)]),
        IndexModel([("user_id", ASCENDING)]),
        IndexModel([("engine", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("created_at", DESCENDING)]),
    ])
    
    # Password reset tokens indexes
    await db.password_reset_tokens.create_indexes([
        IndexModel([("token_hash", ASCENDING)], unique=True),
        IndexModel([("email", ASCENDING)]),
        IndexModel([("expires_at", ASCENDING)]),
        IndexModel([("ip_address", ASCENDING)]),
        IndexModel([("created_at", DESCENDING)]),
    ])
    
    logger.info("Database indexes created successfully")


# Collection accessors for type hints
def users_collection():
    return get_database().users

def teams_collection():
    return get_database().teams

def team_memberships_collection():
    return get_database().team_memberships

def sessions_collection():
    return get_database().sessions

def team_invites_collection():
    return get_database().team_invites

def audit_logs_collection():
    return get_database().audit_logs

def pipelines_collection():
    return get_database().pipelines

def execution_logs_collection():
    return get_database().execution_logs

def password_reset_tokens_collection():
    return get_database().password_reset_tokens
