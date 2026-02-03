from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import deque
from datetime import datetime, timezone
import json
import statistics

@dataclass
class DriftMetrics:
    """Metrics for a single response."""
    response_length: int
    json_valid: bool
    canon_compliant: bool
    field_count: int
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class DriftReport:
    """Drift analysis report."""
    token_count: int
    json_valid: bool
    canon_compliance: str  # "pass", "warn", "fail"
    issues: List[str]
    recommendation: Optional[str] = None

class DriftMonitor:
    """Monitors model responses for behavioral drift."""
    
    # In-memory storage for metrics history
    _history: Dict[str, deque] = {
        "gpt-5.2": deque(maxlen=100),
        "claude-sonnet-4.5": deque(maxlen=100),
        "gemini-3-flash": deque(maxlen=100),
        "all": deque(maxlen=100)
    }
    
    # Baseline metrics
    BASELINES = {
        "response_length_avg": 800,
        "json_valid_rate": 0.95,
        "canon_compliance_rate": 0.95,
        "field_count_expected": 5
    }
    
    # Thresholds
    THRESHOLDS = {
        "warning": 0.15,
        "critical": 0.30
    }
    
    @classmethod
    def check(cls, output: dict, model: str = "all") -> DriftReport:
        """Check output for drift and record metrics."""
        issues = []
        
        # Calculate metrics
        response_str = json.dumps(output)
        token_count = len(response_str)
        
        # JSON validity check
        json_valid = isinstance(output, dict)
        
        # Field validation
        required_fields = ["summary", "steps", "risks", "resources", "next_action"]
        missing_fields = [f for f in required_fields if f not in output]
        
        if missing_fields:
            issues.append(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Type validation
        if "steps" in output and not isinstance(output["steps"], list):
            issues.append("'steps' should be a list")
        if "risks" in output and not isinstance(output["risks"], list):
            issues.append("'risks' should be a list")
        if "resources" in output and not isinstance(output["resources"], list):
            issues.append("'resources' should be a list")
        
        # Length checks
        if "summary" in output and len(output["summary"]) < 50:
            issues.append("Summary is too short (< 50 chars)")
        if "steps" in output and len(output.get("steps", [])) < 3:
            issues.append("Fewer than 3 steps provided")
        if "next_action" in output and len(output.get("next_action", "")) < 20:
            issues.append("Next action is too vague (< 20 chars)")
        
        # Content quality checks
        if "steps" in output:
            for i, step in enumerate(output["steps"]):
                if isinstance(step, str) and len(step) < 10:
                    issues.append(f"Step {i+1} is too short")
        
        # Determine compliance level
        if len(issues) == 0:
            canon_compliance = "pass"
        elif len(issues) <= 2:
            canon_compliance = "warn"
        else:
            canon_compliance = "fail"
        
        # Generate recommendation
        recommendation = None
        if canon_compliance == "fail":
            recommendation = "Response quality below threshold — consider model recalibration or prompt refinement"
        elif canon_compliance == "warn":
            recommendation = "Minor issues detected — monitor for patterns"
        
        # Record metrics
        metrics = DriftMetrics(
            response_length=token_count,
            json_valid=json_valid,
            canon_compliant=(canon_compliance == "pass"),
            field_count=len([f for f in required_fields if f in output])
        )
        cls._history[model].append(metrics)
        cls._history["all"].append(metrics)
        
        return DriftReport(
            token_count=token_count,
            json_valid=json_valid,
            canon_compliance=canon_compliance,
            issues=issues,
            recommendation=recommendation
        )
    
    @classmethod
    def get_drift_report(cls, model: str = "all") -> dict:
        """Get drift analysis for a model."""
        history = list(cls._history.get(model, []))
        
        if len(history) < 5:
            return {
                "status": "insufficient_data",
                "sample_count": len(history),
                "message": "Need at least 5 samples for drift analysis"
            }
        
        # Calculate current metrics
        avg_length = statistics.mean(m.response_length for m in history)
        json_valid_rate = sum(1 for m in history if m.json_valid) / len(history)
        canon_rate = sum(1 for m in history if m.canon_compliant) / len(history)
        
        # Calculate deviations from baseline
        length_deviation = abs(avg_length - cls.BASELINES["response_length_avg"]) / cls.BASELINES["response_length_avg"]
        json_deviation = abs(json_valid_rate - cls.BASELINES["json_valid_rate"])
        canon_deviation = abs(canon_rate - cls.BASELINES["canon_compliance_rate"])
        
        max_deviation = max(length_deviation, json_deviation, canon_deviation)
        
        status = "normal"
        if max_deviation > cls.THRESHOLDS["critical"]:
            status = "critical"
        elif max_deviation > cls.THRESHOLDS["warning"]:
            status = "warning"
        
        return {
            "status": status,
            "model": model,
            "sample_count": len(history),
            "metrics": {
                "avg_response_length": round(avg_length, 2),
                "json_valid_rate": round(json_valid_rate, 3),
                "canon_compliance_rate": round(canon_rate, 3)
            },
            "deviations": {
                "length": round(length_deviation, 3),
                "json_validity": round(json_deviation, 3),
                "canon_compliance": round(canon_deviation, 3)
            },
            "max_deviation": round(max_deviation, 3)
        }
    
    @classmethod
    def reset(cls, model: str = None):
        """Reset metrics history."""
        if model:
            if model in cls._history:
                cls._history[model].clear()
        else:
            for key in cls._history:
                cls._history[key].clear()
