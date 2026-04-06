"""
System Configuration and Utilities
Provides system-level configuration and helper functions.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Environment(Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class SystemConfig:
    """System configuration container."""
    environment: Environment
    debug: bool
    log_level: str
    
    @classmethod
    def from_env(cls) -> "SystemConfig":
        """Create config from environment variables."""
        env_str = os.environ.get("APP_ENV", "development").lower()
        
        if env_str == "production":
            env = Environment.PRODUCTION
        elif env_str == "staging":
            env = Environment.STAGING
        else:
            env = Environment.DEVELOPMENT
        
        return cls(
            environment=env,
            debug=os.environ.get("DEBUG", "false").lower() == "true",
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
        )


def get_env(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get environment variable with optional default.
    
    Args:
        key: Environment variable name
        default: Default value if not set
        required: Raise error if not set and no default
        
    Returns:
        Environment variable value
    """
    value = os.environ.get(key, default)
    if required and value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    return value


def get_bool_env(key: str, default: bool = False) -> bool:
    """Get boolean environment variable."""
    value = os.environ.get(key, str(default)).lower()
    return value in ("true", "1", "yes", "on")


def get_int_env(key: str, default: int = 0) -> int:
    """Get integer environment variable."""
    try:
        return int(os.environ.get(key, str(default)))
    except ValueError:
        return default


def get_system_info() -> Dict[str, Any]:
    """Get system information for diagnostics."""
    from ..llm.config import LLMConfig, ModelProvider
    
    return {
        "version": "1.0.0",
        "environment": os.environ.get("APP_ENV", "development"),
        "providers": LLMConfig.get_available_providers(),
        "default_model": LLMConfig.get_default_model(),
        "emergent_key_set": os.environ.get("EMERGENT_LLM_KEY") is not None,
    }


# Convenience exports
config = SystemConfig.from_env()
