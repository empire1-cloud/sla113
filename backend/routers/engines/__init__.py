"""
Engine routers for the Hybrid Intelligence system.
"""
from .core import router as core_router
from .strategy import router as strategy_router
from .drift import router as drift_router
from .plan import router as plan_router
from .analysis import router as analysis_router
from .opportunity import router as opportunity_router
from .evaluator import router as evaluator_router
from .pricing import router as pricing_router
from .blueprint import router as blueprint_router
from .persona import router as persona_router
from .pipeline import router as pipeline_router
from .anime_character import router as anime_character_router
from .anime_lore import router as anime_lore_router
from .anime_story import router as anime_story_router
from .art_direction import router as art_direction_router
from .money_pipeline import router as money_pipeline_router
from .analytics import router as analytics_router

__all__ = [
    "core_router",
    "strategy_router",
    "drift_router",
    "plan_router",
    "analysis_router",
    "opportunity_router",
    "evaluator_router",
    "pricing_router",
    "blueprint_router",
    "persona_router",
    "pipeline_router",
    "anime_character_router",
    "anime_lore_router",
    "anime_story_router",
    "art_direction_router",
    "money_pipeline_router",
    "analytics_router",
]
