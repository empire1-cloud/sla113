"""
Art Direction Engine

Generates complete, actionable art direction for creative projects.
Defines visual identity, style rules, palettes, composition, and constraints.
Does NOT generate images — defines direction for artists/models to follow.
"""

from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import Optional, List, Dict
from pydantic import BaseModel

load_dotenv()


class VisualStyle(BaseModel):
    genre: str
    influences: List[str]
    description: str


class ColorPalette(BaseModel):
    primary: List[str]
    secondary: List[str]
    accents: List[str]
    mood_notes: str


class CharacterStyle(BaseModel):
    proportions: str
    linework: str
    shading: str
    expression_rules: List[str]
    silhouette_rules: List[str]


class EnvironmentStyle(BaseModel):
    lighting: str
    atmosphere: str
    detail_level: str
    composition_rules: List[str]


class CameraDirection(BaseModel):
    framing: List[str]
    angles: List[str]
    motion_rules: List[str]


class TextureRules(BaseModel):
    materials: List[str]
    surface_treatment: str
    consistency_requirements: List[str]


class ArtDirection(BaseModel):
    """Complete art direction output."""
    project_name: str
    visual_style: VisualStyle
    color_palette: ColorPalette
    character_style: CharacterStyle
    environment_style: EnvironmentStyle
    camera_direction: CameraDirection
    texture_rules: TextureRules
    production_constraints: List[str]
    do_not_use: List[str]


