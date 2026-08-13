"""Tests for subdomain resolution edge cases.

Uses conftest.py fixtures (init_db + async_client).
"""
import pytest
import pytest_asyncio
from tests.conftest import TENANT_A


@pytest_asyncio.fixture
async def tenant_with_status(db):
    await db["sla113_tenants"].delete_many({})
    await db["sla113_projects"].delete_many({})
    await db["sla113_builds"].delete_many({})
    await db["sla113_deployments"].delete_many({})
    docs = [
        {**TENANT_A, "_id": "prov", "subdomain": "provisioning-tenant", "status": "provisioning", "id": "prov"},
        {**TENANT_A, "_id": "susp", "subdomain": "suspended-tenant", "status": "suspended", "id": "susp"},
        {**TENANT_A, "_id": "actv", "subdomain": "active-tenant", "status": "active", "id": "actv"},
    ]
    await db["sla113_tenants"].insert_many(docs)
    return db


@pytest.mark.asyncio
async def test_valid_tenant_reachable(async_client, seeded_db):
    r = await async_client.get(
        "/api/console/stats",
        headers={"Host": "tenant-a.sla113.example.com"},
    )
    assert r.status_code == 200
    assert r.json()["tenant_id"] == "tenant-a"


@pytest.mark.asyncio
async def test_unknown_subdomain_404(async_client):
    r = await async_client.get(
        "/api/console/stats",
        headers={"Host": "nobody.sla113.example.com"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_bare_domain_no_tenant(async_client):
    r = await async_client.get(
        "/api/console/stats",
        headers={"Host": "sla113.example.com"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_www_prefix_no_tenant(async_client):
    r = await async_client.get(
        "/api/console/stats",
        headers={"Host": "www.sla113.example.com"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_deep_subdomain_no_tenant(async_client):
    r = await async_client.get(
        "/api/console/stats",
        headers={"Host": "a.b.sla113.example.com"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_missing_host_header(async_client):
    r = await async_client.get("/api/console/stats")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_ip_address_host(async_client):
    r = await async_client.get(
        "/api/console/stats",
        headers={"Host": "192.168.1.1"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_bare_endpoint_works_without_tenant(async_client):
    r = await async_client.get("/")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint_works_without_tenant(async_client):
    r = await async_client.get("/api/admin/health")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_provisioning_tenant_503(tenant_with_status, async_client):
    r = await async_client.get(
        "/api/console/stats",
        headers={"Host": "provisioning-tenant.sla113.example.com"},
    )
    assert r.status_code == 503
    assert "provisioning" in r.text.lower()


@pytest.mark.asyncio
async def test_suspended_tenant_403(tenant_with_status, async_client):
    r = await async_client.get(
        "/api/console/stats",
        headers={"Host": "suspended-tenant.sla113.example.com"},
    )
    assert r.status_code == 403
    assert "suspended" in r.text.lower()


@pytest.mark.asyncio
async def test_active_tenant_succeeds(tenant_with_status, async_client):
    r = await async_client.get(
        "/api/console/stats",
        headers={"Host": "active-tenant.sla113.example.com"},
    )
    assert r.status_code == 200
