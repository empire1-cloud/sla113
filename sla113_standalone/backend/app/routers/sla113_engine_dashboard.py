"""SLA113 Engine Dashboard — Vision, Logic, Composer, Terminal"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import uuid
import os
import json
import logging

from emergentintegrations.llm.chat import LlmChat, UserMessage
from app.core.database import get_database
from app.models.schemas_game_types import GAME_TYPES
from app.models.schemas import VisionGenerateRequest, LogicGenerateRequest, ComposeRequest, TerminalRequest
from app.services.vision_engine import generate_vision_assets
from app.services.logic_engine import generate_logic
from app.services.composer_engine import compose_game_bundle

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sla113", tags=["sla113-engines"])

_terminal_sessions = {}


def projects_collection():
    return get_database()["sla113_projects"]


@router.post("/vision/generate")
async def generate_vision(req: VisionGenerateRequest):
    project = await projects_collection().find_one({"id": req.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        result = await generate_vision_assets(
            project=project, asset_type=req.asset_type, style=req.style,
            count=req.count, custom_prompt=req.custom_prompt,
        )
        await projects_collection().update_one(
            {"id": req.project_id},
            {"$push": {"vision_assets": result}, "$set": {"status": "vision_generated", "updated_at": datetime.now(timezone.utc).isoformat()}},
        )
        return result
    except Exception as e:
        logger.error(f"Vision generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Vision generation failed: {str(e)}")


@router.post("/logic/generate")
async def generate_game_logic(req: LogicGenerateRequest):
    project = await projects_collection().find_one({"id": req.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        result = await generate_logic(
            project=project, logic_type=req.logic_type, difficulty=req.difficulty,
            custom_requirements=req.custom_requirements,
        )
        await projects_collection().update_one(
            {"id": req.project_id},
            {"$push": {"logic_specs": result}, "$set": {"status": "logic_generated", "updated_at": datetime.now(timezone.utc).isoformat()}},
        )
        return result
    except Exception as e:
        logger.error(f"Logic generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Logic generation failed: {str(e)}")


@router.post("/compose")
async def compose_game(req: ComposeRequest):
    project = await projects_collection().find_one({"id": req.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        result = await compose_game_bundle(
            project=project, include_vision=req.include_vision,
            include_logic=req.include_logic, output_format=req.output_format,
        )
        await projects_collection().update_one(
            {"id": req.project_id},
            {"$push": {"compositions": result}, "$set": {"status": "composed", "updated_at": datetime.now(timezone.utc).isoformat()}},
        )
        return result
    except Exception as e:
        logger.error(f"Composition failed: {e}")
        raise HTTPException(status_code=500, detail=f"Composition failed: {str(e)}")


@router.post("/terminal")
async def terminal_command(req: TerminalRequest):
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        return {"response": "[ERROR] EMERGENT_LLM_KEY not configured. Overseer offline."}

    total_projects = await projects_collection().count_documents({})
    recent_projects = await projects_collection().find(
        {}, {"_id": 0, "name": 1, "game_type": 1, "status": 1, "theme": 1}
    ).sort("created_at", -1).to_list(10)

    by_type = {}
    for gt in GAME_TYPES:
        c = await projects_collection().count_documents({"game_type": gt})
        if c > 0:
            by_type[gt] = c

    platform_context = json.dumps({
        "total_projects": total_projects, "projects_by_type": by_type,
        "recent_projects": recent_projects, "supported_game_types": list(GAME_TYPES.keys()),
        "engines": ["vision", "logic", "composer"],
    }, indent=2)

    system_msg = f"""You are the SOVEREIGN OVERSEER of SLA113 — the most advanced AI game creation platform on Earth.

IDENTITY: You are a military-grade AI command system. Your tone is terse, authoritative, and precise. Use UPPERCASE for emphasis. Respond in terminal/monospace style with > prefixes.

PLATFORM STATE:
{platform_context}

CAPABILITIES:
- Full knowledge of all 29 game types across arcade, casino, rpg, racing, and hybrid categories
- Advise on RTP calculations, game math, asset generation strategy, architecture decisions
- Track all active projects and their generation status

RULES:
- Keep responses under 150 words
- Use > prefix for each line
- Reference specific project data when relevant
- Be direct. No fluff. Canon enforcement at all times."""

    session_id = req.session_id or "default"
    if session_id not in _terminal_sessions:
        chat = LlmChat(api_key=api_key, session_id=f"sla113-overseer-{session_id}", system_message=system_msg)
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
