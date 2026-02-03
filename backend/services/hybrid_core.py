"""
Hybrid Intelligence Core

The master orchestrator that coordinates, executes, and maintains
the multi-model AI pipeline composed of specialized engines.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime, timezone
import asyncio

from services.router import RoutingEngine
from services.strategy_engine import StrategyEngine
from services.plan_builder import PlanBuilderEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage, ErrorType


class TaskType(Enum):
    """Task classification for routing."""
    STRATEGY = "strategy"
    PLAN = "plan"
    ANALYSIS = "analysis"
    CODE = "code"
    QUICK = "quick"
    GENERAL = "general"


class PipelineResult(BaseModel):
    """Standardized pipeline execution result."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class HybridIntelligenceCore:
    """
    Master orchestrator for the multi-model AI pipeline.
    
    Coordinates:
    1. Routing Engine - classifies tasks and selects optimal model
    2. Strategy Engine - generates structured strategies
    3. Plan Builder Engine - converts goals to execution plans
    4. Analysis Engine - performs deep analysis (via routing)
    5. Canon Enforcer - normalizes tone and structure
    6. Drift Monitor - tracks behavioral drift
    7. Error Handler - structured error responses
    """
    
    # Task type to engine mapping
    ENGINE_MAP = {
        TaskType.STRATEGY: "strategy_engine",
        TaskType.PLAN: "plan_builder_engine",
        TaskType.ANALYSIS: "strategy_engine",  # Uses strategy with analysis prompt
        TaskType.CODE: "strategy_engine",  # Routes to GPT via routing engine
        TaskType.QUICK: "strategy_engine",  # Routes to Gemini via routing engine
        TaskType.GENERAL: "strategy_engine"
    }
    
    # Task classification keywords
    TASK_PATTERNS = {
        TaskType.STRATEGY: ["strategy", "plan", "business", "monetize", "grow", "scale", "launch"],
        TaskType.PLAN: ["execution", "timeline", "milestones", "phases", "schedule", "roadmap"],
        TaskType.ANALYSIS: ["analyze", "evaluate", "assess", "review", "diagnose", "investigate"],
        TaskType.CODE: ["code", "function", "debug", "api", "build", "implement", "program"],
        TaskType.QUICK: ["what is", "define", "quick", "simple", "list", "summarize"]
    }
    
    def __init__(self):
        self.execution_log: List[Dict] = []
    
    def classify_task(self, prompt: str) -> TaskType:
        """Classify task type from prompt."""
        prompt_lower = prompt.lower()
        
        # Check for plan-specific keywords first (more specific)
        for keyword in self.TASK_PATTERNS[TaskType.PLAN]:
            if keyword in prompt_lower:
                return TaskType.PLAN
        
        # Check other patterns
        for task_type, keywords in self.TASK_PATTERNS.items():
            if task_type == TaskType.PLAN:
                continue
            for keyword in keywords:
                if keyword in prompt_lower:
                    return task_type
        
        return TaskType.GENERAL
    
    async def execute(
        self,
        prompt: str,
        task_type: Optional[TaskType] = None,
        context: Optional[str] = None,
        force_model: Optional[str] = None
    ) -> PipelineResult:
        """
        Execute the full hybrid pipeline.
        
        Pipeline Order:
        1. Task Classification (if not specified)
        2. Routing Engine
        3. Engine Execution (Strategy/Plan/Analysis)
        4. Canon Enforcer
        5. Drift Monitor
        6. Return Result (or Error Handler on failure)
        """
        start_time = datetime.now(timezone.utc)
        current_stage = PipelineStage.ROUTING
        
        try:
            # Stage 1: Task Classification
            if task_type is None:
                task_type = self.classify_task(prompt)
            
            # Stage 2: Routing
            current_stage = PipelineStage.ROUTING
            routing_decision = RoutingEngine.route(prompt, force_model)
            selected_model = routing_decision.model
            
            # Stage 3: Engine Execution
            current_stage = PipelineStage.STRATEGY
            
            if task_type == TaskType.PLAN:
                raw_output = await PlanBuilderEngine.build_plan_async(
                    goal=prompt,
                    context=context,
                    model=selected_model
                )
            else:
                raw_output = await StrategyEngine.generate_async(
                    model=selected_model,
                    goal=prompt,
                    context=context,
                    tone="direct"
                )
            
            # Stage 4: Canon Enforcement
            current_stage = PipelineStage.CANON
            cleaned_output = CanonEnforcer.normalize(raw_output)
            canon_validation = CanonEnforcer.validate(cleaned_output)
            
            # Stage 5: Drift Monitoring
            current_stage = PipelineStage.DRIFT
            drift_report = DriftMonitor.check(cleaned_output, selected_model)
            
            # Build metadata
            end_time = datetime.now(timezone.utc)
            metadata = {
                "task_type": task_type.value,
                "model_used": selected_model,
                "routing_reason": routing_decision.reason,
                "canon_compliant": canon_validation["is_compliant"],
                "drift_status": drift_report.canon_compliance,
                "latency_ms": int((end_time - start_time).total_seconds() * 1000),
                "timestamp": end_time.isoformat()
            }
            
            # Log execution
            self._log_execution(prompt, task_type, metadata, success=True)
            
            return PipelineResult(
                success=True,
                data=cleaned_output,
                metadata=metadata
            )
        
        except Exception as e:
            # Error Handler
            error_response = ErrorHandler.handle(e, current_stage)
            
            self._log_execution(prompt, task_type, {"error": str(e)}, success=False)
            
            return PipelineResult(
                success=False,
                error=error_response.model_dump()
            )
    
    async def execute_strategy(
        self,
        goal: str,
        context: Optional[str] = None,
        force_model: Optional[str] = None
    ) -> PipelineResult:
        """Execute strategy generation pipeline."""
        return await self.execute(
            prompt=goal,
            task_type=TaskType.STRATEGY,
            context=context,
            force_model=force_model
        )
    
    async def execute_plan(
        self,
        goal: str,
        strategy: Optional[Dict] = None,
        context: Optional[str] = None,
        force_model: Optional[str] = None
    ) -> PipelineResult:
        """Execute plan building pipeline."""
        # If strategy provided, include it in context
        if strategy:
            import json
            strategy_context = f"Strategy to execute:\n{json.dumps(strategy, indent=2)}"
            if context:
                context = f"{context}\n\n{strategy_context}"
            else:
                context = strategy_context
        
        return await self.execute(
            prompt=goal,
            task_type=TaskType.PLAN,
            context=context,
            force_model=force_model
        )
    
    async def execute_strategy_to_plan(
        self,
        goal: str,
        context: Optional[str] = None,
        force_model: Optional[str] = None
    ) -> PipelineResult:
        """Execute full strategy → plan pipeline."""
        # First generate strategy
        strategy_result = await self.execute_strategy(goal, context, force_model)
        
        if not strategy_result.success:
            return strategy_result
        
        # Then convert to plan
        return await self.execute_plan(
            goal=strategy_result.data.get("summary", goal),
            strategy=strategy_result.data,
            force_model=force_model
        )
    
    async def execute_analysis(
        self,
        subject: str,
        context: Optional[str] = None
    ) -> PipelineResult:
        """Execute analysis pipeline (routes to Claude)."""
        analysis_prompt = f"Analyze the following: {subject}"
        return await self.execute(
            prompt=analysis_prompt,
            task_type=TaskType.ANALYSIS,
            context=context,
            force_model="claude-sonnet-4.5"  # Force Claude for analysis
        )
    
    def get_execution_log(self, limit: int = 100) -> List[Dict]:
        """Get recent execution log entries."""
        return self.execution_log[-limit:]
    
    def get_system_status(self) -> Dict:
        """Get current system status."""
        return {
            "status": "operational",
            "core": "hybrid_intelligence_core",
            "engines": {
                "routing_engine": "active",
                "strategy_engine": "active",
                "plan_builder_engine": "active",
                "canon_enforcer": "active",
                "drift_monitor": "active",
                "error_handler": "active"
            },
            "models": {
                "gpt-5.2": "available",
                "claude-sonnet-4.5": "available",
                "gemini-3-flash": "available"
            },
            "drift_report": DriftMonitor.get_drift_report("all"),
            "executions_logged": len(self.execution_log)
        }
    
    def _log_execution(
        self,
        prompt: str,
        task_type: Optional[TaskType],
        metadata: Dict,
        success: bool
    ):
        """Log execution for monitoring."""
        self.execution_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "task_type": task_type.value if task_type else "unknown",
            "success": success,
            "metadata": metadata
        })
        
        # Keep log bounded
        if len(self.execution_log) > 1000:
            self.execution_log = self.execution_log[-500:]


# Singleton instance
_core_instance: Optional[HybridIntelligenceCore] = None

def get_core() -> HybridIntelligenceCore:
    """Get or create the singleton Hybrid Intelligence Core instance."""
    global _core_instance
    if _core_instance is None:
        _core_instance = HybridIntelligenceCore()
    return _core_instance
