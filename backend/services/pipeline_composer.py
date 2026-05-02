"""
Pipeline Composer Engine

Orchestrates multi-engine workflows inside the Hybrid Intelligence Core.
Determines which engines to call, in what order, and how to combine outputs.
"""

from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

load_dotenv()


class PipelineStep(BaseModel):
    """Single step in a composed pipeline."""
    engine: str
    input: str
    output_key: str


class ComposedPipeline(BaseModel):
    """Complete pipeline composition."""
    objective: str
    pipeline: List[PipelineStep]
    final_output_structure: Dict[str, Any]


class PipelineComposerEngine:
    """Orchestrates multi-engine workflows."""
    
    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-5.2"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "gemini-3-flash": ("gemini", "gemini-3-flash-preview")
    }
    
    # Default to GPT for orchestration (strong at structured reasoning)
    DEFAULT_MODEL = "gpt-5.2"
    
    # Available engines and their capabilities
    AVAILABLE_ENGINES = {
        "strategy_engine": {
            "purpose": "Generate high-level strategies",
            "input": "goal, context, tone",
            "output": "summary, steps, risks, resources, next_action"
        },
        "plan_builder_engine": {
            "purpose": "Convert goals/strategies into execution plans",
            "input": "goal, strategy, context",
            "output": "objective, phases, milestones, critical_path, first_24_hours"
        },
        "analysis_engine": {
            "purpose": "Deep SWOT analysis",
            "input": "subject, context, focus_area",
            "output": "overview, strengths, weaknesses, opportunities, threats, key_insights, recommended_focus"
        },
        "opportunity_mapper_engine": {
            "purpose": "Identify high-leverage opportunities",
            "input": "situation, context, constraints, goals",
            "output": "context_summary, opportunities, top_3_opportunities, recommended_next_move"
        },
        "evaluator_engine": {
            "purpose": "Score and evaluate with criteria",
            "input": "subject, content, criteria_preset",
            "output": "criteria, weighted_score, strengths, weaknesses, improvement_suggestions, go_no_go"
        },
        "pricing_engine": {
            "purpose": "Generate pricing structures",
            "input": "product, description, target_market, pricing_model",
            "output": "offer_summary, target_segments, pricing_model, tiers, monetization_risks, expansion_opportunities"
        },
        "blueprint_engine": {
            "purpose": "System architecture blueprints",
            "input": "system_description, requirements, constraints",
            "output": "objective, components, data_flows, constraints, risks"
        },
        "persona_engine": {
            "purpose": "User/customer persona generation",
            "input": "audience, context, product, industry",
            "output": "name, role, background, goals, pains, triggers, buying_criteria, objections"
        },
        "anime_character_engine": {
            "purpose": "Original anime character creation",
            "input": "concept, role, genre, abilities_type",
            "output": "name, role, appearance, personality, abilities, motivations, backstory, arc"
        },
        "anime_lore_engine": {
            "purpose": "World-building, mythology, factions, history for anime/fantasy",
            "input": "world_concept, genre, themes, influences",
            "output": "world_name, setting, core_mythology, factions, locations, power_system, history, mysteries"
        },
        "anime_story_engine": {
            "purpose": "Narrative structure, story arcs, plot points, episode breakdowns",
            "input": "concept, genre, episode_count, characters, lore",
            "output": "title, logline, premise, themes, story_arcs, key_plot_points, climax, resolution, hooks"
        },
        "art_direction_engine": {
            "purpose": "Complete art direction for creative projects",
            "input": "project, genre, mood, target_audience, medium",
            "output": "visual_style, color_palette, character_style, environment_style, camera_direction, texture_rules"
        },
        "money_pipeline_engine": {
            "purpose": "Transform any idea into complete monetizable system",
            "input": "idea, context, industry, target_revenue, constraints",
            "output": "market_analysis, opportunity_map, pricing_model, business_model, product_blueprint, execution_plan, forecast, marketing_funnel, launch_strategy"
        }
    }
    
    # Pre-built pipeline templates
    PIPELINE_TEMPLATES = {
        "full_business_plan": [
            {"engine": "strategy_engine", "input": "goal", "output_key": "strategy"},
            {"engine": "analysis_engine", "input": "strategy.summary", "output_key": "analysis"},
            {"engine": "opportunity_mapper_engine", "input": "strategy", "output_key": "opportunities"},
            {"engine": "plan_builder_engine", "input": "strategy", "output_key": "execution_plan"},
            {"engine": "pricing_engine", "input": "strategy.summary", "output_key": "pricing"},
            {"engine": "evaluator_engine", "input": "strategy", "output_key": "evaluation"}
        ],
        "product_launch": [
            {"engine": "persona_engine", "input": "target_audience", "output_key": "personas"},
            {"engine": "strategy_engine", "input": "product_goal", "output_key": "strategy"},
            {"engine": "pricing_engine", "input": "product", "output_key": "pricing"},
            {"engine": "plan_builder_engine", "input": "strategy", "output_key": "launch_plan"}
        ],
        "startup_validation": [
            {"engine": "analysis_engine", "input": "business_idea", "output_key": "market_analysis"},
            {"engine": "persona_engine", "input": "target_customer", "output_key": "icp"},
            {"engine": "opportunity_mapper_engine", "input": "market", "output_key": "opportunities"},
            {"engine": "evaluator_engine", "input": "business_idea", "output_key": "viability_score"}
        ],
        "system_design": [
            {"engine": "strategy_engine", "input": "system_goal", "output_key": "strategy"},
            {"engine": "blueprint_engine", "input": "system_requirements", "output_key": "architecture"},
            {"engine": "plan_builder_engine", "input": "implementation", "output_key": "build_plan"},
            {"engine": "evaluator_engine", "input": "architecture", "output_key": "architecture_review"}
        ],
        "idea_to_money": [
            {"engine": "money_pipeline_engine", "input": "idea", "output_key": "money_pipeline"},
            {"engine": "persona_engine", "input": "money_pipeline.market_analysis.target_segments", "output_key": "personas"},
            {"engine": "blueprint_engine", "input": "money_pipeline.product_blueprint", "output_key": "tech_architecture"},
            {"engine": "evaluator_engine", "input": "money_pipeline", "output_key": "viability_assessment"}
        ],
        "anime_full_concept": [
            {"engine": "anime_lore_engine", "input": "world_concept", "output_key": "lore"},
            {"engine": "anime_story_engine", "input": "lore", "output_key": "story"},
            {"engine": "anime_character_engine", "input": "story.premise", "output_key": "protagonist"},
            {"engine": "anime_character_engine", "input": "story.premise, role=antagonist", "output_key": "antagonist"},
            {"engine": "art_direction_engine", "input": "story, lore", "output_key": "art_direction"}
        ],
        "saas_monetization": [
            {"engine": "money_pipeline_engine", "input": "saas_idea", "output_key": "full_pipeline"},
            {"engine": "blueprint_engine", "input": "full_pipeline.product_blueprint", "output_key": "architecture"},
            {"engine": "plan_builder_engine", "input": "full_pipeline.execution_plan", "output_key": "detailed_plan"}
        ]
    }
    
    SYSTEM_PROMPT = """You are the Pipeline Composer Engine.

Your job is to orchestrate multi-engine workflows inside the Hybrid Intelligence Core.
You do not generate content yourself.
You determine which engines to call, in what order, and how to combine their outputs.

AVAILABLE ENGINES:
- strategy_engine: Generate high-level strategies (output: summary, steps, risks, resources, next_action)
- plan_builder_engine: Convert goals to execution plans (output: objective, phases, milestones, critical_path)
- analysis_engine: Deep SWOT analysis (output: overview, strengths, weaknesses, opportunities, threats)
- opportunity_mapper_engine: Identify opportunities (output: opportunities, top_3_opportunities, recommended_next_move)
- evaluator_engine: Score and evaluate (output: weighted_score, go_no_go, improvement_suggestions)
- pricing_engine: Generate pricing (output: tiers, pricing_model, monetization_risks)
- blueprint_engine: System architecture (output: components, data_flows, constraints)
- persona_engine: User personas (output: name, goals, pains, triggers, buying_criteria)
- anime_character_engine: Anime characters (output: name, abilities, backstory, arc)
- anime_lore_engine: World-building and mythology (output: world_name, factions, power_system, history)
- anime_story_engine: Story arcs and plot (output: title, story_arcs, key_plot_points, climax)
- art_direction_engine: Visual direction (output: visual_style, color_palette, character_style)
- money_pipeline_engine: Complete monetization system (output: market_analysis, pricing_model, business_model, execution_plan, forecast, marketing_funnel, launch_strategy)

RULES:
1. Always return valid JSON only — no markdown, no commentary.
2. Identify required engines based on user's request.
3. Define sequence of engine calls (order matters for dependencies).
4. Specify input each engine receives (can reference previous outputs).
5. Specify how outputs merge into final result.
6. Do not invent content — only orchestrate.
7. Use output_key to reference previous engine outputs in later inputs.
8. For monetization/business requests, prefer money_pipeline_engine as primary engine.
9. For anime/creative projects, chain lore → story → character → art_direction.

OUTPUT FORMAT (JSON ONLY):
{
  "objective": "What the user wants to achieve",
  "pipeline": [
    {
      "engine": "engine_name",
      "input": "What this engine should receive (can reference {previous_output_key})",
      "output_key": "key_name_for_this_output"
    }
  ],
  "final_output_structure": {
    "description": "How the combined output should be structured",
    "sections": ["section1", "section2"]
  }
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
            session_id=f"pipeline-composer-{model}",
            system_message=cls.SYSTEM_PROMPT
        ).with_model(provider, model_name)
        
        return chat
    
    @classmethod
    async def compose_pipeline_async(
        cls,
        request: str,
        context: Optional[str] = None,
        preferred_engines: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> dict:
        """
        Compose a pipeline based on user request.
        
        Args:
            request: What the user wants to achieve
            context: Additional context
            preferred_engines: Engines to prioritize
            model: Override LLM model selection
            
        Returns:
            ComposedPipeline as dict
        """
        chat = cls._create_chat(model)
        
        # Build prompt
        prompt_parts = [f"Compose a multi-engine pipeline for: {request}"]
        
        if context:
            prompt_parts.append(f"\nContext: {context}")
        
        if preferred_engines:
            prompt_parts.append(f"\nPreferred engines to include: {', '.join(preferred_engines)}")
        
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
                "objective": request,
                "pipeline": [
                    {
                        "engine": "strategy_engine",
                        "input": request,
                        "output_key": "strategy"
                    }
                ],
                "final_output_structure": {
                    "description": "Single engine output - pipeline composition failed",
                    "sections": ["strategy"]
                }
            }
    
    @classmethod
    def compose_pipeline(
        cls,
        request: str,
        context: Optional[str] = None,
        preferred_engines: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> dict:
        """Synchronous wrapper for pipeline composition."""
        return asyncio.run(cls.compose_pipeline_async(
            request, context, preferred_engines, model
        ))
    
    @classmethod
    def get_template(cls, template_name: str) -> Optional[List[dict]]:
        """Get a pre-built pipeline template."""
        return cls.PIPELINE_TEMPLATES.get(template_name)
    
    @classmethod
    def get_available_templates(cls) -> dict:
        """Get all available pipeline templates."""
        return {
            name: [step["engine"] for step in steps]
            for name, steps in cls.PIPELINE_TEMPLATES.items()
        }
    
    @classmethod
    def get_available_engines(cls) -> dict:
        """Get all available engines and their capabilities."""
        return cls.AVAILABLE_ENGINES
    
    @classmethod
    def validate_pipeline(cls, pipeline: List[dict]) -> dict:
        """
        Validate a pipeline configuration.
        
        Args:
            pipeline: List of pipeline steps
            
        Returns:
            Validation result
        """
        errors = []
        warnings = []
        valid_engines = set(cls.AVAILABLE_ENGINES.keys())
        output_keys = set()
        
        for i, step in enumerate(pipeline):
            engine = step.get("engine")
            output_key = step.get("output_key")
            
            # Check engine exists
            if engine not in valid_engines:
                errors.append(f"Step {i+1}: Unknown engine '{engine}'")
            
            # Check output_key is unique
            if output_key in output_keys:
                warnings.append(f"Step {i+1}: Duplicate output_key '{output_key}'")
            output_keys.add(output_key)
            
            # Check required fields
            if not step.get("input"):
                warnings.append(f"Step {i+1}: Missing input specification")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "step_count": len(pipeline),
            "engines_used": list(set(s.get("engine") for s in pipeline))
        }
    
    @classmethod
    async def compose_and_describe_async(
        cls,
        request: str,
        include_descriptions: bool = True
    ) -> dict:
        """
        Compose pipeline and include engine descriptions.
        
        Args:
            request: What the user wants to achieve
            include_descriptions: Include detailed engine info
            
        Returns:
            Pipeline with descriptions
        """
        pipeline = await cls.compose_pipeline_async(request)
        
        if include_descriptions:
            for step in pipeline.get("pipeline", []):
                engine_name = step.get("engine")
                if engine_name in cls.AVAILABLE_ENGINES:
                    step["engine_info"] = cls.AVAILABLE_ENGINES[engine_name]
        
        return pipeline
    
    @classmethod
    def build_custom_pipeline(
        cls,
        objective: str,
        steps: List[Dict[str, str]]
    ) -> dict:
        """
        Build a custom pipeline from explicit steps.
        
        Args:
            objective: Pipeline objective
            steps: List of {"engine": "...", "input": "...", "output_key": "..."}
            
        Returns:
            Validated pipeline configuration
        """
        validation = cls.validate_pipeline(steps)
        
        return {
            "objective": objective,
            "pipeline": steps,
            "final_output_structure": {
                "description": f"Combined output from {len(steps)} engines",
                "sections": [s.get("output_key") for s in steps]
            },
            "validation": validation
        }
