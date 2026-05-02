"""SLA113 Composer Engine - Assemble Game Bundles"""
import os
import json
import time
import uuid
import logging
from typing import Dict, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


async def compose_game_bundle(
    project: Dict[str, Any],
    include_vision: bool = True,
    include_logic: bool = True,
    output_format: str = "json",
) -> Dict[str, Any]:
    """Compose a complete game bundle from project assets and logic."""
    start = time.time()
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise ValueError("EMERGENT_LLM_KEY not configured")

    game_type = project.get("game_type", "platformer")
    vision_assets = project.get("vision_assets", [])
    logic_specs = project.get("logic_specs", [])

    system_prompt = f"""You are SLA113, an expert game composer and technical architect.
You assemble complete game specifications from generated assets and logic.
Always respond with valid JSON only, no markdown.

Game: {project.get('name', 'Untitled')}
Type: {project.get('game_type_info', {}).get('name', game_type)}
Platform: {project.get('target_platform', 'web')}"""

    sections = []
    if include_vision and vision_assets:
        sections.append(f"VISUAL ASSETS ({len(vision_assets)} sets):\n{json.dumps(vision_assets[:3], indent=2)[:2000]}")
    if include_logic and logic_specs:
        sections.append(f"GAME LOGIC ({len(logic_specs)} specs):\n{json.dumps(logic_specs[:3], indent=2)[:2000]}")

    asset_context = "\n\n".join(sections) if sections else "No pre-generated assets. Create a complete specification from scratch."

    format_instructions = {
        "json": "Return a complete game specification as a JSON object.",
        "html5": "Return a JSON object containing an 'html' field with a playable HTML5/Canvas game, plus metadata.",
        "specification": "Return a detailed technical specification document as a JSON object.",
    }

    user_prompt = f"""Compose a complete {game_type} game bundle.

{asset_context}

{format_instructions.get(output_format, format_instructions['json'])}

Include these sections:
- "metadata": {{name, version, game_type, platform, created_by: "SLA113"}}
- "config": {{screen_size, fps, physics_engine, render_mode}}
- "asset_manifest": list of all required assets with paths and specs
- "game_logic": core mechanics, state machine, rules
- "scene_graph": scene hierarchy and object relationships
- "audio_manifest": required sound effects and music tracks
- "build_config": build settings for target platform
- "estimated_size_kb": estimated bundle size
- "development_time_saved_hours": estimated hours of manual dev this replaces

Return complete JSON object."""

    chat = LlmChat(
        api_key=api_key,
        session_id=f"sla113-compose-{uuid.uuid4().hex[:8]}",
        system_message=system_prompt,
    )
    chat.with_model("openai", "gpt-4o-mini")

    raw = await chat.send_message(UserMessage(text=user_prompt))

    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
        bundle = json.loads(cleaned)
    except json.JSONDecodeError:
        bundle = {"raw_output": raw, "format": output_format}

    elapsed = round(time.time() - start, 2)

    return {
        "project_id": project.get("id", ""),
        "bundle": bundle,
        "output_format": output_format,
        "generation_time": elapsed,
    }
