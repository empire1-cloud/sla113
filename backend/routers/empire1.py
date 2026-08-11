"""Empire1 — ecosystem registry + showcase analytics."""
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import uuid
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database.connection import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/empire1", tags=["empire1"])


def ecosystem_collection():
    return get_database()["empire1_ecosystem"]


def analytics_collection():
    return get_database()["empire1_showcase_analytics"]


# ─── ECOSYSTEM REGISTRY ───────────────────────────────────────────────

class EcosystemRepo(BaseModel):
    id: str                   # slug: empire1, ecosystem, lyrica, cultura, sla113
    name: str
    tag: str
    color: str
    desc: str
    status: str = "linked"    # linked | live | building
    deeplink: Optional[str] = None
    repo_url: Optional[str] = None
    production_url: Optional[str] = None


DEFAULT_ECOSYSTEM = [
    {"id": "empire1", "name": "Empire 1", "tag": "Control Plane", "color": "#3b82ff",
     "desc": "Hybrid Intelligence Core orchestrating 15+ specialized AI engines.",
     "status": "live", "deeplink": "/", "repo_url": None, "production_url": None},
    {"id": "ecosystem", "name": "Empire-Lyrica", "tag": "Integration Layer", "color": "#ff2d92",
     "desc": "Cross-app glue. Shared auth, billing, agent runtime.",
     "status": "linked", "deeplink": None, "repo_url": None, "production_url": None},
    {"id": "lyrica", "name": "Lyrica 3 Pro", "tag": "Sonic IP", "color": "#00c8ff",
     "desc": "Music, lyrics, audio generation pillar.",
     "status": "linked", "deeplink": None, "repo_url": None, "production_url": None},
    {"id": "cultura", "name": "Cultura Vibe Forge", "tag": "Cultural IP", "color": "#ff4488",
     "desc": "Aztec, Chicano, SGV, IELA aesthetic engine.",
     "status": "linked", "deeplink": None, "repo_url": None, "production_url": None},
    {"id": "sla113", "name": "SLA113", "tag": "Arcade OS", "color": "#4488ff",
     "desc": "Sovereign game compiler + public arcade portal.",
     "status": "live", "deeplink": "/sla113", "repo_url": None, "production_url": None},
]


async def seed_ecosystem():
    count = await ecosystem_collection().count_documents({})
    if count > 0:
        return
    now = datetime.now(timezone.utc).isoformat()
    for r in DEFAULT_ECOSYSTEM:
        await ecosystem_collection().insert_one({**r, "created_at": now, "updated_at": now})
    logger.info("Seeded %d default ecosystem repos", len(DEFAULT_ECOSYSTEM))


@router.get("/ecosystem")
async def list_ecosystem():
    cursor = ecosystem_collection().find({}, {"_id": 0}).sort("name", 1)
    repos = await cursor.to_list(50)
    return {"repos": repos, "total": len(repos)}


@router.patch("/ecosystem/{repo_id}")
async def update_ecosystem_repo(repo_id: str, body: Dict[str, Any]):
    body.pop("id", None); body.pop("_id", None)
    body["updated_at"] = datetime.now(timezone.utc).isoformat()
    # If production_url is set and status not explicit, flip to live
    if body.get("production_url") and "status" not in body:
        body["status"] = "live"
        body["deeplink"] = body["production_url"]
    result = await ecosystem_collection().update_one({"id": repo_id}, {"$set": body})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Repo not found")
    return await ecosystem_collection().find_one({"id": repo_id}, {"_id": 0})


# ─── SHOWCASE ANALYTICS ───────────────────────────────────────────────

class AnalyticsEvent(BaseModel):
    type: str                 # view | cta_click | scroll_depth | demo_run | demo_open_standalone
    meta: Dict[str, Any] = {}
    session_id: Optional[str] = None
    referrer: Optional[str] = None
    ua: Optional[str] = None


@router.post("/analytics/event")
async def log_event(ev: AnalyticsEvent):
    doc = {
        "id": uuid.uuid4().hex,
        "type": ev.type,
        "meta": ev.meta,
        "session_id": ev.session_id,
        "referrer": ev.referrer,
        "ua": (ev.ua or "")[:300],
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    await analytics_collection().insert_one(doc)
    return {"ok": True, "id": doc["id"]}


@router.get("/analytics/summary")
async def analytics_summary():
    coll = analytics_collection()
    total = await coll.count_documents({})
    by_type_cursor = coll.aggregate([
        {"$group": {"_id": "$type", "n": {"$sum": 1}}},
        {"$sort": {"n": -1}},
    ])
    by_type = [{"type": d["_id"], "count": d["n"]} async for d in by_type_cursor]
    # CTA clicks breakdown
    cta_cursor = coll.aggregate([
        {"$match": {"type": "cta_click"}},
        {"$group": {"_id": "$meta.target", "n": {"$sum": 1}}},
        {"$sort": {"n": -1}},
    ])
    ctas = [{"target": d["_id"], "count": d["n"]} async for d in cta_cursor]
    # Max scroll depth distribution
    depth_cursor = coll.aggregate([
        {"$match": {"type": "scroll_depth"}},
        {"$group": {"_id": "$meta.depth", "n": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ])
    depths = [{"depth": d["_id"], "count": d["n"]} async for d in depth_cursor]
    # Unique sessions
    sessions = await coll.distinct("session_id")
    return {
        "total_events": total,
        "unique_sessions": len([s for s in sessions if s]),
        "by_type": by_type,
        "cta_clicks": ctas,
        "scroll_depth": depths,
    }
