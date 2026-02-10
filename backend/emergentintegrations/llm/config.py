"""
LLM Configuration
Centralized configuration for LLM providers and API keys.
"""

import os
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class ModelProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GEMINI = "gemini"  # Alias for Google


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    provider: ModelProvider
    model_id: str
    display_name: str
    max_tokens: int = 4096
    default_temperature: float = 0.7
    supports_system: bool = True
    supports_streaming: bool = True


# Model Registry - Maps friendly names to actual model configs
MODEL_REGISTRY: Dict[str, ModelConfig] = {
    # OpenAI Models
    "gpt-5.2": ModelConfig(
        provider=ModelProvider.OPENAI,
        model_id="gpt-4o",
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
    "gpt-4-turbo": ModelConfig(
        provider=ModelProvider.OPENAI,
        model_id="gpt-4-turbo",
        display_name="GPT-4 Turbo",
        max_tokens=4096,
    ),
    "gpt-4": ModelConfig(
        provider=ModelProvider.OPENAI,
        model_id="gpt-4",
        display_name="GPT-4",
        max_tokens=4096,
    ),
    "gpt-3.5-turbo": ModelConfig(
        provider=ModelProvider.OPENAI,
        model_id="gpt-3.5-turbo",
        display_name="GPT-3.5 Turbo",
        max_tokens=4096,
    ),
    
    # Anthropic Models
    "claude-sonnet-4.5": ModelConfig(
        provider=ModelProvider.ANTHROPIC,
        model_id="claude-sonnet-4-5-20250929",
        display_name="Claude Sonnet 4.5",
        max_tokens=4096,
    ),
    "claude-sonnet-4-5-20250929": ModelConfig(
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
    "claude-3-5-sonnet-20241022": ModelConfig(
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
    "claude-3-opus-20240229": ModelConfig(
        provider=ModelProvider.ANTHROPIC,
        model_id="claude-3-opus-20240229",
        display_name="Claude 3 Opus",
        max_tokens=4096,
    ),
    "claude-3-haiku": ModelConfig(
        provider=ModelProvider.ANTHROPIC,
        model_id="claude-3-haiku-20240307",
        display_name="Claude 3 Haiku",
        max_tokens=4096,
    ),
    
    # Google/Gemini Models
    "gemini-3-flash": ModelConfig(
        provider=ModelProvider.GOOGLE,
        model_id="gemini-2.0-flash",
        display_name="Gemini 3 Flash",
        max_tokens=4096,
    ),
    "gemini-3-flash-preview": ModelConfig(
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
    "gemini-1.5-flash": ModelConfig(
        provider=ModelProvider.GOOGLE,
        model_id="gemini-1.5-flash",
        display_name="Gemini 1.5 Flash",
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
        ModelProvider.GEMINI: "GOOGLE_API_KEY",
    }
    
    # Fallback universal key
    EMERGENT_KEY_ENV = "EMERGENT_LLM_KEY"
    
    # API Endpoints
    ENDPOINTS = {
        ModelProvider.OPENAI: "https://api.openai.com/v1/chat/completions",
        ModelProvider.ANTHROPIC: "https://api.anthropic.com/v1/messages",
        ModelProvider.GOOGLE: "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        ModelProvider.GEMINI: "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    }
    
    @classmethod
    def get_api_key(cls, provider: ModelProvider) -> Optional[str]:
        """
        Get API key for a provider.
        Checks provider-specific key first, then falls back to EMERGENT_LLM_KEY.
        """
        # Normalize gemini to google
        if provider == ModelProvider.GEMINI:
            provider = ModelProvider.GOOGLE
        
        # Try provider-specific key
        env_key = cls.ENV_KEYS.get(provider)
        if env_key:
            key = os.environ.get(env_key)
            if key:
                return key
        
        # Fall back to Emergent universal key
        return os.environ.get(cls.EMERGENT_KEY_ENV)
    
    @classmethod
    def get_endpoint(cls, provider: ModelProvider, model: str = None) -> str:
        """Get API endpoint for a provider."""
        if provider == ModelProvider.GEMINI:
            provider = ModelProvider.GOOGLE
        
        endpoint = cls.ENDPOINTS.get(provider, "")
        if "{model}" in endpoint and model:
            endpoint = endpoint.format(model=model)
        return endpoint
    
    @classmethod
    def get_model_config(cls, model_name: str) -> Optional[ModelConfig]:
        """Get configuration for a model by name."""
        return MODEL_REGISTRY.get(model_name)
    
    @classmethod
    def resolve_model(cls, provider: str, model: str) -> Tuple[ModelProvider, str]:
        """
        Resolve provider string and model name to actual values.
        
        Args:
            provider: Provider name ("openai", "anthropic", "google", "gemini")
            model: Model name or alias
            
        Returns:
            Tuple of (ModelProvider, actual_model_id)
        """
        # Normalize provider
        provider_lower = provider.lower()
        if provider_lower in ("openai",):
            prov = ModelProvider.OPENAI
        elif provider_lower in ("anthropic", "claude"):
            prov = ModelProvider.ANTHROPIC
        elif provider_lower in ("google", "gemini"):
            prov = ModelProvider.GOOGLE
        else:
            prov = ModelProvider.OPENAI
        
        # Check if model is in registry
        config = MODEL_REGISTRY.get(model)
        if config:
            return config.provider, config.model_id
        
        # Return as-is
        return prov, model
    
    @classmethod
    def is_provider_configured(cls, provider: ModelProvider) -> bool:
        """Check if a provider has an API key configured."""
        return cls.get_api_key(provider) is not None
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, bool]:
        """Get availability status of all providers."""
        return {
            "openai": cls.is_provider_configured(ModelProvider.OPENAI),
            "anthropic": cls.is_provider_configured(ModelProvider.ANTHROPIC),
            "google": cls.is_provider_configured(ModelProvider.GOOGLE),
        }
    
    @classmethod
    def get_default_model(cls) -> Tuple[str, str]:
        """
        Get default model based on available providers.
        Returns (provider, model) tuple.
        """
        # Priority: OpenAI > Anthropic > Google
        if cls.is_provider_configured(ModelProvider.OPENAI):
            return ("openai", "gpt-4o")
        elif cls.is_provider_configured(ModelProvider.ANTHROPIC):
            return ("anthropic", "claude-3-5-sonnet-20241022")
        elif cls.is_provider_configured(ModelProvider.GOOGLE):
            return ("google", "gemini-2.0-flash")
        else:
            return ("openai", "gpt-4o")  # Default even if not configured
