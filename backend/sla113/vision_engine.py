"""SLA113 Vision Engine - AI Game Asset Generation"""
import os
import json
import time
import uuid
import logging
from typing import Dict, Any, List, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


STYLE_PROMPTS = {
    "pixel_art": "16-bit pixel art style with limited color palette",
    "vector": "clean vector illustration with flat colors and sharp edges",
    "3d_render": "3D rendered style with realistic lighting and materials",
    "hand_drawn": "hand-drawn illustration style with ink outlines and watercolor fills",
    "anime": "Japanese anime art style with cel shading and vibrant colors",
    "neon": "neon-lit cyberpunk style with glowing edges and dark backgrounds",
    "retro": "retro 80s arcade style with bold colors and scanline effects",
}

GAME_ASSET_TEMPLATES = {
    "fish_shooter": {
        "sprites": ["fish_small", "fish_medium", "fish_boss", "bullet", "weapon", "net", "coin", "power_up"],
        "backgrounds": ["ocean_floor", "coral_reef", "deep_sea", "treasure_cave"],
        "ui": ["score_panel", "weapon_selector", "health_bar", "coin_counter"],
        "effects": ["splash", "explosion", "sparkle", "bubble_trail"],
    },
    "slot_machine": {
        "sprites": ["reel_symbol_1", "reel_symbol_2", "reel_symbol_3", "wild", "scatter", "bonus"],
        "backgrounds": ["slot_frame", "bonus_bg", "jackpot_bg"],
        "ui": ["spin_button", "bet_panel", "win_display", "paytable_frame"],
        "effects": ["win_glow", "reel_blur", "coin_rain", "jackpot_flash"],
    },
    "crash_game": {
        "sprites": ["rocket", "explosion_stages", "multiplier_badge", "cashout_icon"],
        "backgrounds": ["space_bg", "atmosphere_layers", "launch_pad"],
        "ui": ["multiplier_display", "bet_panel", "history_bar", "cashout_button"],
        "effects": ["trail_fire", "star_streak", "shockwave", "confetti"],
    },
    "platformer": {
        "sprites": ["hero_idle", "hero_run", "hero_jump", "enemy_basic", "enemy_flying", "collectible", "power_up"],
        "backgrounds": ["level_1_bg", "level_2_bg", "sky_parallax", "underground"],
        "ui": ["lives_counter", "score_display", "level_indicator", "pause_menu"],
        "effects": ["dust_cloud", "impact_star", "coin_sparkle", "death_poof"],
    },
    "puzzle": {
        "sprites": ["gem_red", "gem_blue", "gem_green", "gem_yellow", "gem_purple", "bomb", "rainbow"],
        "backgrounds": ["board_bg", "menu_bg", "level_complete_bg"],
        "ui": ["move_counter", "score_bar", "star_rating", "hint_button"],
        "effects": ["match_glow", "cascade_trail", "combo_burst", "clear_wave"],
    },
}


async def generate_vision_assets(
    project: Dict[str, Any],
    asset_type: str = "sprites",
    style: Optional[str] = None,
    count: int = 5,
    custom_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate visual asset specifications for a game project."""
    start = time.time()
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise ValueError("EMERGENT_LLM_KEY not configured")

    game_type = project.get("game_type", "platformer")
    theme = project.get("theme", "fantasy")
    style = style or "pixel_art"
    style_desc = STYLE_PROMPTS.get(style, style)

    # Get template assets for this game type
    templates = GAME_ASSET_TEMPLATES.get(game_type, {})
    template_assets = templates.get(asset_type, [])

    system_prompt = f"""You are SLA113, an expert game asset designer and art director.
You generate detailed visual asset specifications for game development.
Always respond with valid JSON only, no markdown.

Game Type: {project.get('game_type_info', {}).get('name', game_type)}
Theme: {theme}
Art Style: {style_desc}
Project: {project.get('name', 'Untitled')}"""

    user_prompt = custom_prompt or f"""Generate {count} detailed {asset_type} asset specifications for this {game_type} game.

Template reference assets: {json.dumps(template_assets[:count])}

For each asset, provide:
- "id": unique asset identifier
- "name": descriptive name
- "type": "{asset_type}"
- "description": detailed visual description (colors, shapes, animations)
- "dimensions": {{"width": px, "height": px}}
- "animation_frames": number of animation frames (if applicable)
- "color_palette": list of 3-5 hex colors
- "z_index": layer order (0=background, 10=foreground)
- "tags": relevant tags

Return a JSON object: {{"assets": [...]}}"""

    chat = LlmChat(
        api_key=api_key,
        session_id=f"sla113-vision-{uuid.uuid4().hex[:8]}",
        system_message=system_prompt,
    )
    chat.with_model("openai", "gpt-4o-mini")

    raw = await chat.send_message(UserMessage(text=user_prompt))

    # Parse JSON from response
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        result = {"assets": [{"id": str(uuid.uuid4())[:8], "name": f"{asset_type}_asset", "description": raw, "type": asset_type}]}

    elapsed = round(time.time() - start, 2)
    assets = result.get("assets", [result] if isinstance(result, dict) else [])

    return {
        "project_id": project.get("id", ""),
        "asset_type": asset_type,
        "style": style,
        "assets": assets,
        "generation_time": elapsed,
    }
