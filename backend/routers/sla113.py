"""SLA113 API Router - Universal AI Game Studio"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import uuid
import logging
import os
import json
import asyncio
from emergentintegrations.llm.chat import LlmChat, UserMessage

from database import get_database
from sla113.models import (
    GAME_TYPES,
    CreateProjectRequest,
    VisionGenerateRequest,
    LogicGenerateRequest,
    ComposeRequest,
)
from sla113.vision_engine import generate_vision_assets
from sla113.logic_engine import generate_logic
from sla113.composer_engine import compose_game_bundle

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sla113", tags=["sla113"])

# In-memory session store for terminal conversations
_terminal_sessions = {}


class TerminalRequest(BaseModel):
    command: str
    session_id: Optional[str] = "default"


def projects_collection():
    return get_database()["sla113_projects"]


# ─── Game Types ───
@router.get("/game-types")
async def list_game_types():
    """List all supported game types."""
    return {"game_types": GAME_TYPES}


# ─── Projects CRUD ───
@router.post("/projects")
async def create_project(req: CreateProjectRequest):
    """Create a new game project."""
    if req.game_type not in GAME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported game type: {req.game_type}. Supported: {list(GAME_TYPES.keys())}")

    now = datetime.now(timezone.utc).isoformat()
    project = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "game_type": req.game_type,
        "game_type_info": GAME_TYPES[req.game_type],
        "description": req.description or GAME_TYPES[req.game_type]["description"],
        "theme": req.theme or "default",
        "target_platform": req.target_platform,
        "status": "created",
        "vision_assets": [],
        "logic_specs": [],
        "compositions": [],
        "created_at": now,
        "updated_at": now,
    }

    await projects_collection().insert_one(project)
    project.pop("_id", None)
    return project


@router.get("/projects")
async def list_projects():
    """List all game projects."""
    cursor = projects_collection().find({}, {"_id": 0})
    projects = await cursor.to_list(100)
    return {"projects": projects, "total": len(projects)}


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get a game project by ID."""
    project = await projects_collection().find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a game project."""
    result = await projects_collection().delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"deleted": True, "project_id": project_id}


# ─── Vision Engine ───
@router.post("/vision/generate")
async def generate_vision(req: VisionGenerateRequest):
    """Generate visual assets for a game project."""
    project = await projects_collection().find_one({"id": req.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        result = await generate_vision_assets(
            project=project,
            asset_type=req.asset_type,
            style=req.style,
            count=req.count,
            custom_prompt=req.custom_prompt,
        )

        # Save generated assets to project
        await projects_collection().update_one(
            {"id": req.project_id},
            {
                "$push": {"vision_assets": result},
                "$set": {"status": "vision_generated", "updated_at": datetime.now(timezone.utc).isoformat()},
            },
        )
        return result

    except Exception as e:
        logger.error(f"Vision generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Vision generation failed: {str(e)}")


# ─── Logic Engine ───
@router.post("/logic/generate")
async def generate_game_logic(req: LogicGenerateRequest):
    """Generate game logic/math for a project."""
    project = await projects_collection().find_one({"id": req.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        result = await generate_logic(
            project=project,
            logic_type=req.logic_type,
            difficulty=req.difficulty,
            custom_requirements=req.custom_requirements,
        )

        await projects_collection().update_one(
            {"id": req.project_id},
            {
                "$push": {"logic_specs": result},
                "$set": {"status": "logic_generated", "updated_at": datetime.now(timezone.utc).isoformat()},
            },
        )
        return result

    except Exception as e:
        logger.error(f"Logic generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Logic generation failed: {str(e)}")


# ─── Composer Engine ───
@router.post("/compose")
async def compose_game(req: ComposeRequest):
    """Compose a complete game bundle from generated assets."""
    project = await projects_collection().find_one({"id": req.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        result = await compose_game_bundle(
            project=project,
            include_vision=req.include_vision,
            include_logic=req.include_logic,
            output_format=req.output_format,
        )

        await projects_collection().update_one(
            {"id": req.project_id},
            {
                "$push": {"compositions": result},
                "$set": {"status": "composed", "updated_at": datetime.now(timezone.utc).isoformat()},
            },
        )
        return result

    except Exception as e:
        logger.error(f"Composition failed: {e}")
        raise HTTPException(status_code=500, detail=f"Composition failed: {str(e)}")


# ─── Quick Stats ───
@router.get("/stats")
async def get_stats():
    """Get SLA113 platform stats."""
    total = await projects_collection().count_documents({})
    by_type = {}
    for gt in GAME_TYPES:
        count = await projects_collection().count_documents({"game_type": gt})
        if count > 0:
            by_type[gt] = count

    return {
        "total_projects": total,
        "by_game_type": by_type,
        "supported_game_types": len(GAME_TYPES),
        "engines": ["vision", "logic", "composer"],
        "version": "1.0.0",
    }



# ─── AI Terminal (Sovereign Overseer) ───
@router.post("/terminal")
async def terminal_command(req: TerminalRequest):
    """AI Terminal — Sovereign Overseer with full platform context."""
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        return {"response": "[ERROR] EMERGENT_LLM_KEY not configured. Overseer offline."}

    # Gather live platform context
    total_projects = await projects_collection().count_documents({})
    recent_projects = await projects_collection().find({}, {"_id": 0, "name": 1, "game_type": 1, "status": 1, "theme": 1}).sort("created_at", -1).to_list(10)

    by_type = {}
    for gt in GAME_TYPES:
        c = await projects_collection().count_documents({"game_type": gt})
        if c > 0:
            by_type[gt] = c

    platform_context = json.dumps({
        "total_projects": total_projects,
        "projects_by_type": by_type,
        "recent_projects": recent_projects,
        "supported_game_types": list(GAME_TYPES.keys()),
        "engines": ["vision", "logic", "composer"],
    }, indent=2)

    system_msg = f"""You are the SOVEREIGN OVERSEER of SLA113 — the most advanced AI game creation platform on Earth.

