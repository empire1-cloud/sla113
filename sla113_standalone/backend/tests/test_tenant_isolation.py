"""Tenant isolation tests.

Strategy:
  1. Seed two tenants (A and B) with known IDs/subdomains.
  2. As tenant A, create real data across all scoped resources.
  3. As tenant B, hit every scoped list/get endpoint — assert zero A data leaks.
  4. Positive control: as tenant A, verify own data is still reachable.
"""
import pytest


@pytest.mark.asyncio
async def test_tenant_isolation(
    async_client, seeded_db, tenant_a_headers, tenant_b_headers
):
    ha, hb = tenant_a_headers, tenant_b_headers

    # ─── Phase 1: Create tenant A data ───
    # Project 1
    r1 = await async_client.post(
        "/api/console/projects",
        json={
            "name": "Alpha Fish Shooter",
            "game_type": "fish_shooter",
            "description": "A's main game",
            "target_platform": "mobile",
            "theme": "aztec",
        },
        headers=ha,
    )
    assert r1.status_code == 200, f"Create project A1 failed: {r1.text}"
    p1 = r1.json()
    p1_id = p1["id"]

    # Project 2
    r2 = await async_client.post(
        "/api/console/projects",
        json={
            "name": "Alpha Slots",
            "game_type": "video_slots",
            "description": "A's second game",
            "target_platform": "web",
        },
        headers=ha,
    )
    assert r2.status_code == 200
    p2 = r2.json()

    # Build from project 1
    r3 = await async_client.post(
        "/api/console/builds",
        json={
            "project_id": p1_id,
            "target": "html5",
            "optimization": "size",
            "include_assets": True,
            "include_logic": True,
        },
        headers=ha,
    )
    assert r3.status_code == 200, f"Create build failed: {r3.text}"
    b1 = r3.json()
    b1_id = b1["id"]

    # Advance build to completion (5 stages × 2 advances each = 10)
    for _ in range(12):
        r = await async_client.post(
            f"/api/console/builds/{b1_id}/advance",
            headers=ha,
        )
        assert r.status_code == 200
        if r.json()["status"] == "completed":
            break

    # Verify build completed
    r4 = await async_client.get(
        f"/api/console/builds/{b1_id}",
        headers=ha,
    )
    assert r4.status_code == 200
    assert r4.json()["status"] == "completed"

    # Deploy the completed build
    r5 = await async_client.post(
        f"/api/deploy/{b1_id}?label=v1.0.0",
        headers=ha,
    )
    assert r5.status_code == 200, f"Deploy failed: {r5.text}"
    d1 = r5.json()

    # ─── Phase 2: Tenant B sees NO tenant A data ───
    # Projects list — must be empty
    r = await async_client.get("/api/console/projects", headers=hb)
    assert r.status_code == 200
    assert r.json()["total"] == 0, f"Tenant B sees A's projects: {r.json()}"
    assert r.json()["projects"] == []

    # Builds list — must be empty
    r = await async_client.get("/api/console/builds", headers=hb)
    assert r.status_code == 200
    assert r.json()["total"] == 0, f"Tenant B sees A's builds: {r.json()}"

    # Deployments list — must be empty
    r = await async_client.get("/api/deploy/list", headers=hb)
    assert r.status_code == 200
    assert r.json()["total"] == 0, f"Tenant B sees A's deployments: {r.json()}"

    # Console stats — must show zeros
    r = await async_client.get("/api/console/stats", headers=hb)
    assert r.status_code == 200
    stats = r.json()
    assert stats["total_projects"] == 0
    assert stats["total_builds"] == 0
    assert stats["total_deployments"] == 0

    # Billing usage — must show zeros
    r = await async_client.get("/api/billing/usage", headers=hb)
    assert r.status_code == 200
    usage = r.json()
    assert usage["projects_current"] == 0
    assert usage["builds_this_month"] == 0

    # ─── Phase 3: Negative tests — direct resource access ───
    # Tenant B tries to GET tenant A's project directly
    r = await async_client.get(
        f"/api/console/projects/{p1_id}",
        headers=hb,
    )
    assert r.status_code == 404, f"Tenant B should not see A's project: {r.text}"

    # Tenant B tries to GET tenant A's build directly
    r = await async_client.get(
        f"/api/console/builds/{b1_id}",
        headers=hb,
    )
    assert r.status_code == 404, f"Tenant B should not see A's build: {r.text}"

    # Tenant B tries to GET tenant A's deployment directly
    r = await async_client.get(
        f"/api/deploy/{d1['id']}",
        headers=hb,
    )
    assert r.status_code == 404, f"Tenant B should not see A's deploy: {r.text}"

    # Tenant B tries to delete tenant A's project
    r = await async_client.delete(
        f"/api/console/projects/{p1_id}",
        headers=hb,
    )
    assert r.status_code == 404

    # Tenant B tries to create a build from tenant A's project
    r = await async_client.post(
        "/api/console/builds",
        json={
            "project_id": p1_id,
            "target": "html5",
            "optimization": "size",
            "include_assets": True,
            "include_logic": True,
        },
        headers=hb,
    )
    assert r.status_code == 404, f"Tenant B should not build A's project: {r.text}"

    # Tenant B tries to deploy tenant A's build
    r = await async_client.post(
        f"/api/deploy/{b1_id}?label=hack-attempt",
        headers=hb,
    )
    assert r.status_code == 404, f"Tenant B should not deploy A's build: {r.text}"

    # ─── Phase 4: Positive control — tenant A still sees own data ───
    r = await async_client.get("/api/console/projects", headers=ha)
    assert r.status_code == 200
    assert r.json()["total"] == 2, f"A should see 2 projects: {r.json()}"

    r = await async_client.get("/api/console/builds", headers=ha)
    assert r.status_code == 200
    assert r.json()["total"] == 1, f"A should see 1 build: {r.json()}"

    r = await async_client.get("/api/deploy/list", headers=ha)
    assert r.status_code == 200
    assert r.json()["total"] == 1, f"A should see 1 deployment: {r.json()}"

    # Stats check
    r = await async_client.get("/api/console/stats", headers=ha)
    assert r.status_code == 200
    s = r.json()
    assert s["total_projects"] == 2
    assert s["total_builds"] == 1
    assert s["total_deployments"] == 1
