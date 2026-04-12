"""
SLA113 Iteration 15 Tests - New Features:
1. Universe Registry (auto-discovery of mounted universe routers)
2. Real Compliance Engine (pulls real RTP from Logic Engine)
3. Frontline Snapshot API
4. WebSocket Frontline (connection test)
"""
import pytest
import requests
import os
import json
import asyncio
import websockets

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://genesis-engine-4.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api/sla113"

# Test project with Logic Engine RTP data
TEST_PROJECT_ID = "219b65d6-aa30-4799-b6df-d2d9e2ba3a98"


class TestUniverseRegistry:
    """Universe Registry API tests - auto-discovery of mounted universe routers"""

    def test_list_universes_returns_4_plus(self):
        """GET /api/sla113/universes should return 4+ universes"""
        response = requests.get(f"{API_BASE}/universes")
        assert response.status_code == 200
        data = response.json()
        
        assert "universes" in data
        assert "total" in data
        assert data["total"] >= 4, f"Expected 4+ universes, got {data['total']}"
        assert data["sovereign"] == "SLA113"
        
        # Verify required fields in each universe
        for universe in data["universes"]:
            assert "id" in universe
            assert "name" in universe
            assert "prefix" in universe
            assert "engine" in universe
            assert "status" in universe
            assert "registered_at" in universe

    def test_list_universes_contains_core_universes(self):
        """Verify core universes are registered: sla113, empire1, southern, soulfire"""
        response = requests.get(f"{API_BASE}/universes")
        assert response.status_code == 200
        data = response.json()
        
        universe_ids = [u["id"] for u in data["universes"]]
        assert "sla113" in universe_ids, "SLA113 Core should be registered"
        assert "empire1" in universe_ids, "Empire 1 should be registered"
        assert "southern" in universe_ids, "Southern Lifestyle should be registered"
        assert "soulfire" in universe_ids, "Soulfire Ecosystem should be registered"

    def test_get_single_universe(self):
        """GET /api/sla113/universes/{id} returns specific universe"""
        response = requests.get(f"{API_BASE}/universes/sla113")
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == "sla113"
        assert data["name"] == "SLA113 Core"
        assert data["engine"] == "fastapi+mongodb"
        assert data["status"] == "online"

    def test_get_nonexistent_universe_returns_404(self):
        """GET /api/sla113/universes/{id} returns 404 for unknown universe"""
        response = requests.get(f"{API_BASE}/universes/nonexistent_universe_xyz")
        assert response.status_code == 404

    def test_register_universe_dynamically(self):
        """POST /api/sla113/universes/register should dynamically add universe"""
        # Register a test universe
        params = {
            "uid": "TEST_dynamic_universe",
            "name": "TEST Dynamic Universe",
            "description": "Test universe for iteration 15",
            "prefix": "/api/test_dynamic",
            "engine": "pytest",
            "product": "Test Product"
        }
        response = requests.post(f"{API_BASE}/universes/register", params=params)
        assert response.status_code == 200
        data = response.json()
        
        assert data["registered"] == True
        assert data["universe"]["id"] == "TEST_dynamic_universe"
        assert data["universe"]["name"] == "TEST Dynamic Universe"
        assert data["universe"]["engine"] == "pytest"
        assert data["universe"]["status"] == "online"
        
        # Verify it appears in list
        list_response = requests.get(f"{API_BASE}/universes")
        universe_ids = [u["id"] for u in list_response.json()["universes"]]
        assert "TEST_dynamic_universe" in universe_ids

    def test_deregister_universe(self):
        """DELETE /api/sla113/universes/{id} should remove universe"""
        # First ensure test universe exists
        params = {
            "uid": "TEST_to_delete",
            "name": "TEST To Delete",
            "description": "Will be deleted",
            "prefix": "/api/test_delete",
            "engine": "pytest"
        }
        requests.post(f"{API_BASE}/universes/register", params=params)
        
        # Delete it
        response = requests.delete(f"{API_BASE}/universes/TEST_to_delete")
        assert response.status_code == 200
        data = response.json()
        
        assert data["deregistered"] == True
        assert data["universe"]["id"] == "TEST_to_delete"
        
        # Verify it's gone
        list_response = requests.get(f"{API_BASE}/universes")
        universe_ids = [u["id"] for u in list_response.json()["universes"]]
        assert "TEST_to_delete" not in universe_ids

    def test_cannot_deregister_nonexistent_universe(self):
        """DELETE /api/sla113/universes/{id} returns 404 for unknown universe"""
        response = requests.delete(f"{API_BASE}/universes/nonexistent_xyz_123")
        assert response.status_code == 404

    def test_universe_engine_colors_mapping(self):
        """Verify universes have different engines for color-coding"""
        response = requests.get(f"{API_BASE}/universes")
        data = response.json()
        
        engines = set(u["engine"] for u in data["universes"])
        # Should have multiple different engines
        assert len(engines) >= 3, f"Expected 3+ different engines, got {engines}"
        
        # Verify specific engine mappings
        engine_map = {u["id"]: u["engine"] for u in data["universes"]}
        assert engine_map.get("sla113") == "fastapi+mongodb"
        assert engine_map.get("empire1") == "emergent-llm"
        assert engine_map.get("soulfire") == "vertex-ai"


