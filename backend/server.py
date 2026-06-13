from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone

# Load environment variables first
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import database connection
from database import connect_to_database, close_database_connection, get_database
from routers.sla113 import seed_default_pipelines, seed_default_lobbies, start_worker, stop_worker
from routers.empire1 import router as empire1_router, seed_ecosystem

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to database
    await connect_to_database()
    logging.info("Database connected on startup")
    await seed_default_pipelines()
    await seed_default_lobbies()
    await seed_ecosystem()
    start_worker()
    logging.info("Night Queue Worker started")
    yield
    # Shutdown: Close database connection
    stop_worker()
    await close_database_connection()
    logging.info("Database connection closed on shutdown")

# Create the main app with lifespan
app = FastAPI(
    title="Hybrid AI Stack",
    description="Multi-model AI pipeline with GPT-5.2, Claude Sonnet 4.5, and Gemini 3 Flash",
    version="2.0.0",
    lifespan=lifespan,
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Import auth and team routers
from routers.auth import router as auth_router
from routers.teams import router as teams_router
from routers.profile import router as profile_router
from routers.invites import router as invites_router
from routers.billing import router as billing_router
from routers.api_keys import router as api_keys_router
from routers.admin import router as admin_router
from routers.system import router as system_router

# Import and include all engine routers
from routers.engines import (
    core_router,
    strategy_router,
    drift_router,
    plan_router,
    analysis_router,
    opportunity_router,
    evaluator_router,
    pricing_router,
    blueprint_router,
    persona_router,
    pipeline_router,
    anime_character_router,
    anime_lore_router,
    anime_story_router,
    art_direction_router,
    money_pipeline_router,
    analytics_router,
)
from routers.engines.history_protected import router as history_protected_router
from routers.pipelines import router as pipelines_router
from routers.sla113 import router as sla113_router

# Include auth and team routers first (higher priority)
api_router.include_router(auth_router)
api_router.include_router(teams_router)
api_router.include_router(profile_router)
api_router.include_router(invites_router)  # Public invite endpoints
api_router.include_router(billing_router)  # Billing endpoints
api_router.include_router(api_keys_router)  # API key management
api_router.include_router(admin_router)  # Admin endpoints (system admin only)
api_router.include_router(system_router)  # System status endpoints

# Include protected routers (require auth)
api_router.include_router(history_protected_router)  # /api/history (protected)
api_router.include_router(pipelines_router)  # /api/pipelines (protected)

# Include all engine routers (currently public for backward compatibility)
api_router.include_router(core_router)
api_router.include_router(strategy_router)
api_router.include_router(drift_router)
api_router.include_router(plan_router)
api_router.include_router(analysis_router)
api_router.include_router(opportunity_router)
api_router.include_router(evaluator_router)
api_router.include_router(pricing_router)
api_router.include_router(blueprint_router)
api_router.include_router(persona_router)
api_router.include_router(pipeline_router)
api_router.include_router(anime_character_router)
api_router.include_router(anime_lore_router)
api_router.include_router(anime_story_router)
api_router.include_router(art_direction_router)
api_router.include_router(money_pipeline_router)
api_router.include_router(analytics_router)  # Analytics remains public for now (system-wide metrics)
api_router.include_router(sla113_router)  # SLA113 - Universal AI Game Studio


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    db = get_database()
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    db = get_database()
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Include the router in the main app
app.include_router(api_router)
app.include_router(empire1_router)  # /api/empire1/* — ecosystem registry + showcase analytics

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add execution logging middleware
from middleware.logging_middleware import ExecutionLoggingMiddleware
app.add_middleware(ExecutionLoggingMiddleware)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ─── Universe Status Stubs (for SLA113 Registry health checks) ───
@app.get("/api/empire1/status")
async def empire1_status():
    return {"universe": "empire1", "status": "online", "description": "Hybrid Intelligence Core — 19 AI Engines", "product": "Hybrid Intelligence SaaS"}

@app.get("/api/southern/status")
async def southern_status():
    return {"universe": "southern", "status": "online", "description": "SouthernLifestyle Game OS", "product": "Southern Game OS"}

@app.get("/api/soulfire/status")
async def soulfire_status():
    return {"universe": "soulfire", "status": "online", "description": "Soulfire Ecosystem Blueprint (ASW, El Coro, Sentinel, SL Universal)", "product": "Lyrica 3 Pro — AI Music Creation", "engine": "Vertex AI"}
