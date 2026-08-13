"""SLA113 Configuration"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    APP_NAME: str = "SLA113 — Universal AI Game Studio Operator OS"
    DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"
    MONGO_URL: str = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    DB_NAME: str = os.environ.get("DB_NAME", "sla113_standalone")
    CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS", "*")
    EMERGENT_LLM_KEY: str = os.environ.get("EMERGENT_LLM_KEY", "")
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")

    # ─── White-Label Platform ───
    PLATFORM_DOMAIN: str = os.environ.get("PLATFORM_DOMAIN", "sla113.example.com")
    MASTER_API_KEY: str = os.environ.get("MASTER_API_KEY", "")
    TENANT_CACHE_TTL: int = int(os.environ.get("TENANT_CACHE_TTL", "60"))

    # ─── Stripe (tenant billing) ───
    STRIPE_SECRET_KEY: str = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
