"""
SLA113 — Universal AI Game Studio Operator OS
==============================================
Sovereign FastAPI entrypoint. All universes are routers/modules under SLA113.

Architecture:
  SLA113 (Sovereign Root)
  ├── sla113_admin         — Tenant Management (White Label Mint)
  ├── sla113_billing       — Revenue Pipelines
  ├── sla113_dashboard_context — Stats, Game Types, Projects CRUD
  ├── sla113_engine_dashboard  — Vision, Logic, Composer, Terminal
  ├── sla113_factory       — Build Pipeline
  ├── sla113_foundry       — Vision Smith Image Generation (Gemini 3 Pro)
  ├── sla113_health        — System Status
  ├── sla113_orchestration — Night Queue Worker, Jobs, Dependencies
  ├── sla113_regulatory    — Compliance Engine
  ├── sla113/factory       — Deploy Engine
  ├── empire1              — Empire1 Universe (stub)
  ├── southern             — SouthernLifestyle Game OS (stub)
  └── soulfire             — Soulfire Ecosystem / Lyrica 3 Pro (stub)
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import get_settings
from app.core.database import connect_to_database, close_database_connection

# ─── SLA113 Core Routers ───
from app.routers.sla113_admin import router as sla113_admin_router
from app.routers.sla113_billing import router as sla113_billing_router, seed_default_pipelines
from app.routers.sla113_dashboard_context import router as sla113_dashboard_context_router
from app.routers.sla113_engine_dashboard import router as sla113_engine_dashboard_router
from app.routers.sla113_factory import router as sla113_factory_router
from app.routers.sla113_foundry import router as sla113_foundry_router
from app.routers.sla113_health import router as sla113_health_router
from app.routers.sla113_orchestration import router as sla113_orchestration_router, start_worker, stop_worker
from app.routers.sla113_regulatory import router as sla113_regulatory_router
from app.routers.sla113.factory import router as sla113_deploy_router
from app.routers.sla113_universe import router as sla113_universe_router

# ─── Universe Routers ───
from app.routers.empire1 import router as empire1_router
from app.routers.southern import router as southern_router
from app.routers.soulfire import router as soulfire_router

# ─── AI Engine Routers ───
from app.routers.hybrid_ai import router as hybrid_ai_router
from app.routers.omni_agent import router as omni_agent_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    await connect_to_database()
    await seed_default_pipelines()
    start_worker()
    logger.info("SLA113 Operator OS — All systems online.")
    yield
    stop_worker()
    await close_database_connection()
    logger.info("SLA113 Operator OS — Shutdown complete.")


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Universal AI Game Studio Operator OS — Sovereign Platform",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# ─── CORS ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── SLA113 Core ───
app.include_router(sla113_admin_router)
app.include_router(sla113_billing_router)
app.include_router(sla113_dashboard_context_router)
app.include_router(sla113_engine_dashboard_router)
app.include_router(sla113_factory_router)
app.include_router(sla113_foundry_router)
app.include_router(sla113_health_router)
app.include_router(sla113_orchestration_router)
app.include_router(sla113_regulatory_router)
app.include_router(sla113_deploy_router)
app.include_router(sla113_universe_router)

# ─── Universes ───
app.include_router(empire1_router)
app.include_router(southern_router)
app.include_router(soulfire_router)

# ─── AI Engines ───
app.include_router(hybrid_ai_router)
app.include_router(omni_agent_router)

# ─── Root Health ───
@app.get("/")
async def root():
    return {"status": "online", "app": settings.APP_NAME, "version": "1.0.0"}
