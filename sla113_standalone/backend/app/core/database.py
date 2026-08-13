"""SLA113 Database Connection — MongoDB via Motor (with mock fallback).

╔═══════════════════════════════════════════════════════════════════╗
║  COLLISION GUARD                                                 ║
║  connect_to_database() refuses to boot if DB_NAME matches any    ║
║  known monolith database name. This prevents the standalone      ║
║  from silently corrupting live deployment data.                  ║
║                                                                  ║
║  Override with COLLISION_BYPASS=true env var for migration.      ║
╚═══════════════════════════════════════════════════════════════════╝
"""
import logging
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings

logger = logging.getLogger(__name__)

_client = None
_db = None

PROTECTED_DB_NAMES = frozenset({
    "sla113",        # Monolith .env: DB_NAME=sla113
    "sla113_db",     # Old standalone default (v1.0.0)
})


async def connect_to_database():
    global _client, _db
    settings = get_settings()
    db_name = settings.DB_NAME

    _guard_collision(db_name)

    try:
        _client = AsyncIOMotorClient(
            settings.MONGO_URL,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
        )
        await _client.admin.command("ping")
        _db = _client[db_name]
        logger.info(f"Connected to MongoDB: {db_name}")
    except Exception as e:
        logger.warning(f"MongoDB unavailable ({e}) — using in-memory mock")
        from mongomock_motor import AsyncMongoMockClient
        _client = AsyncMongoMockClient()
        _db = _client[db_name]


def _guard_collision(db_name: str):
    """Hard abort if DB_NAME matches a known monolith database name."""
    bypass = os.environ.get("COLLISION_BYPASS", "").lower() in ("true", "1", "yes")
    if bypass:
        logger.warning(
            f"COLLISION_BYPASS is set — connecting to DB '{db_name}' "
            f"even though it matches protected name(s). This should only "
            f"be used during migration."
        )
        return
    if db_name in PROTECTED_DB_NAMES:
        raise RuntimeError(
            f"\n"
            f"╔══════════════════════════════════════════════════════╗\n"
            f"║  SAFETY GUARD TRIGGERED                              ║\n"
            f"╠══════════════════════════════════════════════════════╣\n"
            f"║  DB_NAME='{db_name}' matches a known                ║\n"
            f"║  monolith database name. Connecting would            ║\n"
            f"║  corrupt live deployment data.                       ║\n"
            f"║                                                      ║\n"
            f"║  Fix: Set DB_NAME to a unique value                 ║\n"
            f"║  (e.g., 'sla113_standalone' which is the default).  ║\n"
            f"║                                                      ║\n"
            f"║  Migration override: COLLISION_BYPASS=true           ║\n"
            f"╚══════════════════════════════════════════════════════╝"
        )


async def close_database_connection():
    global _client
    if _client:
        _client.close()
        logger.info("Database connection closed")


def get_database():
    if _db is None:
        raise RuntimeError("Database not initialized. Call connect_to_database() first.")
    return _db
