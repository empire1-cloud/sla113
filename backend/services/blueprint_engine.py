"""
Blueprint Engine

Generates clear, structured system or product blueprints.
Defines components, responsibilities, data flows, and constraints — without code.
"""

from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import Optional, List
from pydantic import BaseModel

load_dotenv()


class Component(BaseModel):
    """System component definition."""
    name: str
    type: str  # service | module | datastore | ui | integration | other
    responsibilities: List[str]
    inputs: List[str]
    outputs: List[str]
    dependencies: List[str]


class DataFlow(BaseModel):
    """Data flow between components."""
    from_component: str  # 'from' is reserved
    to: str
    data: str
    frequency: str  # real_time | on_demand | batch


class Blueprint(BaseModel):
    """Complete system blueprint output."""
    objective: str
    components: List[Component]
    data_flows: List[DataFlow]
    constraints: List[str]
    risks: List[str]


class BlueprintEngine:
    """Generates system and product blueprints."""
    
    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-5.2"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "gemini-3-flash": ("gemini", "gemini-3-flash-preview")
    }
    
    # Default to GPT-5.2 for architecture (strong at structured system design)
    DEFAULT_MODEL = "gpt-5.2"
    
    # Component type templates
    COMPONENT_TYPES = {
        "service": "Backend service/API that processes requests",
        "module": "Internal module or library",
        "datastore": "Database, cache, or storage system",
        "ui": "User interface component",
        "integration": "External API or third-party integration",
        "queue": "Message queue or event bus",
        "gateway": "API gateway or load balancer",
        "worker": "Background job processor",
        "other": "Other component type"
    }
    
    SYSTEM_PROMPT = """You are the Blueprint Engine.

Your job is to generate a clear, structured system or product blueprint based on the user's description, requirements, or goals.
You define components, responsibilities, data flows, and constraints — without writing code.

RULES:
1. Always return valid JSON only — no markdown, no commentary.
2. Focus on structure, interfaces, and responsibilities.
3. Do not generate code. Do not propose strategies. Stay architectural.
4. No disclaimers, no model identity, no filler.
5. Be explicit about dependencies and data flows.
6. Ensure all components are cohesive, modular, and clearly defined.
7. Include 5-10 components for a typical system.
8. Map all data flows between dependent components.

OUTPUT FORMAT (JSON ONLY):
{
  "objective": "What this system/product is meant to achieve.",
  "components": [
    {
      "name": "Component name",
      "type": "service | module | datastore | ui | integration | other",
      "responsibilities": ["Responsibility 1", "Responsibility 2"],
      "inputs": ["Input 1", "Input 2"],
      "outputs": ["Output 1", "Output 2"],
      "dependencies": ["Component A", "Component B"]
    }
  ],
  "data_flows": [
    {
      "from": "Component A",
      "to": "Component B",
      "data": "What is passed",
      "frequency": "real_time | on_demand | batch"
    }
  ],
  "constraints": ["Constraint 1", "Constraint 2"],
  "risks": ["Risk 1", "Risk 2"]
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
            session_id=f"blueprint-{model}",
            system_message=cls.SYSTEM_PROMPT
        ).with_model(provider, model_name)
        
        return chat
    
    @classmethod
    async def generate_blueprint_async(
        cls,
        system_description: str,
        requirements: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        tech_stack: Optional[List[str]] = None,
        scale: Optional[str] = None,
        model: Optional[str] = None
    ) -> dict:
        """
        Generate a system blueprint.
        
        Args:
            system_description: What the system should do
            requirements: Functional requirements
            constraints: Non-functional constraints
            tech_stack: Preferred technologies
            scale: Expected scale (e.g., "100 users", "1M requests/day")
            model: Override LLM model selection
            
        Returns:
            Blueprint as dict
        """
        chat = cls._create_chat(model)
        
        # Build prompt
        prompt_parts = [f"Generate a system blueprint for: {system_description}"]
        
        if requirements:
            prompt_parts.append(f"\nRequirements:\n- " + "\n- ".join(requirements))
        
        if constraints:
            prompt_parts.append(f"\nConstraints:\n- " + "\n- ".join(constraints))
        
        if tech_stack:
            prompt_parts.append(f"\nPreferred tech stack: {', '.join(tech_stack)}")
        
        if scale:
            prompt_parts.append(f"\nExpected scale: {scale}")
        
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
            
            result = json.loads(response)
            
            # Normalize data_flows 'from' field
            if "data_flows" in result:
                for flow in result["data_flows"]:
                    if "from" in flow and "from_component" not in flow:
                        flow["from_component"] = flow.pop("from")
            
            return result
        except json.JSONDecodeError:
            return {
                "objective": system_description,
                "components": [
                    {
                        "name": "Core System",
                        "type": "service",
                        "responsibilities": ["Primary functionality"],
                        "inputs": ["User requests"],
                        "outputs": ["Responses"],
                        "dependencies": []
                    }
                ],
                "data_flows": [],
                "constraints": ["Blueprint generation failed - retry required"],
                "risks": ["Incomplete architecture"]
            }
    
    @classmethod
    def generate_blueprint(
        cls,
        system_description: str,
        requirements: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        tech_stack: Optional[List[str]] = None,
        scale: Optional[str] = None,
        model: Optional[str] = None
    ) -> dict:
        """Synchronous wrapper for blueprint generation."""
        return asyncio.run(cls.generate_blueprint_async(
            system_description, requirements, constraints,
            tech_stack, scale, model
        ))
    
    @classmethod
    async def blueprint_from_strategy_async(cls, strategy: dict) -> dict:
        """
        Generate blueprint from a Strategy Engine output.
        
        Args:
            strategy: Output from Strategy Engine
            
        Returns:
            Blueprint as dict
        """
        summary = strategy.get("summary", "")
        steps = strategy.get("steps", [])
        
        description = f"System to implement strategy: {summary}"
        requirements = steps[:5] if steps else None
        
        return await cls.generate_blueprint_async(
            system_description=description,
            requirements=requirements
        )
    
    @classmethod
    async def saas_blueprint_async(
        cls,
        product_name: str,
        core_features: List[str],
        user_types: Optional[List[str]] = None
    ) -> dict:
        """
        Generate SaaS product blueprint.
        
        Args:
            product_name: Name of the SaaS product
            core_features: Core features to include
            user_types: Types of users
            
        Returns:
            Blueprint as dict
        """
        description = f"SaaS product: {product_name}"
        requirements = [f"Feature: {f}" for f in core_features]
        
        if user_types:
            requirements.append(f"User types: {', '.join(user_types)}")
        
        constraints = [
            "Multi-tenant architecture",
            "Subscription-based access control",
            "Scalable infrastructure"
        ]
        
        return await cls.generate_blueprint_async(
            system_description=description,
            requirements=requirements,
            constraints=constraints
        )
    
    @classmethod
    async def api_blueprint_async(
        cls,
        api_name: str,
        endpoints: List[str],
        expected_load: Optional[str] = None
    ) -> dict:
        """
        Generate API system blueprint.
        
        Args:
            api_name: Name of the API
            endpoints: Key endpoints/operations
            expected_load: Expected request volume
            
        Returns:
            Blueprint as dict
        """
        description = f"API system: {api_name}"
        requirements = [f"Endpoint: {e}" for e in endpoints]
        
        constraints = [
            "RESTful design principles",
            "Authentication/authorization",
            "Rate limiting",
            "API versioning"
        ]
        
        return await cls.generate_blueprint_async(
            system_description=description,
            requirements=requirements,
            constraints=constraints,
            scale=expected_load
        )
    
    @classmethod
    async def microservices_blueprint_async(
        cls,
        system_name: str,
        domains: List[str],
        shared_concerns: Optional[List[str]] = None
    ) -> dict:
        """
        Generate microservices architecture blueprint.
        
        Args:
            system_name: Name of the system
            domains: Business domains to model as services
            shared_concerns: Cross-cutting concerns
            
        Returns:
            Blueprint as dict
        """
        description = f"Microservices architecture for: {system_name}"
        requirements = [f"Domain service: {d}" for d in domains]
        
        constraints = [
            "Service independence",
            "API-first communication",
            "Event-driven where appropriate",
            "Centralized logging and monitoring"
        ]
        
        if shared_concerns:
            constraints.extend(shared_concerns)
        
        return await cls.generate_blueprint_async(
            system_description=description,
            requirements=requirements,
            constraints=constraints
        )
    
    @classmethod
    def get_component_types(cls) -> dict:
        """Get available component types."""
        return cls.COMPONENT_TYPES
