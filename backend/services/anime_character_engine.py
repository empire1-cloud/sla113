"""
Anime Character Engine

Generates detailed, original anime-style characters with clear
personalities, motivations, abilities, and narrative roles.
"""

from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import Optional, List, Dict
from pydantic import BaseModel

load_dotenv()


class CharacterRelationships(BaseModel):
    """Character relationship structure."""
    allies: List[str]
    rivals: List[str]
    enemies: List[str]


class AnimeCharacter(BaseModel):
    """Complete anime character definition."""
    name: str
    role: str  # Protagonist | Antagonist | Support | Rival | Mentor | Other
    appearance: str
    personality: List[str]
    abilities: List[str]
    motivations: List[str]
    backstory: str
    relationships: CharacterRelationships
    arc: str


class AnimeCharacterEngine:
    """Generates original anime-style characters."""
    
    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-5.2"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "gemini-3-flash": ("gemini", "gemini-3-flash-preview")
    }
    
    # Default to Claude for creative character work
    DEFAULT_MODEL = "claude-sonnet-4.5"
    
    # Character archetypes
    ARCHETYPES = {
        "protagonist": {
            "classic_hero": "Determined, grows through adversity, strong moral compass",
            "reluctant_hero": "Pulled into conflict, doubts themselves, discovers inner strength",
            "anti_hero": "Morally gray, pragmatic, achieves good through questionable means",
            "chosen_one": "Destined for greatness, burdened by prophecy, unique power"
        },
        "antagonist": {
            "fallen_hero": "Once good, corrupted by tragedy or power",
            "ideological": "Believes they're right, wants to reshape the world",
            "rival_turned_enemy": "Former ally with conflicting goals",
            "force_of_nature": "Beyond morality, represents chaos or destruction"
        },
        "support": {
            "best_friend": "Loyal, comic relief, grounds the protagonist",
            "mentor": "Wise, experienced, has hidden past",
            "love_interest": "Emotional anchor, own goals and agency",
            "team_member": "Specialized skills, complementary to protagonist"
        }
    }
    
    # Genre templates
    GENRES = {
        "shonen": "Action-focused, themes of friendship, training arcs, power progression",
        "shojo": "Emotional depth, relationships, personal growth, aesthetic beauty",
        "seinen": "Mature themes, complex morality, realistic consequences",
        "isekai": "Transported to another world, unique abilities, world-building focus",
        "mecha": "Giant robots, military themes, technology vs humanity",
        "slice_of_life": "Everyday moments, subtle character development, relatable struggles"
    }
    
    SYSTEM_PROMPT = """You are the Anime Character Engine.

Your job is to generate detailed, original anime-style characters with clear personalities, motivations, abilities, and narrative roles.

RULES:
1. Always return valid JSON only — no markdown, no commentary.
2. Characters must be ORIGINAL and not based on copyrighted anime characters.
3. Focus on personality, motivations, abilities, and narrative function.
4. No disclaimers, no model identity, no filler.
5. Ensure all attributes are concrete, specific, and usable.
6. Include Japanese-style naming conventions when appropriate.
7. Make abilities and powers internally consistent.
8. Backstory should explain motivations and abilities.

OUTPUT FORMAT (JSON ONLY):
{
  "name": "Character name (can include Japanese name)",
  "role": "Protagonist | Antagonist | Support | Rival | Mentor | Other",
  "appearance": "Physical description including hair, eyes, outfit, distinctive features, anime style notes.",
  "personality": ["Trait 1", "Trait 2", "Trait 3"],
  "abilities": ["Ability 1 with description", "Ability 2 with description"],
  "motivations": ["Primary motivation", "Secondary motivation"],
  "backstory": "Origin story explaining who they are and why (2-4 sentences).",
  "relationships": {
    "allies": ["Ally name/type"],
    "rivals": ["Rival name/type"],
    "enemies": ["Enemy name/type"]
  },
  "arc": "How the character evolves over the story (1-2 sentences)."
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
            session_id=f"anime-character-{model}",
            system_message=cls.SYSTEM_PROMPT
        ).with_model(provider, model_name)
        
        return chat
    
    @classmethod
    async def generate_character_async(
        cls,
        concept: str,
        role: Optional[str] = None,
        genre: Optional[str] = None,
        abilities_type: Optional[str] = None,
        context: Optional[str] = None,
        model: Optional[str] = None
    ) -> dict:
        """
        Generate an anime character.
        
        Args:
            concept: Character concept or description
            role: Character role (protagonist, antagonist, etc.)
            genre: Anime genre (shonen, seinen, isekai, etc.)
            abilities_type: Type of powers (magic, martial arts, tech, etc.)
            context: Story or world context
            model: Override LLM model selection
            
        Returns:
            AnimeCharacter as dict
        """
        chat = cls._create_chat(model)
        
        # Build prompt
        prompt_parts = [f"Create an original anime character: {concept}"]
        
        if role:
            prompt_parts.append(f"\nRole: {role}")
        
        if genre:
            genre_desc = cls.GENRES.get(genre.lower(), genre)
            prompt_parts.append(f"\nGenre: {genre} - {genre_desc}")
        
        if abilities_type:
            prompt_parts.append(f"\nAbilities type: {abilities_type}")
        
        if context:
            prompt_parts.append(f"\nStory context: {context}")
        
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
                "name": "Unknown Character",
                "role": role or "Other",
                "appearance": "Character generation failed",
                "personality": ["TBD"],
                "abilities": ["TBD"],
                "motivations": ["TBD"],
                "backstory": "Retry required",
                "relationships": {"allies": [], "rivals": [], "enemies": []},
                "arc": "TBD"
            }
    
    @classmethod
    def generate_character(
        cls,
        concept: str,
        role: Optional[str] = None,
        genre: Optional[str] = None,
        abilities_type: Optional[str] = None,
        context: Optional[str] = None,
        model: Optional[str] = None
    ) -> dict:
        """Synchronous wrapper for character generation."""
        return asyncio.run(cls.generate_character_async(
            concept, role, genre, abilities_type, context, model
        ))
    
    @classmethod
    async def generate_protagonist_async(
        cls,
        concept: str,
        genre: Optional[str] = None,
        abilities_type: Optional[str] = None
    ) -> dict:
        """Generate a protagonist character."""
        return await cls.generate_character_async(
            concept=concept,
            role="Protagonist",
            genre=genre,
            abilities_type=abilities_type
        )
    
    @classmethod
    async def generate_antagonist_async(
        cls,
        concept: str,
        genre: Optional[str] = None,
        protagonist: Optional[str] = None
    ) -> dict:
        """Generate an antagonist character."""
        context = f"Antagonist to protagonist: {protagonist}" if protagonist else None
        return await cls.generate_character_async(
            concept=concept,
            role="Antagonist",
            genre=genre,
            context=context
        )
    
    @classmethod
    async def generate_cast_async(
        cls,
        story_concept: str,
        genre: Optional[str] = None,
        cast_size: int = 5
    ) -> List[dict]:
        """
        Generate a full cast of characters.
        
        Args:
            story_concept: Overall story concept
            genre: Anime genre
            cast_size: Number of characters (default 5)
            
        Returns:
            List of character dicts
        """
        roles = ["Protagonist", "Antagonist", "Support", "Rival", "Mentor"][:cast_size]
        characters = []
        
        for role in roles:
            char = await cls.generate_character_async(
                concept=f"{role} for story: {story_concept}",
                role=role,
                genre=genre
            )
            characters.append(char)
        
        return characters
    
    @classmethod
    async def generate_villain_async(
        cls,
        concept: str,
        villain_type: Optional[str] = None,
        genre: Optional[str] = None
    ) -> dict:
        """Generate a villain character with specific archetype."""
        archetype_desc = ""
        if villain_type and villain_type.lower() in cls.ARCHETYPES["antagonist"]:
            archetype_desc = cls.ARCHETYPES["antagonist"][villain_type.lower()]
        
        context = f"Villain archetype: {villain_type} - {archetype_desc}" if archetype_desc else None
        
        return await cls.generate_character_async(
            concept=concept,
            role="Antagonist",
            genre=genre,
            context=context
        )
    
    @classmethod
    def get_archetypes(cls) -> dict:
        """Get available character archetypes."""
        return cls.ARCHETYPES
    
    @classmethod
    def get_genres(cls) -> dict:
        """Get available anime genres."""
        return cls.GENRES