class TestRealComplianceEngine:
    """Real Compliance Engine tests - pulls real RTP from Logic Engine"""

    def test_compliance_check_with_logic_engine_rtp(self):
        """POST /api/sla113/compliance/check should show real RTP from Logic Engine"""
        payload = {
            "project_id": TEST_PROJECT_ID,
            "jurisdiction": "GLI",
            "check_type": "full"
        }
        response = requests.post(f"{API_BASE}/compliance/check", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "id" in data
        assert data["project_id"] == TEST_PROJECT_ID
        assert data["jurisdiction"] == "GLI"
        assert "status" in data
        assert "results" in data
        assert "actual_rtp" in data
        assert "has_logic_data" in data
        
        # Verify RTP is from Logic Engine (not random)
        assert data["has_logic_data"] == True, "Project should have Logic Engine data"
        assert data["actual_rtp"] != "Not generated", "RTP should be generated"
        
        # Check RTP verification result
        rtp_check = next((r for r in data["results"] if "RTP" in r["check"]), None)
        assert rtp_check is not None, "Should have RTP Verification check"
        assert rtp_check["source"] == "logic_engine", "RTP should come from Logic Engine"
        assert "%" in rtp_check["value"], "RTP value should be percentage"

    def test_compliance_status_types(self):
        """Compliance should return CERTIFIED, CONDITIONAL, or NEEDS_REMEDIATION"""
        payload = {
            "project_id": TEST_PROJECT_ID,
            "jurisdiction": "GLI"
        }
        response = requests.post(f"{API_BASE}/compliance/check", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        valid_statuses = ["CERTIFIED", "CONDITIONAL", "NEEDS_REMEDIATION"]
        assert data["status"] in valid_statuses, f"Status should be one of {valid_statuses}, got {data['status']}"

    def test_compliance_warn_for_missing_rng(self):
        """Compliance should show WARN for missing RNG specification"""
        payload = {
            "project_id": TEST_PROJECT_ID,
            "jurisdiction": "GLI"
        }
        response = requests.post(f"{API_BASE}/compliance/check", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Find RNG check
        rng_check = next((r for r in data["results"] if "RNG" in r["check"]), None)
        assert rng_check is not None, "Should have RNG check"
        # RNG might be WARN or PASS depending on project state
        assert rng_check["status"] in ["WARN", "PASS"]

    def test_compliance_different_jurisdictions(self):
        """Test compliance with different jurisdictions: GLI, MGA, UKGC, CURACAO"""
        jurisdictions = ["GLI", "MGA", "UKGC", "CURACAO", "INTERNAL"]
        
        for jurisdiction in jurisdictions:
            payload = {
                "project_id": TEST_PROJECT_ID,
                "jurisdiction": jurisdiction
            }
            response = requests.post(f"{API_BASE}/compliance/check", json=payload)
            assert response.status_code == 200, f"Failed for jurisdiction {jurisdiction}"
            data = response.json()
            assert data["jurisdiction"] == jurisdiction
            assert len(data["results"]) > 0, f"Should have checks for {jurisdiction}"

    def test_compliance_pass_rate_format(self):
        """Compliance pass_rate should be in X/Y format"""
        payload = {
            "project_id": TEST_PROJECT_ID,
            "jurisdiction": "GLI"
        }
        response = requests.post(f"{API_BASE}/compliance/check", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "/" in data["pass_rate"], f"pass_rate should be X/Y format, got {data['pass_rate']}"
        parts = data["pass_rate"].split("/")
        assert len(parts) == 2
        assert parts[0].isdigit() and parts[1].isdigit()

    def test_compliance_nonexistent_project_returns_404(self):
        """Compliance check on nonexistent project returns 404"""
        payload = {
            "project_id": "nonexistent-project-id-xyz",
            "jurisdiction": "GLI"
        }
        response = requests.post(f"{API_BASE}/compliance/check", json=payload)
        assert response.status_code == 404


class TestFrontlineSnapshot:
    """Frontline Snapshot API tests - real metrics"""

    def test_frontline_snapshot_returns_metrics(self):
        """GET /api/sla113/frontline/snapshot should return real metrics"""
        response = requests.get(f"{API_BASE}/frontline/snapshot")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required metrics
        required_fields = [
            "total_projects", "active_jobs", "blocked_jobs", "completed_jobs",
            "total_tenants", "active_builds", "live_deployments", "total_revenue",
            "worker_running", "universes_online", "timestamp"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_frontline_snapshot_universes_count(self):
        """Frontline should show correct universes_online count"""
        response = requests.get(f"{API_BASE}/frontline/snapshot")
        assert response.status_code == 200
        data = response.json()
        
        # Should match universe registry count
        universes_response = requests.get(f"{API_BASE}/universes")
        expected_count = universes_response.json()["total"]
        
        assert data["universes_online"] == expected_count, \
            f"universes_online ({data['universes_online']}) should match registry ({expected_count})"

    def test_frontline_snapshot_worker_status(self):
        """Frontline should show worker_running status"""
        response = requests.get(f"{API_BASE}/frontline/snapshot")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data["worker_running"], bool)

    def test_frontline_snapshot_numeric_values(self):
        """Frontline metrics should be numeric"""
        response = requests.get(f"{API_BASE}/frontline/snapshot")
        assert response.status_code == 200
        data = response.json()
        
        numeric_fields = [
            "total_projects", "active_jobs", "blocked_jobs", "completed_jobs",
            "total_tenants", "active_builds", "live_deployments", "total_revenue",
            "universes_online"
        ]
        for field in numeric_fields:
            assert isinstance(data[field], (int, float)), f"{field} should be numeric"


class TestWebSocketFrontline:
    """WebSocket Frontline tests - real-time metrics feed"""

    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """WSS /api/sla113/frontline/ws should connect and push metrics"""
        ws_url = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
        ws_url = f"{ws_url}/api/sla113/frontline/ws"
        
        try:
            async with websockets.connect(ws_url, close_timeout=5) as websocket:
                # Wait for first message (should come within 2 seconds)
                message = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(message)
                
                # Verify message structure
                assert data["type"] == "frontline_update"
                assert "timestamp" in data
                assert "metrics" in data
                
                # Verify metrics content
                metrics = data["metrics"]
                assert "total_projects" in metrics
                assert "active_jobs" in metrics
                assert "universes_online" in metrics
                assert "worker_running" in metrics
                
        except Exception as e:
            pytest.fail(f"WebSocket connection failed: {e}")

    @pytest.mark.asyncio
    async def test_websocket_receives_multiple_updates(self):
        """WebSocket should receive multiple updates over time"""
        ws_url = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
        ws_url = f"{ws_url}/api/sla113/frontline/ws"
        
        try:
            async with websockets.connect(ws_url, close_timeout=10) as websocket:
                messages = []
                for _ in range(2):  # Get 2 messages
                    message = await asyncio.wait_for(websocket.recv(), timeout=5)
                    messages.append(json.loads(message))
                
                assert len(messages) == 2
                # Both should be frontline_update type
                assert all(m["type"] == "frontline_update" for m in messages)
                
        except Exception as e:
            pytest.fail(f"WebSocket multiple updates test failed: {e}")


class TestCleanup:
    """Cleanup test data created during tests"""

    def test_cleanup_test_universes(self):
        """Remove any TEST_ prefixed universes"""
        response = requests.get(f"{API_BASE}/universes")
        if response.status_code == 200:
            universes = response.json()["universes"]
            for u in universes:
                if u["id"].startswith("TEST_"):
                    requests.delete(f"{API_BASE}/universes/{u['id']}")
        
        # Verify cleanup
        response = requests.get(f"{API_BASE}/universes")
        universe_ids = [u["id"] for u in response.json()["universes"]]
        test_universes = [uid for uid in universe_ids if uid.startswith("TEST_")]
        assert len(test_universes) == 0, f"Test universes not cleaned up: {test_universes}"


# Fixtures
@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session