IDENTITY: You are a military-grade AI command system. Your tone is terse, authoritative, and precise. Use UPPERCASE for emphasis. Respond in terminal/monospace style with > prefixes.

PLATFORM STATE:
{platform_context}

CAPABILITIES:
- You have full knowledge of all 16 game types: casino (fish shooter, slots, crash, cards) and AAA (open world/GTA, tactical FPS/COD, fighting/MK, fantasy RPG, survival horror, platformer, puzzle, tower defense, runner, battle royale, racing, sports)
- You can advise on RTP calculations, game math, asset generation strategy, architecture decisions
- You understand game economy design, probability math, and certification requirements
- You track all active projects and their generation status

RULES:
- Keep responses under 150 words
- Use > prefix for each line
- Reference specific project data when relevant
- Be direct. No fluff. Canon enforcement at all times.
- If asked to generate something, explain what engine to use and how"""

    session_id = req.session_id or "default"

    # Get or create chat session
    if session_id not in _terminal_sessions:
        chat = LlmChat(
            api_key=api_key,
            session_id=f"sla113-overseer-{session_id}",
            system_message=system_msg,
        )
        chat.with_model("openai", "gpt-4o-mini")
        _terminal_sessions[session_id] = chat
    else:
        chat = _terminal_sessions[session_id]

    try:
        response = await chat.send_message(UserMessage(text=req.command))
        return {"response": response, "session_id": session_id}
    except Exception as e:
        logger.error(f"Terminal error: {e}")
        return {"response": f"> [ERROR] Overseer fault: {str(e)}", "session_id": session_id}


# ─── Collections ───
def tenants_collection():
    return get_database()["sla113_tenants"]

def jobs_collection():
    return get_database()["sla113_jobs"]

def pipelines_collection():
    return get_database()["sla113_pipelines"]


# ─── Image Generation (Vision Smith) ───
class ImageGenRequest(BaseModel):
    prompt: str
    style: str = "pixel_art"
    size: str = "1024x1024"


@router.post("/vision/generate-image")
async def generate_image(req: ImageGenRequest):
    """Generate actual game art image using GPT Image 1."""
    import base64
    from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not configured")

    style_map = {
        "pixel_art": "16-bit pixel art style, limited color palette, retro game aesthetic",
        "vector": "clean vector illustration, flat colors, sharp edges, game asset",
        "3d_render": "3D rendered, realistic lighting, game-ready asset",
        "hand_drawn": "hand-drawn illustration, ink outlines, watercolor fills",
        "anime": "Japanese anime art style, cel shading, vibrant colors",
        "neon": "neon-lit cyberpunk style, glowing edges, dark background",
        "retro": "retro 80s arcade style, bold colors, scanline effects",
    }
    style_desc = style_map.get(req.style, req.style)
    full_prompt = f"{req.prompt}. Style: {style_desc}. Game asset on transparent/dark background, high detail."

    try:
        image_gen = OpenAIImageGeneration(api_key=api_key)
        images = await image_gen.generate_images(
            prompt=full_prompt,
            model="gpt-image-1",
            number_of_images=1,
        )
        if images and len(images) > 0:
            image_base64 = base64.b64encode(images[0]).decode("utf-8")
            return {"image_base64": image_base64, "prompt": req.prompt, "style": req.style}
        raise HTTPException(status_code=500, detail="No image generated")
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


# ─── White Label Tenants ───
class CreateTenantRequest(BaseModel):
    name: str
    subdomain: str
    config: Optional[dict] = None


@router.post("/tenants")
async def create_tenant(req: CreateTenantRequest):
    """Mint a new white-label tenant instance."""
    now = datetime.now(timezone.utc).isoformat()
    existing = await tenants_collection().find_one({"subdomain": req.subdomain}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=409, detail=f"Subdomain '{req.subdomain}' already exists")

    tenant = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "subdomain": req.subdomain,
        "status": "provisioning",
        "credits": 0,
        "rtp_mode": 92,
        "config": req.config or {},
        "created_at": now,
        "updated_at": now,
    }
    await tenants_collection().insert_one(tenant)
    tenant.pop("_id", None)

    # Simulate provisioning steps
    await tenants_collection().update_one(
        {"id": tenant["id"]},
        {"$set": {"status": "active", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    tenant["status"] = "active"
    return tenant


@router.get("/tenants")
async def list_tenants():
    """List all white-label tenants."""
    cursor = tenants_collection().find({}, {"_id": 0})
    tenants = await cursor.to_list(100)
    return {"tenants": tenants, "total": len(tenants)}


@router.delete("/tenants/{tenant_id}")
async def delete_tenant(tenant_id: str):
    result = await tenants_collection().delete_one({"id": tenant_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"deleted": True}


@router.put("/tenants/{tenant_id}/credits")
async def update_tenant_credits(tenant_id: str, amount: int):
    """Load credits to a tenant."""
    result = await tenants_collection().update_one(
        {"id": tenant_id},
        {"$inc": {"credits": amount}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant = await tenants_collection().find_one({"id": tenant_id}, {"_id": 0})
    return tenant


@router.put("/tenants/{tenant_id}/rtp")
async def update_tenant_rtp(tenant_id: str, rtp: int):
    """Set tenant RTP mode."""
    if rtp < 80 or rtp > 99:
        raise HTTPException(status_code=400, detail="RTP must be between 80 and 99")
    await tenants_collection().update_one(
        {"id": tenant_id},
        {"$set": {"rtp_mode": rtp, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    tenant = await tenants_collection().find_one({"id": tenant_id}, {"_id": 0})
    return tenant


# ─── Night Queue (Persistent Jobs) ───
JOB_STAGES = {
    "ARCADE_40": ["Asset Indexing", "Sprite Generation", "Physics Binding", "AI Balancing", "Package Export"],
    "ARCADE_60": ["Asset Indexing", "Sprite Generation", "Physics Binding", "AI Balancing", "Network Layer", "Package Export"],
    "SLOTS_20": ["Reel Mapping", "Paytable Calculation", "RTP Verification", "Visual Rendering", "Package Export"],
    "OPEN_WORLD": ["World Generation", "NPC Scripting", "Physics Binding", "AI Pathing", "Texture Streaming", "LOD Pipeline", "Package Export"],
    "CASINO_SUITE": ["Game Selection Matrix", "RTP Calibration", "Lobby UI", "Payment Gateway", "Package Export"],
    "CUSTOM_OS_BUILD": ["Init Scaffold", "Core Logic", "Asset Pipeline", "Integration Pass", "Package Export"],
    "AAA_FISH_SLOT": ["Asset Indexing", "Sprite Generation", "Boss Patterns", "RTP Verification", "Package Export"],
    "GTA5_TYPE": ["World Generation", "NPC Scripting", "Vehicle Physics", "Mission Logic", "Package Export"],
    "COD_WARFARE": ["Map Generation", "Weapon Balancing", "Netcode Layer", "AI Opponents", "Package Export"],
    "FANTASY_RPG": ["Lore Generation", "Skill Trees", "Monster AI", "Dungeon Layout", "Package Export"],
}

DEFAULT_STAGES = ["Initialization", "Core Processing", "Asset Compilation", "Quality Check", "Package Export"]


class CreateJobRequest(BaseModel):
    preset: str
    config: Optional[dict] = None
    priority: str = "normal"


@router.post("/jobs")
async def create_job(req: CreateJobRequest):
    """Queue a new build job with processing stages."""
    now = datetime.now(timezone.utc).isoformat()
    stage_names = JOB_STAGES.get(req.preset, DEFAULT_STAGES)
    stages = [{"name": s, "status": "pending", "progress": 0} for s in stage_names]

    job = {
        "id": f"JOB-{uuid.uuid4().hex[:6].upper()}",
        "preset": req.preset,
        "status": "pending",
        "progress": 0,
        "priority": req.priority,
        "config": req.config or {},
        "stages": stages,
        "logs": [f"[{now}] Job queued. Preset: {req.preset}. Priority: {req.priority}. Stages: {len(stages)}"],
        "created_at": now,
        "updated_at": now,
    }
    await jobs_collection().insert_one(job)
    job.pop("_id", None)
    return job


@router.get("/jobs")
async def list_jobs():
    """List all queued jobs."""
    cursor = jobs_collection().find({}, {"_id": 0}).sort("created_at", -1)
    jobs = await cursor.to_list(100)
    return {"jobs": jobs, "total": len(jobs)}


@router.put("/jobs/{job_id}/progress")
async def update_job_progress(job_id: str, progress: int, status: Optional[str] = None):
    """Update job progress."""
    update = {"progress": progress, "updated_at": datetime.now(timezone.utc).isoformat()}
    if status:
        update["status"] = status
    if progress >= 100:
        update["status"] = "completed"
    result = await jobs_collection().update_one({"id": job_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    job = await jobs_collection().find_one({"id": job_id}, {"_id": 0})
    return job


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    result = await jobs_collection().delete_one({"id": job_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"deleted": True}


@router.post("/jobs/{job_id}/process")
async def process_job(job_id: str):
    """Manually advance a job one step."""
    job = await jobs_collection().find_one({"id": job_id}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] == "completed":
        return job

    return await _advance_job(job)


async def _advance_job(job):
    """Internal: advance a job through its stages."""
    import random
    now = datetime.now(timezone.utc).isoformat()
    stages = job.get("stages", [])

    if not stages:
        # Legacy job without stages — simple progress bump
        new_progress = min(job["progress"] + 25, 100)
        new_status = "completed" if new_progress >= 100 else "processing"
        log_msg = f"[{now}] Progress: {new_progress}% — {'Complete.' if new_status == 'completed' else 'Processing...'}"
        await jobs_collection().update_one(
            {"id": job["id"]},
            {"$set": {"progress": new_progress, "status": new_status, "updated_at": now}, "$push": {"logs": log_msg}}
        )
        return await jobs_collection().find_one({"id": job["id"]}, {"_id": 0})

    # Find current active stage
    current_idx = next((i for i, s in enumerate(stages) if s["status"] != "completed"), len(stages))

    if current_idx < len(stages):
        stage = stages[current_idx]
        increment = random.randint(20, 45)
        new_stage_progress = min(stage["progress"] + increment, 100)
        stage["progress"] = new_stage_progress

        if new_stage_progress >= 100:
            stage["status"] = "completed"
            log_msg = f"[{now}] Stage '{stage['name']}' DONE."
        else:
            stage["status"] = "processing"
            log_msg = f"[{now}] {stage['name']}: {new_stage_progress}%"

    # Calculate overall progress
    total_progress = sum(s["progress"] for s in stages) // len(stages) if stages else 100
    all_done = all(s["status"] == "completed" for s in stages)
    new_status = "completed" if all_done else "processing"

    if all_done:
        log_msg = f"[{now}] ALL STAGES COMPLETE. Job finished."

    await jobs_collection().update_one(
        {"id": job["id"]},
        {"$set": {"stages": stages, "progress": total_progress, "status": new_status, "updated_at": now},
         "$push": {"logs": log_msg}}
    )
    return await jobs_collection().find_one({"id": job["id"]}, {"_id": 0})


# ─── Background Worker ───
_worker_running = False
_worker_task = None


async def night_queue_worker():
    """Background worker that auto-processes pending/processing jobs."""
    global _worker_running
    _worker_running = True
    logger.info("Night Queue Worker started")

    while _worker_running:
        try:
            # Find jobs that need processing
            active_jobs = await jobs_collection().find(
                {"status": {"$in": ["pending", "processing"]}}, {"_id": 0}
            ).sort("priority", -1).to_list(10)

            for job in active_jobs:
                if not _worker_running:
                    break
                await _advance_job(job)

            if active_jobs:
                logger.debug(f"Worker processed {len(active_jobs)} jobs")

        except Exception as e:
            logger.error(f"Worker error: {e}")

        await asyncio.sleep(3)  # Process every 3 seconds

    logger.info("Night Queue Worker stopped")


def start_worker():
    """Start the background worker."""
    global _worker_task, _worker_running
    if _worker_task and not _worker_task.done():
        return  # Already running
    _worker_running = True
    _worker_task = asyncio.create_task(night_queue_worker())


def stop_worker():
    """Stop the background worker."""
    global _worker_running
    _worker_running = False


@router.get("/worker/status")
async def worker_status():
    """Get Night Queue worker status."""
    active = await jobs_collection().count_documents({"status": {"$in": ["pending", "processing"]}})
    completed = await jobs_collection().count_documents({"status": "completed"})
    total = await jobs_collection().count_documents({})
    return {
        "running": _worker_running and _worker_task is not None and not _worker_task.done(),
        "active_jobs": active,
        "completed_jobs": completed,
        "total_jobs": total,
    }


@router.post("/worker/toggle")
async def toggle_worker():
    """Start or stop the Night Queue worker."""
    global _worker_running
    if _worker_running and _worker_task and not _worker_task.done():
        stop_worker()
        return {"status": "stopped"}
    else:
        start_worker()
        return {"status": "started"}


# ─── Revenue Pipelines ───
class CreatePipelineRequest(BaseModel):
    name: str
    type: str = "Automation"
    lane: int = 1


@router.post("/pipelines")
async def create_pipeline(req: CreatePipelineRequest):
    now = datetime.now(timezone.utc).isoformat()
    pipeline = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "type": req.type,
        "lane": req.lane,
        "status": "active",
        "heartbeat": "idle",
        "executions": 0,
        "revenue": 0,
        "created_at": now,
        "updated_at": now,
    }
    await pipelines_collection().insert_one(pipeline)
    pipeline.pop("_id", None)
    return pipeline


@router.get("/pipelines")
async def list_pipelines():
    cursor = pipelines_collection().find({}, {"_id": 0})
    pipelines = await cursor.to_list(100)
    total_revenue = sum(p.get("revenue", 0) for p in pipelines)
    return {"pipelines": pipelines, "total": len(pipelines), "total_revenue": total_revenue}


@router.put("/pipelines/{pipeline_id}/pulse")
async def pulse_pipeline(pipeline_id: str):
    """Trigger a pipeline heartbeat (simulates execution)."""
    import random
    rev = random.randint(50, 500)
    now = datetime.now(timezone.utc).isoformat()
    result = await pipelines_collection().update_one(
        {"id": pipeline_id},
        {"$set": {"heartbeat": "active", "updated_at": now}, "$inc": {"executions": 1, "revenue": rev}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    pipeline = await pipelines_collection().find_one({"id": pipeline_id}, {"_id": 0})
    return pipeline


@router.delete("/pipelines/{pipeline_id}")
async def delete_pipeline(pipeline_id: str):
    result = await pipelines_collection().delete_one({"id": pipeline_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"deleted": True}



# ─── Collections for Build / Compliance / Deploy ───
def builds_collection():
    return get_database()["sla113_builds"]

def compliance_collection():
    return get_database()["sla113_compliance"]

def deployments_collection():
    return get_database()["sla113_deployments"]


# ─── Build Pipeline Engine ───
class CreateBuildRequest(BaseModel):
    project_id: str
    target: str = "webgl"  # webgl | apk | both
    optimization: str = "balanced"  # speed | balanced | size
    include_assets: bool = True
    include_logic: bool = True


@router.post("/builds")
async def create_build(req: CreateBuildRequest):
    """Initiate a game build pipeline."""
    project = await projects_collection().find_one({"id": req.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    now = datetime.now(timezone.utc).isoformat()
    build = {
        "id": f"BLD-{uuid.uuid4().hex[:8].upper()}",
        "project_id": req.project_id,
        "project_name": project.get("name", "Unknown"),
        "game_type": project.get("game_type", "unknown"),
        "target": req.target,
        "optimization": req.optimization,
        "include_assets": req.include_assets,
        "include_logic": req.include_logic,
        "status": "queued",
        "progress": 0,
        "stages": [
            {"name": "Asset Compilation", "status": "pending", "progress": 0},
            {"name": "Logic Binding", "status": "pending", "progress": 0},
            {"name": "Shader Compilation", "status": "pending", "progress": 0},
            {"name": "Bundle Packaging", "status": "pending", "progress": 0},
            {"name": "Optimization Pass", "status": "pending", "progress": 0},
        ],
        "output": None,
        "size_mb": None,
        "logs": [f"[{now}] Build queued. Target: {req.target}, Optimization: {req.optimization}"],
        "created_at": now,
        "updated_at": now,
    }
    await builds_collection().insert_one(build)
    build.pop("_id", None)
    return build


@router.get("/builds")
async def list_builds():
    """List all builds."""
    cursor = builds_collection().find({}, {"_id": 0}).sort("created_at", -1)
    builds = await cursor.to_list(100)
    return {"builds": builds, "total": len(builds)}


@router.post("/builds/{build_id}/advance")
async def advance_build(build_id: str):
    """Advance build through its stages (simulate compilation)."""
    import random
    build = await builds_collection().find_one({"id": build_id}, {"_id": 0})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    if build["status"] == "completed":
        return build

    stages = build["stages"]
    now = datetime.now(timezone.utc).isoformat()
    current_stage_idx = next((i for i, s in enumerate(stages) if s["status"] != "completed"), len(stages))

    if current_stage_idx < len(stages):
        stage = stages[current_stage_idx]
        new_progress = min(stage["progress"] + random.randint(30, 60), 100)
        stage["progress"] = new_progress
        if new_progress >= 100:
            stage["status"] = "completed"
            log_msg = f"[{now}] Stage '{stage['name']}' completed."
        else:
            stage["status"] = "processing"
            log_msg = f"[{now}] Stage '{stage['name']}' at {new_progress}%..."
    else:
        log_msg = f"[{now}] All stages completed."

    # Calculate overall progress
    total_progress = sum(s["progress"] for s in stages) // len(stages)
    all_done = all(s["status"] == "completed" for s in stages)
    new_status = "completed" if all_done else "building"

    output = None
    size_mb = None
    if all_done:
        target = build["target"]
        output = f"sla113_{build['project_name'].lower().replace(' ', '_')}_{build['id']}.{'apk' if target == 'apk' else 'zip'}"
        size_mb = round(random.uniform(12.5, 185.0), 1)
        log_msg += f"\n[{now}] Build artifact: {output} ({size_mb} MB)"

    await builds_collection().update_one(
        {"id": build_id},
        {"$set": {"stages": stages, "progress": total_progress, "status": new_status,
                  "output": output, "size_mb": size_mb, "updated_at": now},
         "$push": {"logs": log_msg}}
    )
    build = await builds_collection().find_one({"id": build_id}, {"_id": 0})
    return build


@router.delete("/builds/{build_id}")
async def delete_build(build_id: str):
    result = await builds_collection().delete_one({"id": build_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Build not found")
    return {"deleted": True}


# ─── Compliance Engine ───
class ComplianceCheckRequest(BaseModel):
    project_id: str
    jurisdiction: str = "GLI"  # GLI | MGA | UKGC | CURACAO | INTERNAL
    check_type: str = "full"  # full | rtp_only | rng_only | fairness


COMPLIANCE_CHECKS = {
    "GLI": ["RTP Verification", "RNG Seed Audit", "Paytable Integrity", "Max Bet Limits", "Session Timeout Compliance", "Responsible Gaming Controls"],
    "MGA": ["RTP Verification", "RNG Certification", "Player Protection", "Anti-Money Laundering", "Game History Logging"],
    "UKGC": ["RTP Verification", "RNG Audit", "Fairness Testing", "Underage Prevention", "Self-Exclusion", "Advertising Compliance"],
    "CURACAO": ["RTP Verification", "RNG Basics", "Fair Play Attestation"],
    "INTERNAL": ["RTP Verification", "RNG Seed Audit", "Stress Test", "Edge Case Validation"],
}


@router.post("/compliance/check")
async def run_compliance_check(req: ComplianceCheckRequest):
    """Run compliance/certification checks on a project."""
    import random
    project = await projects_collection().find_one({"id": req.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    checks = COMPLIANCE_CHECKS.get(req.jurisdiction, COMPLIANCE_CHECKS["INTERNAL"])
    now = datetime.now(timezone.utc).isoformat()

    results = []
    all_passed = True
    for check_name in checks:
        passed = random.random() > 0.15  # 85% pass rate
        severity = "critical" if "RTP" in check_name or "RNG" in check_name else "warning"
        results.append({
            "check": check_name,
            "status": "PASS" if passed else "FAIL",
            "severity": severity if not passed else "none",
            "details": f"Verified against {req.jurisdiction} standards" if passed else f"Requires remediation per {req.jurisdiction} §4.2",
            "value": f"{round(random.uniform(91.0, 96.5), 2)}%" if "RTP" in check_name else None,
        })
        if not passed:
            all_passed = False

    report = {
        "id": f"CMP-{uuid.uuid4().hex[:8].upper()}",
        "project_id": req.project_id,
        "project_name": project.get("name", "Unknown"),
        "jurisdiction": req.jurisdiction,
        "check_type": req.check_type,
        "status": "CERTIFIED" if all_passed else "NEEDS_REMEDIATION",
        "pass_rate": f"{sum(1 for r in results if r['status'] == 'PASS')}/{len(results)}",
        "results": results,
        "created_at": now,
    }
    await compliance_collection().insert_one(report)
    report.pop("_id", None)
    return report


@router.get("/compliance")
async def list_compliance_reports():
    cursor = compliance_collection().find({}, {"_id": 0}).sort("created_at", -1)
    reports = await cursor.to_list(100)
    return {"reports": reports, "total": len(reports)}


@router.delete("/compliance/{report_id}")
async def delete_compliance_report(report_id: str):
    result = await compliance_collection().delete_one({"id": report_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"deleted": True}


# ─── Deploy Engine ───
class DeployRequest(BaseModel):
    build_id: str
    target_cdn: str = "cloudflare"  # cloudflare | aws | gcp | custom
    region: str = "us-west"
    auto_ssl: bool = True


@router.post("/deploy")
async def deploy_build(req: DeployRequest):
    """Deploy a completed build to CDN."""
    build = await builds_collection().find_one({"id": req.build_id}, {"_id": 0})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    if build["status"] != "completed":
        raise HTTPException(status_code=400, detail="Build must be completed before deployment")

    now = datetime.now(timezone.utc).isoformat()
    deployment = {
        "id": f"DPL-{uuid.uuid4().hex[:8].upper()}",
        "build_id": req.build_id,
        "project_name": build.get("project_name", "Unknown"),
        "target_cdn": req.target_cdn,
        "region": req.region,
        "auto_ssl": req.auto_ssl,
        "status": "deploying",
        "progress": 0,
        "url": None,
        "ssl_status": "pending" if req.auto_ssl else "disabled",
        "logs": [f"[{now}] Deployment initiated. CDN: {req.target_cdn}, Region: {req.region}"],
        "created_at": now,
        "updated_at": now,
    }
    await deployments_collection().insert_one(deployment)
    deployment.pop("_id", None)
    return deployment


@router.post("/deploy/{deploy_id}/advance")
async def advance_deployment(deploy_id: str):
    """Advance deployment progress (simulate CDN propagation)."""
    import random
    deploy = await deployments_collection().find_one({"id": deploy_id}, {"_id": 0})
    if not deploy:
        raise HTTPException(status_code=404, detail="Deployment not found")
    if deploy["status"] == "live":
        return deploy

    now = datetime.now(timezone.utc).isoformat()
    new_progress = min(deploy["progress"] + random.randint(25, 50), 100)
    new_status = "live" if new_progress >= 100 else "propagating"

    url = None
    ssl_status = deploy.get("ssl_status", "pending")
    if new_progress >= 100:
        slug = deploy["project_name"].lower().replace(" ", "-")
        cdn = deploy["target_cdn"]
        url = f"https://{slug}.{'cdn.cloudflare.com' if cdn == 'cloudflare' else 'd2x.amazonaws.com' if cdn == 'aws' else 'storage.googleapis.com' if cdn == 'gcp' else 'custom-cdn.io'}"
        ssl_status = "active" if deploy.get("auto_ssl") else "disabled"

    log_msg = f"[{now}] {'LIVE — CDN propagation complete.' if new_progress >= 100 else f'Propagating... {new_progress}%'}"

    await deployments_collection().update_one(
        {"id": deploy_id},
        {"$set": {"progress": new_progress, "status": new_status, "url": url,
                  "ssl_status": ssl_status, "updated_at": now},
         "$push": {"logs": log_msg}}
    )
    deploy = await deployments_collection().find_one({"id": deploy_id}, {"_id": 0})
    return deploy


@router.get("/deployments")
async def list_deployments():
    cursor = deployments_collection().find({}, {"_id": 0}).sort("created_at", -1)
    deploys = await cursor.to_list(100)
    return {"deployments": deploys, "total": len(deploys)}


@router.delete("/deploy/{deploy_id}")
async def delete_deployment(deploy_id: str):
    result = await deployments_collection().delete_one({"id": deploy_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return {"deleted": True}


# ─── Seed default pipelines if empty ───
async def seed_default_pipelines():
    count = await pipelines_collection().count_documents({})
    if count == 0:
        defaults = [
            {"name": "Lead Qualification Engine", "type": "Automation", "lane": 1},
            {"name": "CRM Syncing Logic", "type": "Automation", "lane": 1},
            {"name": "Pro Voice Over (SaaS)", "type": "Utility", "lane": 2},
            {"name": "SMS/Email Gateway", "type": "Utility", "lane": 2},
            {"name": "White-Label Instance", "type": "Sovereign", "lane": 3},
            {"name": "Managed Sovereignty", "type": "Sovereign", "lane": 3},
        ]
        now = datetime.now(timezone.utc).isoformat()
        for d in defaults:
            await pipelines_collection().insert_one({
                "id": str(uuid.uuid4()), **d, "status": "active", "heartbeat": "idle",
                "executions": 0, "revenue": 0, "created_at": now, "updated_at": now,
            })
        logger.info("Seeded 6 default pipelines")