class ArtDirectionEngine:
    """Generates art direction for creative projects."""
    
    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-5.2"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "gemini-3-flash": ("gemini", "gemini-3-flash-preview")
    }
    
    # Default to Claude for creative direction
    DEFAULT_MODEL = "claude-sonnet-4.5"
    
    # Visual style templates
    STYLE_TEMPLATES = {
        "anime": {
            "genre": "anime",
            "typical_elements": ["cel-shading", "expressive eyes", "dynamic poses", "speed lines"],
            "shading": "flat or cel-shaded",
            "linework": "clean, consistent weight"
        },
        "cinematic": {
            "genre": "cinematic",
            "typical_elements": ["realistic lighting", "depth of field", "dramatic composition"],
            "shading": "realistic with soft gradients",
            "linework": "minimal or integrated into rendering"
        },
        "painterly": {
            "genre": "painterly",
            "typical_elements": ["visible brushstrokes", "impasto texture", "color mixing"],
            "shading": "soft, blended",
            "linework": "loose, expressive"
        },
        "stylized": {
            "genre": "stylized",
            "typical_elements": ["exaggerated proportions", "bold colors", "graphic shapes"],
            "shading": "varies by sub-style",
            "linework": "bold, graphic"
        },
        "minimalist": {
            "genre": "minimalist",
            "typical_elements": ["negative space", "limited palette", "essential forms"],
            "shading": "flat or subtle",
            "linework": "thin, precise"
        }
    }
    
    # Color mood presets
    COLOR_MOODS = {
        "warm_heroic": ["#FF6B35", "#F7931E", "#FFC857", "#2E4057"],
        "cool_mysterious": ["#1A1A2E", "#16213E", "#0F3460", "#E94560"],
        "pastel_dreamy": ["#FFB5E8", "#B5DEFF", "#85E3FF", "#B5FFD9"],
        "dark_dramatic": ["#0D0D0D", "#1A1A1A", "#8B0000", "#FFD700"],
        "nature_organic": ["#2D5A27", "#8B9556", "#D4A574", "#F5E6D3"],
        "cyberpunk": ["#0D0D0D", "#FF00FF", "#00FFFF", "#FFE600"]
    }
    
    SYSTEM_PROMPT = """You are the Art Direction Engine.

Your job is to generate complete, actionable art direction for any creative project.
You define visual identity, style rules, composition guidelines, palettes, mood, and production constraints.

You do NOT generate images.
You define the direction that image models, artists, or pipelines should follow.

RULES:
1. Always return valid JSON only — no markdown, no commentary.
2. Art direction must be ORIGINAL and not based on copyrighted works.
3. Focus on clarity, consistency, and production-ready detail.
4. No disclaimers, no model identity, no filler.
5. Ensure all attributes are concrete, specific, and usable.
6. Use valid hex color codes for all palette colors.
7. Be specific enough that an artist could execute without further clarification.

OUTPUT FORMAT (JSON ONLY):
{
  "project_name": "Name of the project",
  "visual_style": {
    "genre": "anime | cinematic | painterly | stylized | minimalist | mixed",
    "influences": ["Non-copyrighted influence 1", "Aesthetic movement 2"],
    "description": "High-level description of the visual identity"
  },
  "color_palette": {
    "primary": ["#hex1", "#hex2"],
    "secondary": ["#hex1", "#hex2"],
    "accents": ["#hex1"],
    "mood_notes": "How the palette should feel"
  },
  "character_style": {
    "proportions": "Description of body/head ratio",
    "linework": "Line weight, texture, consistency",
    "shading": "Flat | cel-shaded | soft | painterly",
    "expression_rules": ["Rule 1", "Rule 2"],
    "silhouette_rules": ["Rule 1", "Rule 2"]
  },
  "environment_style": {
    "lighting": "Lighting rules and mood",
    "atmosphere": "Mood and atmospheric effects",
    "detail_level": "Low | medium | high",
    "composition_rules": ["Rule 1", "Rule 2"]
  },
  "camera_direction": {
    "framing": ["Shot types to use"],
    "angles": ["Angle preferences"],
    "motion_rules": ["How movement should be conveyed"]
  },
  "texture_rules": {
    "materials": ["Key materials in the world"],
    "surface_treatment": "How surfaces should look",
    "consistency_requirements": ["Rule 1"]
  },
  "production_constraints": ["Technical constraint 1", "Constraint 2"],
  "do_not_use": ["Elements or styles to avoid"]
}

Return ONLY the JSON object. No other text."""

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
            session_id=f"art-direction-{model}",
            system_message=cls.SYSTEM_PROMPT
        ).with_model(provider, model_name)
        
        return chat
    
    @classmethod
    async def generate_direction_async(
        cls,
        project: str,
        genre: Optional[str] = None,
        mood: Optional[str] = None,
        target_audience: Optional[str] = None,
        medium: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> dict:
        """
        Generate art direction for a project.
        
        Args:
            project: Project name/description
            genre: Visual style genre
            mood: Desired emotional mood
            target_audience: Who this is for
            medium: Output medium (game, film, illustration, etc.)
            constraints: Production constraints
            model: Override LLM model selection
            
        Returns:
            ArtDirection as dict
        """
        chat = cls._create_chat(model)
        
        # Build prompt
        prompt_parts = [f"Create art direction for: {project}"]
        
        if genre:
            prompt_parts.append(f"\nVisual genre: {genre}")
        
        if mood:
            prompt_parts.append(f"\nDesired mood: {mood}")
        
        if target_audience:
            prompt_parts.append(f"\nTarget audience: {target_audience}")
        
        if medium:
            prompt_parts.append(f"\nOutput medium: {medium}")
        
        if constraints:
            prompt_parts.append(f"\nProduction constraints: {', '.join(constraints)}")
        
        prompt = "\n".join(prompt_parts)
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Parse JSON from response
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
            return {
                "project_name": project,
                "visual_style": {
                    "genre": genre or "mixed",
                    "influences": ["TBD"],
                    "description": "Art direction generation failed - retry required"
                },
                "color_palette": {
                    "primary": ["#333333", "#666666"],
                    "secondary": ["#999999"],
                    "accents": ["#FF0000"],
                    "mood_notes": "Placeholder palette"
                },
                "character_style": {
                    "proportions": "TBD",
                    "linework": "TBD",
                    "shading": "TBD",
                    "expression_rules": [],
                    "silhouette_rules": []
                },
                "environment_style": {
                    "lighting": "TBD",
                    "atmosphere": "TBD",
                    "detail_level": "medium",
                    "composition_rules": []
                },
                "camera_direction": {
                    "framing": [],
                    "angles": [],
                    "motion_rules": []
                },
                "texture_rules": {
                    "materials": [],
                    "surface_treatment": "TBD",
                    "consistency_requirements": []
                },
                "production_constraints": constraints or [],
                "do_not_use": []
            }
    
    @classmethod
    def generate_direction(
        cls,
        project: str,
        genre: Optional[str] = None,
        mood: Optional[str] = None,
        target_audience: Optional[str] = None,
        medium: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> dict:
        """Synchronous wrapper for art direction generation."""
        return asyncio.run(cls.generate_direction_async(
            project, genre, mood, target_audience, medium, constraints, model
        ))
    
    @classmethod
    async def anime_direction_async(
        cls,
        project: str,
        sub_style: Optional[str] = None,
        era: Optional[str] = None
    ) -> dict:
        """Generate anime-specific art direction."""
        genre = "anime"
        mood = sub_style or "modern action anime"
        
        constraints = []
        if era:
            constraints.append(f"Visual era reference: {era}")
        
        return await cls.generate_direction_async(
            project=project,
            genre=genre,
            mood=mood,
            constraints=constraints if constraints else None
        )
    
    @classmethod
    async def game_direction_async(
        cls,
        project: str,
        game_genre: str,
        platform: Optional[str] = None
    ) -> dict:
        """Generate game-specific art direction."""
        constraints = [f"Game genre: {game_genre}"]
        if platform:
            constraints.append(f"Platform: {platform}")
        
        return await cls.generate_direction_async(
            project=project,
            medium="video game",
            constraints=constraints
        )
    
    @classmethod
    async def film_direction_async(
        cls,
        project: str,
        film_genre: str,
        aspect_ratio: Optional[str] = None
    ) -> dict:
        """Generate film/animation-specific art direction."""
        constraints = [f"Film genre: {film_genre}"]
        if aspect_ratio:
            constraints.append(f"Aspect ratio: {aspect_ratio}")
        
        return await cls.generate_direction_async(
            project=project,
            genre="cinematic",
            medium="film/animation",
            constraints=constraints
        )
    
    @classmethod
    async def brand_direction_async(
        cls,
        brand_name: str,
        industry: str,
        personality: List[str]
    ) -> dict:
        """Generate brand visual identity direction."""
        project = f"Brand identity for {brand_name}"
        mood = ", ".join(personality)
        
        return await cls.generate_direction_async(
            project=project,
            mood=mood,
            target_audience=f"{industry} market",
            medium="brand identity"
        )
    
    @classmethod
    async def character_art_direction_async(
        cls,
        character_name: str,
        character_type: str,
        visual_style: str
    ) -> dict:
        """Generate character-specific art direction."""
        project = f"Character design: {character_name} ({character_type})"
        
        return await cls.generate_direction_async(
            project=project,
            genre=visual_style,
            medium="character design"
        )
    
    @classmethod
    def get_style_templates(cls) -> dict:
        """Get available style templates."""
        return cls.STYLE_TEMPLATES
    
    @classmethod
    def get_color_moods(cls) -> dict:
        """Get available color mood presets."""
        return cls.COLOR_MOODS
