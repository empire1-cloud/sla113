"""
Anime Story Engine

Generates narrative structure, story arcs, plot points, and episode
breakdowns for anime projects.
"""

from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import Optional, List
from pydantic import BaseModel

load_dotenv()


class AnimeStory(BaseModel):
    """Complete anime story output."""
    title: str
    logline: str
    premise: str
    themes: List[str]
    tone: str
    story_arcs: List[dict]
    key_plot_points: List[str]
    climax: str
    resolution: str
    hooks: List[str]
    episode_structure: List[dict]


class AnimeStoryEngine:
    """Generates narrative structure and story arcs for anime projects."""
    
    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-5.2"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "gemini-3-flash": ("gemini", "gemini-3-flash-preview")
    }
    
    DEFAULT_MODEL = "claude-sonnet-4.5"
    
    SYSTEM_PROMPT = """You are the Anime Story Engine.

Your job is to generate narrative structure, story arcs, plot points, and episode breakdowns for anime projects.

RULES:
1. Always return valid JSON only — no markdown, no commentary.
2. Stories must be ORIGINAL and not based on copyrighted works.
3. Focus on emotional resonance and narrative momentum.
4. No disclaimers, no model identity, no filler.
5. Create compelling arcs with clear stakes and payoffs.

OUTPUT FORMAT (JSON ONLY):
{
  "title": "Story title",
  "logline": "One-sentence pitch",
  "premise": "2-3 sentence setup",
  "themes": ["Theme 1", "Theme 2", "Theme 3"],
  "tone": "Overall emotional tone",
  "story_arcs": [
    {
      "name": "Arc name",
      "episodes": "Episode range",
      "summary": "What happens",
      "protagonist_goal": "What the hero wants",
      "antagonist_goal": "What opposes them",
      "stakes": "What's at risk",
      "resolution": "How it ends"
    }
  ],
  "key_plot_points": ["Inciting incident", "First major turn", "Midpoint", "Crisis", "Climax"],
  "climax": "Description of the climactic moment",
  "resolution": "How the story concludes",
  "hooks": ["Mystery 1", "Unanswered question 2"],
  "episode_structure": [
    {
      "episode": 1,
      "title": "Episode title",
      "summary": "What happens",
      "hook": "Cliffhanger or setup"
    }
  ]
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
            session_id=f"anime-story-{model}",
            system_message=cls.SYSTEM_PROMPT
        ).with_model(provider, model_name)
        
        return chat
    
    @classmethod
    async def generate_story_async(
        cls,
        concept: str,
        genre: Optional[str] = None,
        episode_count: Optional[int] = None,
        characters: Optional[List[str]] = None,
        lore: Optional[dict] = None,
        model: Optional[str] = None
    ) -> dict:
        chat = cls._create_chat(model)
        
        prompt_parts = [f"Create a complete story structure for: {concept}"]
        
        if genre:
            prompt_parts.append(f"\nGenre: {genre}")
        if episode_count:
            prompt_parts.append(f"\nTarget episode count: {episode_count}")
        if characters:
            prompt_parts.append(f"\nMain characters: {', '.join(characters)}")
        if lore:
            prompt_parts.append(f"\nWorld/lore context: {json.dumps(lore)[:500]}")
        
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
            return {"title": concept, "error": "Generation failed"}
    
    @classmethod
    def generate_story(cls, concept: str, **kwargs) -> dict:
        return asyncio.run(cls.generate_story_async(concept, **kwargs))
