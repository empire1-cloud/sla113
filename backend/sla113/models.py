"""SLA113 Data Models"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid


# ─── Game Types ───
GAME_TYPES = {
    "fish_shooter": {
        "name": "Fish Shooter",
        "description": "Multiplayer fish hunting arcade game with weapon upgrades",
        "category": "arcade",
    },
    "slot_machine": {
        "name": "Slot Machine",
        "description": "Classic/video slot with reels, paylines, and bonus rounds",
        "category": "casino",
    },
    "crash_game": {
        "name": "Crash Game",
        "description": "Multiplier-based game with cash-out mechanics",
        "category": "casino",
    },
    "platformer": {
        "name": "Platformer",
        "description": "Side-scrolling platform game with levels and enemies",
        "category": "action",
    },
    "puzzle": {
        "name": "Puzzle",
        "description": "Match-3, tile-based, or logic puzzle game",
        "category": "casual",
    },
    "card_game": {
        "name": "Card Game",
        "description": "Poker, blackjack, or custom card-based game",
        "category": "casino",
    },
    "tower_defense": {
        "name": "Tower Defense",
        "description": "Strategic tower placement to defend against waves",
        "category": "strategy",
    },
    "runner": {
        "name": "Endless Runner",
        "description": "Auto-running character with obstacles and power-ups",
        "category": "casual",
    },
    "rpg": {
        "name": "RPG",
        "description": "Role-playing game with stats, inventory, and quests",
        "category": "adventure",
    },
    "battle_royale": {
        "name": "Battle Royale",
        "description": "Last-player-standing arena combat game",
        "category": "action",
    },
}


# ─── Request Models ───
class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    game_type: str = Field(..., description="One of the supported game types")
    description: Optional[str] = None
    theme: Optional[str] = Field(None, description="Visual theme: cyberpunk, fantasy, ocean, space, etc.")
    target_platform: str = Field(default="web", description="web, mobile, or both")


class VisionGenerateRequest(BaseModel):
    project_id: str
    asset_type: str = Field(default="sprites", description="sprites, backgrounds, ui, animations, effects")
    style: Optional[str] = Field(None, description="pixel_art, vector, 3d_render, hand_drawn, anime")
    count: int = Field(default=5, ge=1, le=20)
    custom_prompt: Optional[str] = None


class LogicGenerateRequest(BaseModel):
    project_id: str
    logic_type: str = Field(default="mechanics", description="mechanics, rtp, paytable, rng, scoring, levels, economy")
    difficulty: str = Field(default="medium", description="easy, medium, hard, progressive")
    custom_requirements: Optional[str] = None


class ComposeRequest(BaseModel):
    project_id: str
    include_vision: bool = True
    include_logic: bool = True
    output_format: str = Field(default="json", description="json, html5, specification")


# ─── Response Models ───
class ProjectResponse(BaseModel):
    id: str
    name: str
    game_type: str
    game_type_info: Dict[str, Any]
    description: Optional[str]
    theme: Optional[str]
    target_platform: str
    status: str
    vision_assets: List[Dict[str, Any]] = []
    logic_specs: List[Dict[str, Any]] = []
    compositions: List[Dict[str, Any]] = []
    created_at: str
    updated_at: str


class VisionResponse(BaseModel):
    project_id: str
    asset_type: str
    assets: List[Dict[str, Any]]
    style: str
    generation_time: float


class LogicResponse(BaseModel):
    project_id: str
    logic_type: str
    specs: Dict[str, Any]
    generation_time: float


class ComposeResponse(BaseModel):
    project_id: str
    bundle: Dict[str, Any]
    output_format: str
    generation_time: float
