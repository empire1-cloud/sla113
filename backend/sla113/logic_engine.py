"""SLA113 Logic Engine - AI Game Math & Mechanics Generation"""
import os
import json
import time
import uuid
import logging
from typing import Dict, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


LOGIC_TEMPLATES = {
    "fish_shooter": {
        "mechanics": ["weapon_types", "fish_values", "hit_detection", "multipliers", "boss_mechanics"],
        "rtp": {"target": 96.5, "variance": "medium-high"},
        "economy": ["coin_earn_rates", "weapon_costs", "upgrade_paths"],
    },
    "slot_machine": {
        "mechanics": ["reel_config", "paylines", "wild_mechanics", "scatter_trigger", "bonus_rounds", "free_spins"],
        "rtp": {"target": 96.0, "variance": "medium"},
        "paytable": ["symbol_values", "combo_multipliers", "jackpot_tiers"],
    },
    "crash_game": {
        "mechanics": ["multiplier_curve", "crash_probability", "cashout_mechanics", "auto_cashout"],
        "rtp": {"target": 97.0, "variance": "high"},
        "economy": ["min_max_bets", "house_edge", "payout_limits"],
    },
    "platformer": {
        "mechanics": ["physics_config", "jump_params", "enemy_ai", "collision_rules", "power_up_effects"],
        "levels": ["difficulty_curve", "spawn_rates", "checkpoint_spacing"],
        "scoring": ["point_values", "combo_system", "time_bonuses"],
    },
    "puzzle": {
        "mechanics": ["match_rules", "board_generation", "cascade_logic", "special_pieces", "objectives"],
        "levels": ["difficulty_progression", "move_limits", "star_thresholds"],
        "scoring": ["base_points", "combo_multipliers", "time_bonus"],
    },
}


async def generate_logic(
    project: Dict[str, Any],
    logic_type: str = "mechanics",
    difficulty: str = "medium",
    custom_requirements: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate game logic/math specifications."""
    start = time.time()
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise ValueError("EMERGENT_LLM_KEY not configured")

    game_type = project.get("game_type", "platformer")
    templates = LOGIC_TEMPLATES.get(game_type, {})
    type_refs = templates.get(logic_type, [])

    system_prompt = f"""You are SLA113, an expert game mathematician and mechanics designer.
You generate precise, balanced game logic specifications with real numbers.
Always respond with valid JSON only, no markdown.

Game Type: {project.get('game_type_info', {}).get('name', game_type)}
Difficulty: {difficulty}
Project: {project.get('name', 'Untitled')}"""

    prompts_by_type = {
        "mechanics": f"""Generate complete game mechanics specification for this {game_type} game.
Reference areas: {json.dumps(type_refs)}

Include:
- "core_loop": main gameplay loop description
- "mechanics": list of mechanic objects with "name", "description", "parameters" (with actual numeric values), "interactions"
- "state_machine": game states and transitions
- "input_map": player inputs and their effects
- "difficulty_scaling": how difficulty={difficulty} affects parameters

Return JSON: {{"mechanics": ..., "core_loop": ..., "state_machine": ..., "input_map": ..., "difficulty_scaling": ...}}""",

        "rtp": f"""Generate RTP (Return to Player) mathematical proof for this {game_type} game.
Target RTP: {templates.get('rtp', {}).get('target', 96.0)}%
Variance: {templates.get('rtp', {}).get('variance', 'medium')}

Include:
- "target_rtp": target percentage
- "calculated_rtp": actual calculated RTP with formula
- "house_edge": percentage
- "variance_profile": low/medium/high with standard deviation
- "hit_frequency": how often player wins
- "max_win_multiplier": maximum possible win
- "simulation_results": simulated over 10000 rounds with win/loss distribution
- "certification_notes": notes for gaming certification compliance

Return JSON object with all fields above.""",

        "paytable": f"""Generate a complete paytable for this {game_type} game.

Include:
- "symbols": list of symbols with "name", "value_3", "value_4", "value_5" (for 3/4/5 matches)
- "special_symbols": wilds, scatters with their effects
- "bonus_triggers": conditions and rewards
- "jackpot_tiers": mini/minor/major/grand with values and odds
- "payline_patterns": list of payline configurations

Return JSON object.""",

        "scoring": f"""Generate a scoring system for this {game_type} game.

Include:
- "base_scores": point values for each action
- "combo_system": how combos work, multiplier progression
- "bonus_events": special scoring events
- "leaderboard_tiers": score ranges for bronze/silver/gold/platinum
- "progression_curve": XP requirements per level

Return JSON object.""",

        "levels": f"""Generate level design specifications for this {game_type} game with difficulty={difficulty}.

Include:
- "total_levels": recommended count
- "difficulty_curve": array of difficulty values per level
- "level_specs": first 5 levels with "enemies", "obstacles", "objectives", "time_limit", "rewards"
- "boss_levels": every Nth level has boss encounter
- "unlock_requirements": what unlocks each tier

Return JSON object.""",

        "economy": f"""Generate in-game economy design for this {game_type} game.
Reference: {json.dumps(templates.get('economy', []))}

Include:
- "currencies": list of currencies with earn/spend rates
- "pricing_tiers": items/upgrades with costs
- "earn_rates": how fast players earn per minute of play
- "sink_ratio": spend-to-earn ratio for balanced economy
- "monetization_hooks": optional premium currency opportunities
- "session_economics": average earnings per session

Return JSON object.""",

        "rng": f"""Generate RNG (Random Number Generation) specification for this {game_type} game.

Include:
- "algorithm": recommended RNG algorithm (e.g., Mersenne Twister, xorshift128+)
- "seed_strategy": how seeds are generated and rotated
- "distribution_tables": probability distributions for key random events
- "fairness_proof": mathematical proof of fairness
- "anti_manipulation": measures against prediction/manipulation
- "audit_trail": how RNG results are logged for certification

Return JSON object.""",
    }

    user_prompt = custom_requirements or prompts_by_type.get(logic_type, prompts_by_type["mechanics"])

    chat = LlmChat(
        api_key=api_key,
        session_id=f"sla113-logic-{uuid.uuid4().hex[:8]}",
        system_message=system_prompt,
    )
    chat.with_model("openai", "gpt-4o-mini")

    raw = await chat.send_message(UserMessage(text=user_prompt))

    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
        specs = json.loads(cleaned)
    except json.JSONDecodeError:
        specs = {"raw_output": raw, "logic_type": logic_type}

    elapsed = round(time.time() - start, 2)

    return {
        "project_id": project.get("id", ""),
        "logic_type": logic_type,
        "difficulty": difficulty,
        "specs": specs,
        "generation_time": elapsed,
    }
