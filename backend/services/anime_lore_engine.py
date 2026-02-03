"""
Anime Lore Engine

Generates detailed world-building, mythology, factions, history,
and lore systems for anime/fantasy projects.
"""

from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import Optional, List
from pydantic import BaseModel

load_dotenv()


class AnimeLore(BaseModel):
    """Complete anime lore output."""
    world_name: str
    setting: str
    time_period: str
    core_mythology: List[str]
    factions: List[dict]
    locations: List[dict]
    power_system: dict
    history: List[str]
    cultural_elements: List[str]
    mysteries: List[str]
    rules_of_the_world: List[str]


class AnimeLoreEngine:
    """Generates world-building and lore for anime projects."""
    
    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-5.2"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "gemini-3-flash": ("gemini", "gemini-3-flash-preview")
    }
    
    DEFAULT_MODEL = "claude-sonnet-4.5"
    
    SYSTEM_PROMPT = """You are the Anime Lore Engine.

Your job is to generate detailed world-building, mythology, factions, history, and lore for anime/fantasy projects.

RULES:
1. Always return valid JSON only — no markdown, no commentary.
2. Lore must be ORIGINAL and not based on copyrighted works.
3. Focus on internal consistency and narrative potential.
4. No disclaimers, no model identity, no filler.
5. Create rich, interconnected world elements.

OUTPUT FORMAT (JSON ONLY):
{
  "world_name": "Name of the world/setting",
  "setting": "Description of the world",
  "time_period": "When the story takes place",
  "core_mythology": ["Creation myth", "Divine beings", "Cosmic rules"],
  "factions": [
    {
      "name": "Faction name",
      "description": "What they are",
      "goals": "What they want",
      "territory": "Where they operate",
      "symbol": "Their emblem/mark"
    }
  ],
  "locations": [
    {
      "name": "Location name",
      "type": "City | Realm | Sacred site | etc.",
      "description": "What it's like",
      "significance": "Why it matters"
    }
  ],
  "power_system": {
    "name": "Name of the power/magic system",
    "source": "Where power comes from",
    "types": ["Type 1", "Type 2"],
    "limitations": ["Limitation 1"],
    "cost": "What using power costs"
  },
  "history": ["Major historical event 1", "Event 2", "Event 3"],
  "cultural_elements": ["Custom 1", "Tradition 2", "Belief 3"],
  "mysteries": ["Unsolved mystery 1", "Ancient secret 2"],
  "rules_of_the_world": ["Rule 1", "Rule 2"]
}

Return ONLY the JSON object."""

    @classmethod
    def _get_api_key(cls) -> str:
        return os.environ.get("EMERGENT_LLM_KEY")
    
    @classmethod
    def _create_chat(cls, model: str = None) -> LlmChat:
        model = model or cls.DEFAULT_MODEL
        api_key = cls._get_api_key()
        provider, model_name = cls.MODEL_CONFIG.get(model, cls.MODEL_CONFIG[cls.DEFAULT_MODEL])
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"anime-lore-{model}",
            system_message=cls.SYSTEM_PROMPT
        ).with_model(provider, model_name)
        
        return chat
    
    @classmethod
    async def generate_lore_async(
        cls,
        world_concept: str,
        genre: Optional[str] = None,
        themes: Optional[List[str]] = None,
        influences: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> dict:
        chat = cls._create_chat(model)
        
        prompt_parts = [f"Create detailed lore for: {world_concept}"]
        
        if genre:
            prompt_parts.append(f"\nGenre: {genre}")
        if themes:
            prompt_parts.append(f"\nThemes: {', '.join(themes)}")
        if influences:
            prompt_parts.append(f"\nCultural influences: {', '.join(influences)}")
        
        prompt = "\n".join(prompt_parts)
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()
            return json.loads(response)
        except json.JSONDecodeError:
            return {"world_name": world_concept, "error": "Generation failed"}
    
    @classmethod
    def generate_lore(cls, world_concept: str, **kwargs) -> dict:
        return asyncio.run(cls.generate_lore_async(world_concept, **kwargs))
