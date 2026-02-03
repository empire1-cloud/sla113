from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import Optional, List
from pydantic import BaseModel

load_dotenv()

class Task(BaseModel):
    task: str
    steps: List[str]
    owner: str
    dependencies: List[str]

class Phase(BaseModel):
    name: str
    duration: str
    tasks: List[Task]

class ExecutionPlan(BaseModel):
    objective: str
    phases: List[Phase]
    milestones: List[str]
    critical_path: List[str]
    first_24_hours: List[str]

class PlanBuilderEngine:
    """Converts goals/strategies into actionable execution plans."""
    
    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-5.2"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "gemini-3-flash": ("gemini", "gemini-3-flash-preview")
    }
    
    # Default to GPT-5.2 for planning (complex reasoning)
    DEFAULT_MODEL = "gpt-5.2"
    
    SYSTEM_PROMPT = """You are the Plan Builder Engine.

Your job is to convert a goal or strategy into a clear, actionable execution plan with timelines, milestones, and dependencies.

RULES:
1. Always return valid JSON only — no markdown, no explanations outside JSON.
2. Focus on clarity, sequencing, and feasibility.
3. Break work into phases, tasks, and sub-tasks.
4. Never drift into high-level strategy — stay tactical.
5. No disclaimers, no model identity, no filler.
6. Be specific with time estimates and owners.
7. Identify real dependencies that block progress.

OUTPUT FORMAT (JSON ONLY):
{
  "objective": "Clear statement of what the plan will accomplish.",
  "phases": [
    {
      "name": "Phase name",
      "duration": "Estimated time window (e.g., 'Week 1-2', '3 days')",
      "tasks": [
        {
          "task": "Specific action item",
          "steps": ["Step 1", "Step 2", "Step 3"],
          "owner": "Role or persona responsible",
          "dependencies": ["What must be done first"]
        }
      ]
    }
  ],
  "milestones": ["Key deliverable 1", "Key deliverable 2"],
  "critical_path": ["Blocking task 1", "Blocking task 2"],
  "first_24_hours": ["Immediate action 1", "Immediate action 2", "Immediate action 3"]
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
            session_id=f"plan-builder-{model}",
            system_message=cls.SYSTEM_PROMPT
        ).with_model(provider, model_name)
        
        return chat
    
    @classmethod
    async def build_plan_async(
        cls,
        goal: str,
        strategy: Optional[dict] = None,
        context: Optional[str] = None,
        model: Optional[str] = None
    ) -> dict:
        """
        Build an execution plan from a goal or strategy.
        
        Args:
            goal: The objective to plan for
            strategy: Optional strategy dict from Strategy Engine
            context: Additional context
            model: Override model selection
            
        Returns:
            ExecutionPlan as dict
        """
        chat = cls._create_chat(model)
        
        # Build prompt
        prompt_parts = [f"Goal: {goal}"]
        
        if strategy:
            prompt_parts.append(f"\nStrategy to execute:\n{json.dumps(strategy, indent=2)}")
        
        if context:
            prompt_parts.append(f"\nAdditional context: {context}")
        
        prompt = "\n".join(prompt_parts)
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Parse JSON from response
        try:
            # Extract JSON if wrapped in markdown
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
            # Return structured fallback
            return {
                "objective": goal,
                "phases": [
                    {
                        "name": "Initial Phase",
                        "duration": "TBD",
                        "tasks": [
                            {
                                "task": "Review and refine plan",
                                "steps": ["Parse response", "Extract actionable items"],
                                "owner": "Operator",
                                "dependencies": []
                            }
                        ]
                    }
                ],
                "milestones": ["Plan refinement complete"],
                "critical_path": ["Manual review required"],
                "first_24_hours": ["Retry with more specific goal"]
            }
    
    @classmethod
    def build_plan(
        cls,
        goal: str,
        strategy: Optional[dict] = None,
        context: Optional[str] = None,
        model: Optional[str] = None
    ) -> dict:
        """Synchronous wrapper for plan building."""
        return asyncio.run(cls.build_plan_async(goal, strategy, context, model))
    
    @classmethod
    async def convert_strategy_to_plan_async(cls, strategy: dict) -> dict:
        """
        Convert a Strategy Engine output directly into an execution plan.
        
        Args:
            strategy: Output from Strategy Engine
            
        Returns:
            ExecutionPlan as dict
        """
        goal = strategy.get("summary", "Execute the provided strategy")
        return await cls.build_plan_async(goal=goal, strategy=strategy)
