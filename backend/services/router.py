from pydantic import BaseModel
import re
from enum import Enum

class TaskCategory(Enum):
    CODE = "code"
    ANALYSIS = "analysis"
    QUICK = "quick"
    STRATEGY = "strategy"
    GENERAL = "general"

class RoutingDecision(BaseModel):
    model: str
    reason: str

class RoutingEngine:
    """Routes requests to optimal model based on task analysis."""
    
    PATTERNS = {
        TaskCategory.CODE: [
            r"\bcode\b", r"\bfunction\b", r"\bclass\b", r"\bapi\b",
            r"\bdebug\b", r"\bfix\b", r"\brefactor\b", r"\bpython\b",
            r"\bjavascript\b", r"\bsql\b", r"\bprogram\b", r"\bbuild\b"
        ],
        TaskCategory.ANALYSIS: [
            r"\banalyze\b", r"\breview\b", r"\bcompare\b",
            r"\bevaluate\b", r"\bassess\b", r"\binterpret\b"
        ],
        TaskCategory.STRATEGY: [
            r"\bstrategy\b", r"\bmonetize\b", r"\bplan\b", r"\bgrow\b",
            r"\bscale\b", r"\blaunch\b", r"\bmarket\b", r"\bbusiness\b"
        ],
        TaskCategory.QUICK: [
            r"\bquick\b", r"\bsimple\b", r"\bwhat is\b", r"\bdefine\b",
            r"\btranslate\b", r"\bconvert\b", r"\blist\b", r"\bsummarize\b"
        ]
    }
    
    CATEGORY_MODEL_MAP = {
        TaskCategory.CODE: "gpt-5.2",
        TaskCategory.ANALYSIS: "claude-sonnet-4.5",
        TaskCategory.STRATEGY: "claude-sonnet-4.5",
        TaskCategory.QUICK: "gemini-3-flash",
        TaskCategory.GENERAL: "gpt-5.2"
    }
    
    CATEGORY_REASONS = {
        TaskCategory.CODE: "Complex reasoning and code generation task — routed to GPT-5.2",
        TaskCategory.ANALYSIS: "Analysis and structured thinking task — routed to Claude",
        TaskCategory.STRATEGY: "Strategy and planning task — routed to Claude",
        TaskCategory.QUICK: "Fast, simple task — routed to Gemini Flash",
        TaskCategory.GENERAL: "General task — routed to GPT-5.2 as default"
    }
    
    @classmethod
    def _compile_patterns(cls):
        return {
            category: [re.compile(p, re.IGNORECASE) for p in patterns]
            for category, patterns in cls.PATTERNS.items()
        }
    
    @classmethod
    def _classify_task(cls, prompt: str) -> TaskCategory:
        compiled = cls._compile_patterns()
        scores = {category: 0 for category in TaskCategory}
        
        for category, patterns in compiled.items():
            for pattern in patterns:
                if pattern.search(prompt):
                    scores[category] += 1
        
        max_category = max(scores, key=scores.get)
        
        if scores[max_category] == 0:
            return TaskCategory.GENERAL
        
        return max_category
    
    @classmethod
    def route(cls, goal: str, force_model: str = None) -> RoutingDecision:
        if force_model:
            return RoutingDecision(
                model=force_model,
                reason=f"Model override specified — using {force_model}"
            )
        
        category = cls._classify_task(goal)
        model = cls.CATEGORY_MODEL_MAP[category]
        reason = cls.CATEGORY_REASONS[category]
        
        return RoutingDecision(model=model, reason=reason)
