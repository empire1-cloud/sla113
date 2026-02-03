from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
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

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(
    title="Hybrid AI Stack",
    description="Multi-model AI pipeline with GPT-5.2, Claude Sonnet 4.5, and Gemini 3 Flash",
    version="1.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

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
)

# Include all engine routers
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

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()