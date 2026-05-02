import re
from typing import Any

class CanonEnforcer:
    """Normalizes model outputs to match Strategy Engine canon."""
    
    FORBIDDEN_PHRASES = [
        "As an AI",
        "As a language model",
        "I'm Claude",
        "I'm GPT",
        "I'm Gemini",
        "my training data",
        "my knowledge cutoff",
        "Certainly!",
        "Sure!",
        "I'd be happy to",
        "Great question!",
        "That's a great question",
        "I cannot",
        "I'm sorry, but",
        "I apologize",
        "As an assistant",
        "I don't have access",
        "Based on my training"
    ]
    
    REPLACEMENT_MAP = {
        "As an AI": "",
        "As a language model": "",
        "my training data": "available information",
        "my knowledge cutoff": "the information available",
        "Certainly!": "",
        "Sure!": "",
        "I'd be happy to": "",
        "Great question!": "",
        "That's a great question": "",
        "I'm sorry, but": "",
        "I apologize": ""
    }
    
    @classmethod
    def _clean_string(cls, text: str) -> str:
        """Remove forbidden phrases from a string."""
        if not isinstance(text, str):
            return text
        
        cleaned = text
        
        for phrase, replacement in cls.REPLACEMENT_MAP.items():
            cleaned = cleaned.replace(phrase, replacement)
            cleaned = cleaned.replace(phrase.lower(), replacement)
        
        # Clean up double spaces
        while "  " in cleaned:
            cleaned = cleaned.replace("  ", " ")
        
        # Clean up leading/trailing whitespace
        cleaned = cleaned.strip()
        
        # Capitalize first letter if needed
        if cleaned and cleaned[0].islower():
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        return cleaned
    
    @classmethod
    def _clean_list(cls, items: list) -> list:
        """Clean each item in a list."""
        return [cls._clean_string(item) if isinstance(item, str) else item for item in items]
    
    @classmethod
    def normalize(cls, output: dict) -> dict:
        """Normalize the entire output to match canon."""
        if not isinstance(output, dict):
            return output
        
        normalized = {}
        
        for key, value in output.items():
            if isinstance(value, str):
                normalized[key] = cls._clean_string(value)
            elif isinstance(value, list):
                normalized[key] = cls._clean_list(value)
            else:
                normalized[key] = value
        
        # Ensure required fields exist
        required_fields = ["summary", "steps", "risks", "resources", "next_action"]
        for field in required_fields:
            if field not in normalized:
                if field in ["steps", "risks", "resources"]:
                    normalized[field] = []
                else:
                    normalized[field] = ""
        
        return normalized
    
    @classmethod
    def validate(cls, output: dict) -> dict:
        """Validate output against canon rules."""
        violations = []
        
        def check_string(text: str, field: str):
            if not isinstance(text, str):
                return
            for phrase in cls.FORBIDDEN_PHRASES:
                if phrase.lower() in text.lower():
                    violations.append({
                        "field": field,
                        "phrase": phrase,
                        "severity": "medium"
                    })
        
        for key, value in output.items():
            if isinstance(value, str):
                check_string(value, key)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, str):
                        check_string(item, f"{key}[{i}]")
        
        return {
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "violation_count": len(violations)
        }
