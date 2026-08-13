import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

os.environ["MASTER_API_KEY"] = "test-master-key"
os.environ["PLATFORM_DOMAIN"] = "sla113.example.com"
os.environ["MONGO_URL"] = ""
os.environ["DB_NAME"] = "test_sla113_standalone"
os.environ["TENANT_CACHE_TTL"] = "0"

from app.core.database import connect_to_database, close_database_connection, get_database
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def init_db():
    await connect_to_database()
    yield
    await close_database_connection()


@pytest_asyncio.fixture
async def async_client(init_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def db(init_db):
    return get_database()


@pytest.fixture
def master_headers():
    return {"Authorization": "Bearer test-master-key"}


TENANT_A = {
    "id": "tenant-a",
    "name": "Tenant Alpha",
    "subdomain": "tenant-a",
    "plan": "pro",
    "status": "active",
    "admin_email": "admin@tenant-a.com",
    "brand": {"primary_color": "#ff0000", "operator_name": "Alpha"},
    "features": {
        "custom_domain": True, "api_access": True, "white_label": True,
        "analytics": True, "priority_support": True,
        "max_projects": 50, "max_builds_per_month": 200, "max_storage_mb": 10000,
    },
    "credits": 1000,
    "stats": {"total_projects": 0, "total_builds": 0, "total_deployments": 0, "total_storage_mb": 0},
}

TENANT_B = {
    "id": "tenant-b",
    "name": "Tenant Beta",
    "subdomain": "tenant-b",
    "plan": "free",
    "status": "active",
    "admin_email": "admin@tenant-b.com",
    "brand": {"primary_color": "#00ff00", "operator_name": "Beta"},
    "features": {
        "custom_domain": False, "api_access": False, "white_label": True,
        "analytics": False, "priority_support": False,
        "max_projects": 5, "max_builds_per_month": 10, "max_storage_mb": 500,
    },
    "credits": 100,
    "stats": {"total_projects": 0, "total_builds": 0, "total_deployments": 0, "total_storage_mb": 0},
}


@pytest_asyncio.fixture
async def seeded_db(db):
    await db["sla113_tenants"].delete_many({})
    await db["sla113_projects"].delete_many({})
    await db["sla113_builds"].delete_many({})
    await db["sla113_deployments"].delete_many({})
    await db["sla113_tenants"].insert_one(TENANT_A)
    await db["sla113_tenants"].insert_one(TENANT_B)
    return db


@pytest.fixture
def tenant_a_headers():
    return {"Host": "tenant-a.sla113.example.com"}


@pytest.fixture
def tenant_b_headers():
    return {"Host": "tenant-b.sla113.example.com"}
