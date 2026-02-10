"""
LLM Configuration
Centralized configuration for LLM providers and API keys.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    provider: ModelProvider
    model_id: str
    display_name: str
    max_tokens: int = 4096
    default_temperature: float = 0.7


# Model Registry - Maps friendly names to actual model configs
MODEL_REGISTRY: Dict[str, ModelConfig] = {
    # OpenAI Models
    "gpt-5.2": ModelConfig(
        provider=ModelProvider.OPENAI,
        model_id="gpt-4o",  # Use latest available
        display_name="GPT-5.2",
        max_tokens=4096,
    ),
    "gpt-4o": ModelConfig(
        provider=ModelProvider.OPENAI,
        model_id="gpt-4o",
        display_name="GPT-4o",
        max_tokens=4096,
    ),
    "gpt-4o-mini": ModelConfig(
        provider=ModelProvider.OPENAI,
        model_id="gpt-4o-mini",
        display_name="GPT-4o Mini",
        max_tokens=4096,
    ),
    
    # Anthropic Models
    "claude-sonnet-4.5": ModelConfig(
        provider=ModelProvider.ANTHROPIC,
        model_id="claude-sonnet-4-5-20250929",
        display_name="Claude Sonnet 4.5",
        max_tokens=4096,
    ),
    "claude-3-5-sonnet": ModelConfig(
        provider=ModelProvider.ANTHROPIC,
        model_id="claude-3-5-sonnet-20241022",
        display_name="Claude 3.5 Sonnet",
        max_tokens=4096,
    ),
    "claude-3-opus": ModelConfig(
        provider=ModelProvider.ANTHROPIC,
        model_id="claude-3-opus-20240229",
        display_name="Claude 3 Opus",
        max_tokens=4096,
    ),
    
    # Google Models
    "gemini-3-flash": ModelConfig(
        provider=ModelProvider.GOOGLE,
        model_id="gemini-2.0-flash",
        display_name="Gemini 3 Flash",
        max_tokens=4096,
    ),
    "gemini-2.0-flash": ModelConfig(
        provider=ModelProvider.GOOGLE,
        model_id="gemini-2.0-flash",
        display_name="Gemini 2.0 Flash",
        max_tokens=4096,
    ),
    "gemini-1.5-pro": ModelConfig(
        provider=ModelProvider.GOOGLE,
        model_id="gemini-1.5-pro",
        display_name="Gemini 1.5 Pro",
        max_tokens=4096,
    ),
}


class LLMConfig:
    """
    Centralized LLM configuration manager.
    Reads API keys from environment variables.
    """
    
    # Environment variable names for API keys
    ENV_KEYS = {
        ModelProvider.OPENAI: "OPENAI_API_KEY",
        ModelProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
        ModelProvider.GOOGLE: "GOOGLE_API_KEY",
    }
    
    # Fallback to Emergent key if individual keys not set
    EMERGENT_KEY_ENV = "EMERGENT_LLM_KEY"
    
    @classmethod
    def get_api_key(cls, provider: ModelProvider) -> Optional[str]:
        """
        Get API key for a provider.
        Falls back to EMERGENT_LLM_KEY if provider-specific key not set.
        """
        # First try provider-specific key
        key = os.environ.get(cls.ENV_KEYS.get(provider, ""))
        if key:
            return key
        
        # Fall back to Emergent universal key
        return os.environ.get(cls.EMERGENT_KEY_ENV)
    
    @classmethod
    def get_model_config(cls, model_name: str) -> Optional[ModelConfig]:
        """Get configuration for a model by name."""
        return MODEL_REGISTRY.get(model_name)
    
    @classmethod
    def is_provider_configured(cls, provider: ModelProvider) -> bool:
        """Check if a provider has an API key configured."""
        return cls.get_api_key(provider) is not None
    
    @classmethod
    def get_available_models(cls) -> Dict[str, ModelConfig]:
        """Get all models that have their provider configured."""
        available = {}
        for name, config in MODEL_REGISTRY.items():
            if cls.is_provider_configured(config.provider):
                available[name] = config
        return available
    
    @classmethod
    def get_default_model(cls) -> str:
        """Get the default model based on available providers."""
        # Priority: OpenAI > Anthropic > Google
        priority = [
            ("gpt-4o", ModelProvider.OPENAI),
            ("claude-sonnet-4.5", ModelProvider.ANTHROPIC),
            ("gemini-2.0-flash", ModelProvider.GOOGLE),
        ]
        
        for model_name, provider in priority:
            if cls.is_provider_configured(provider):
                return model_name
        
        # Fallback
        return "gpt-4o"
    
    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """Get configuration status for all providers."""
        return {
            "openai": {
                "configured": cls.is_provider_configured(ModelProvider.OPENAI),
                "models": ["gpt-5.2", "gpt-4o", "gpt-4o-mini"],
            },
            "anthropic": {
                "configured": cls.is_provider_configured(ModelProvider.ANTHROPIC),
                "models": ["claude-sonnet-4.5", "claude-3-5-sonnet", "claude-3-opus"],
            },
            "google": {
                "configured": cls.is_provider_configured(ModelProvider.GOOGLE),
                "models": ["gemini-3-flash", "gemini-2.0-flash", "gemini-1.5-pro"],
            },
            "default_model": cls.get_default_model(),
            "emergent_key_set": os.environ.get(cls.EMERGENT_KEY_ENV) is not None,
        }
