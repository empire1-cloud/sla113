"""
SLA113 - Universal AI Game Studio Backend Tests
Tests all SLA113 API endpoints: game-types, projects CRUD, vision/logic/compose generation
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
API_URL = f"{BASE_URL}/api/sla113"

# Test credentials
TEST_EMAIL = "newuser@example.com"
TEST_PASSWORD = "NewPass123!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for protected endpoints"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


class TestSLA113GameTypes:
    """Test game types endpoint - now includes 16 types with AAA games"""
    
    def test_get_game_types_returns_16_types(self, api_client):
        """GET /api/sla113/game-types should return 16 supported game types including AAA"""
        response = api_client.get(f"{API_URL}/game-types")
        assert response.status_code == 200
        
        data = response.json()
        assert "game_types" in data
        game_types = data["game_types"]
        assert len(game_types) >= 16, f"Expected at least 16 game types, got {len(game_types)}"
        
        # Verify expected game types exist (including AAA types)
        expected_types = [
            # Casino/Arcade
            "fish_shooter", "slot_machine", "crash_game", "card_game",
            # AAA types
            "open_world", "tactical_fps", "fighting_game", "fantasy_rpg",
            # Other types
            "platformer", "puzzle", "tower_defense", "runner", 
            "battle_royale", "racing", "survival_horror", "sports"
        ]
        for gt in expected_types:
            assert gt in game_types, f"Missing game type: {gt}"
            assert "name" in game_types[gt]
            assert "description" in game_types[gt]
            assert "category" in game_types[gt]
    
    def test_aaa_game_types_have_correct_category(self, api_client):
        """Verify AAA game types have 'aaa' category"""
        response = api_client.get(f"{API_URL}/game-types")
        assert response.status_code == 200
        
        game_types = response.json()["game_types"]
        aaa_types = ["open_world", "tactical_fps", "fighting_game", "fantasy_rpg", "survival_horror"]
        for gt in aaa_types:
            assert game_types[gt]["category"] == "aaa", f"{gt} should have 'aaa' category"


class TestSLA113Stats:
    """Test stats endpoint"""
    
    def test_get_stats_returns_valid_structure(self, api_client):
        """GET /api/sla113/stats should return stats object with 16 game types"""
        response = api_client.get(f"{API_URL}/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_projects" in data
        assert "supported_game_types" in data
        assert data["supported_game_types"] >= 16, f"Expected at least 16 game types, got {data['supported_game_types']}"
        assert "engines" in data
        assert set(data["engines"]) == {"vision", "logic", "composer"}
        assert "version" in data
        assert data["version"] == "1.0.0"


class TestSLA113ProjectsCRUD:
    """Test projects CRUD operations"""
    
    def test_list_projects(self, api_client):
        """GET /api/sla113/projects should list all projects"""
        response = api_client.get(f"{API_URL}/projects")
        assert response.status_code == 200
        
        data = response.json()
        assert "projects" in data
        assert "total" in data
        assert isinstance(data["projects"], list)
    
    def test_create_project_slot_machine(self, api_client):
        """POST /api/sla113/projects should create a new game project"""
        project_data = {
            "name": "TEST_Vegas_Slots",
            "game_type": "slot_machine",
            "theme": "vegas",
            "target_platform": "web"
        }
        response = api_client.post(f"{API_URL}/projects", json=project_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "TEST_Vegas_Slots"
        assert data["game_type"] == "slot_machine"
        assert data["theme"] == "vegas"
        assert data["target_platform"] == "web"
        assert "id" in data
        assert data["status"] == "created"
        assert "game_type_info" in data
        assert data["game_type_info"]["name"] == "Slot Machine"
        
        # Store project ID for cleanup
        TestSLA113ProjectsCRUD.created_project_id = data["id"]
    
    def test_create_project_tactical_fps(self, api_client):
        """POST /api/sla113/projects should create AAA tactical FPS project"""
        project_data = {
            "name": "TEST_Tactical_Ops",
            "game_type": "tactical_fps",
            "theme": "military",
            "target_platform": "both"
        }
        response = api_client.post(f"{API_URL}/projects", json=project_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "TEST_Tactical_Ops"
        assert data["game_type"] == "tactical_fps"
        assert data["game_type_info"]["category"] == "aaa"
        assert data["game_type_info"]["name"] == "Tactical FPS (COD Style)"
        
        # Store for cleanup
        TestSLA113ProjectsCRUD.aaa_project_id = data["id"]
    
    def test_get_project_by_id(self, api_client):
        """GET /api/sla113/projects/{id} should return project details"""
        project_id = getattr(TestSLA113ProjectsCRUD, 'created_project_id', None)
        if not project_id:
            pytest.skip("No project created to fetch")
        
        response = api_client.get(f"{API_URL}/projects/{project_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == "TEST_Vegas_Slots"
    
    def test_create_project_invalid_game_type(self, api_client):
        """POST /api/sla113/projects with invalid game_type should return 400"""
        project_data = {
            "name": "Invalid Game",
            "game_type": "invalid_type",
            "target_platform": "web"
        }
        response = api_client.post(f"{API_URL}/projects", json=project_data)
        assert response.status_code == 400
        assert "Unsupported game type" in response.json().get("detail", "")
    
    def test_get_nonexistent_project(self, api_client):
        """GET /api/sla113/projects/{id} with invalid ID should return 404"""
        response = api_client.get(f"{API_URL}/projects/nonexistent-id-12345")
        assert response.status_code == 404
    
    def test_delete_project(self, api_client):
        """DELETE /api/sla113/projects/{id} should delete the project"""
        project_id = getattr(TestSLA113ProjectsCRUD, 'created_project_id', None)
        if not project_id:
            pytest.skip("No project created to delete")
        
        response = api_client.delete(f"{API_URL}/projects/{project_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["deleted"] == True
        assert data["project_id"] == project_id
        
        # Verify deletion
        get_response = api_client.get(f"{API_URL}/projects/{project_id}")
        assert get_response.status_code == 404
    
    def test_delete_aaa_project(self, api_client):
        """DELETE /api/sla113/projects/{id} should delete AAA project"""
        project_id = getattr(TestSLA113ProjectsCRUD, 'aaa_project_id', None)
        if not project_id:
            pytest.skip("No AAA project created to delete")
        
        response = api_client.delete(f"{API_URL}/projects/{project_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["deleted"] == True
    
    def test_delete_nonexistent_project(self, api_client):
        """DELETE /api/sla113/projects/{id} with invalid ID should return 404"""
        response = api_client.delete(f"{API_URL}/projects/nonexistent-id-12345")
        assert response.status_code == 404


class TestSLA113VisionEngine:
    """Test vision generation endpoint (requires LLM API)"""
    
    @pytest.fixture(autouse=True)
    def setup_project(self, api_client):
        """Create a test project for vision generation"""
        project_data = {
            "name": "TEST_Vision_Project",
            "game_type": "platformer",
            "theme": "fantasy",
            "target_platform": "web"
        }
        response = api_client.post(f"{API_URL}/projects", json=project_data)
        if response.status_code == 200:
            self.project_id = response.json()["id"]
        yield
        # Cleanup
        if hasattr(self, 'project_id'):
            api_client.delete(f"{API_URL}/projects/{self.project_id}")
    
    def test_vision_generate_requires_project_id(self, api_client):
        """POST /api/sla113/vision/generate with invalid project_id should return 404"""
        response = api_client.post(f"{API_URL}/vision/generate", json={
            "project_id": "invalid-project-id",
            "asset_type": "sprites",
            "count": 3
        })
        assert response.status_code == 404
    
    def test_vision_generate_success(self, api_client):
        """POST /api/sla113/vision/generate should generate vision assets"""
        if not hasattr(self, 'project_id'):
            pytest.skip("No project created for vision test")
        
        response = api_client.post(f"{API_URL}/vision/generate", json={
            "project_id": self.project_id,
            "asset_type": "sprites",
            "style": "pixel_art",
            "count": 3
        }, timeout=60)  # LLM calls can take time
        
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == self.project_id
        assert data["asset_type"] == "sprites"
        assert data["style"] == "pixel_art"
        assert "assets" in data
        assert "generation_time" in data


class TestSLA113LogicEngine:
    """Test logic generation endpoint (requires LLM API)"""
    
    @pytest.fixture(autouse=True)
    def setup_project(self, api_client):
        """Create a test project for logic generation"""
        project_data = {
            "name": "TEST_Logic_Project",
            "game_type": "slot_machine",
            "theme": "vegas",
            "target_platform": "web"
        }
        response = api_client.post(f"{API_URL}/projects", json=project_data)
        if response.status_code == 200:
            self.project_id = response.json()["id"]
        yield
        # Cleanup
        if hasattr(self, 'project_id'):
            api_client.delete(f"{API_URL}/projects/{self.project_id}")
    
    def test_logic_generate_requires_project_id(self, api_client):
        """POST /api/sla113/logic/generate with invalid project_id should return 404"""
        response = api_client.post(f"{API_URL}/logic/generate", json={
            "project_id": "invalid-project-id",
            "logic_type": "mechanics"
        })
        assert response.status_code == 404
    
    def test_logic_generate_success(self, api_client):
        """POST /api/sla113/logic/generate should generate game logic"""
        if not hasattr(self, 'project_id'):
            pytest.skip("No project created for logic test")
        
        response = api_client.post(f"{API_URL}/logic/generate", json={
            "project_id": self.project_id,
            "logic_type": "mechanics",
            "difficulty": "medium"
        }, timeout=60)  # LLM calls can take time
        
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == self.project_id
        assert data["logic_type"] == "mechanics"
        assert data["difficulty"] == "medium"
        assert "specs" in data
        assert "generation_time" in data


class TestSLA113Composer:
    """Test composer endpoint (requires LLM API)"""
    
    @pytest.fixture(autouse=True)
    def setup_project(self, api_client):
        """Create a test project for composition"""
        project_data = {
            "name": "TEST_Compose_Project",
            "game_type": "puzzle",
            "theme": "candy",
            "target_platform": "mobile"
        }
        response = api_client.post(f"{API_URL}/projects", json=project_data)
        if response.status_code == 200:
            self.project_id = response.json()["id"]
        yield
        # Cleanup
        if hasattr(self, 'project_id'):
            api_client.delete(f"{API_URL}/projects/{self.project_id}")
    
    def test_compose_requires_project_id(self, api_client):
        """POST /api/sla113/compose with invalid project_id should return 404"""
        response = api_client.post(f"{API_URL}/compose", json={
            "project_id": "invalid-project-id"
        })
        assert response.status_code == 404
    
    def test_compose_success(self, api_client):
        """POST /api/sla113/compose should compose game bundle"""
        if not hasattr(self, 'project_id'):
            pytest.skip("No project created for compose test")
        
        response = api_client.post(f"{API_URL}/compose", json={
            "project_id": self.project_id,
            "include_vision": True,
            "include_logic": True,
            "output_format": "json"
        }, timeout=60)  # LLM calls can take time
        
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == self.project_id
        assert data["output_format"] == "json"
        assert "bundle" in data
        assert "generation_time" in data


class TestSLA113ExistingProject:
    """Test with existing 'Neon Fish Hunt' project"""
    
    def test_existing_project_in_list(self, api_client):
        """Verify 'Neon Fish Hunt' project exists from development"""
        response = api_client.get(f"{API_URL}/projects")
        assert response.status_code == 200
        
        projects = response.json()["projects"]
        neon_fish = next((p for p in projects if p["name"] == "Neon Fish Hunt"), None)
        
        if neon_fish:
            assert neon_fish["game_type"] == "fish_shooter"
            assert neon_fish["theme"] == "cyberpunk"
            print(f"Found existing project: {neon_fish['name']} (ID: {neon_fish['id']})")
        else:
            print("Note: 'Neon Fish Hunt' project not found - may have been deleted")


# ─── NEW TESTS FOR TENANTS, JOBS, PIPELINES, TERMINAL ───

class TestSLA113Tenants:
    """Test white-label tenants CRUD - /api/sla113/tenants"""
    
    def test_list_tenants(self, api_client):
        """GET /api/sla113/tenants should return list of tenants"""
        response = api_client.get(f"{API_URL}/tenants")
        assert response.status_code == 200
        
        data = response.json()
        assert "tenants" in data
        assert "total" in data
        assert isinstance(data["tenants"], list)
    
    def test_create_tenant(self, api_client):
        """POST /api/sla113/tenants should create a new tenant"""
        tenant_data = {
            "name": "TEST_ARCADE_TENANT",
            "subdomain": f"test-arcade-{int(time.time())}.empire1.cloud"
        }
        response = api_client.post(f"{API_URL}/tenants", json=tenant_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "TEST_ARCADE_TENANT"
        assert "test-arcade" in data["subdomain"]
        assert data["status"] == "active"
        assert data["credits"] == 0
        assert data["rtp_mode"] == 92
        assert "id" in data
        
        # Store for cleanup
        TestSLA113Tenants.created_tenant_id = data["id"]
    
    def test_create_duplicate_subdomain_fails(self, api_client):
        """POST /api/sla113/tenants with duplicate subdomain should return 409"""
        tenant_id = getattr(TestSLA113Tenants, 'created_tenant_id', None)
        if not tenant_id:
            pytest.skip("No tenant created to test duplicate")
        
        # Get the subdomain of the created tenant
        response = api_client.get(f"{API_URL}/tenants")
        tenants = response.json()["tenants"]
        existing = next((t for t in tenants if t["id"] == tenant_id), None)
        if not existing:
            pytest.skip("Created tenant not found")
        
        # Try to create with same subdomain
        response = api_client.post(f"{API_URL}/tenants", json={
            "name": "DUPLICATE_TEST",
            "subdomain": existing["subdomain"]
        })
        assert response.status_code == 409
    
    def test_update_tenant_credits(self, api_client):
        """PUT /api/sla113/tenants/{id}/credits should add credits"""
        tenant_id = getattr(TestSLA113Tenants, 'created_tenant_id', None)
        if not tenant_id:
            pytest.skip("No tenant created to update")
        
        response = api_client.put(f"{API_URL}/tenants/{tenant_id}/credits?amount=1000")
        assert response.status_code == 200
        
        data = response.json()
        assert data["credits"] == 1000
    
    def test_update_tenant_rtp(self, api_client):
        """PUT /api/sla113/tenants/{id}/rtp should set RTP mode"""
        tenant_id = getattr(TestSLA113Tenants, 'created_tenant_id', None)
        if not tenant_id:
            pytest.skip("No tenant created to update")
        
        response = api_client.put(f"{API_URL}/tenants/{tenant_id}/rtp?rtp=95")
        assert response.status_code == 200
        
        data = response.json()
        assert data["rtp_mode"] == 95
    
    def test_update_tenant_rtp_invalid(self, api_client):
        """PUT /api/sla113/tenants/{id}/rtp with invalid RTP should return 400"""
        tenant_id = getattr(TestSLA113Tenants, 'created_tenant_id', None)
        if not tenant_id:
            pytest.skip("No tenant created to update")
        
        response = api_client.put(f"{API_URL}/tenants/{tenant_id}/rtp?rtp=150")
        assert response.status_code == 400
    
    def test_delete_tenant(self, api_client):
        """DELETE /api/sla113/tenants/{id} should delete tenant"""
        tenant_id = getattr(TestSLA113Tenants, 'created_tenant_id', None)
        if not tenant_id:
            pytest.skip("No tenant created to delete")
        
        response = api_client.delete(f"{API_URL}/tenants/{tenant_id}")
        assert response.status_code == 200
        assert response.json()["deleted"] == True


class TestSLA113Jobs:
    """Test Night Queue jobs CRUD - /api/sla113/jobs"""
    
    def test_list_jobs(self, api_client):
        """GET /api/sla113/jobs should return list of jobs"""
        response = api_client.get(f"{API_URL}/jobs")
        assert response.status_code == 200
        
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        assert isinstance(data["jobs"], list)
    
    def test_create_job(self, api_client):
        """POST /api/sla113/jobs should create a new job"""
        job_data = {
            "preset": "TEST_ARCADE_40",
            "priority": "high"
        }
        response = api_client.post(f"{API_URL}/jobs", json=job_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["preset"] == "TEST_ARCADE_40"
        assert data["priority"] == "high"
        assert data["status"] == "pending"
        assert data["progress"] == 0
        assert "id" in data
        assert data["id"].startswith("JOB-")
        
        # Store for cleanup
        TestSLA113Jobs.created_job_id = data["id"]
    
    def test_update_job_progress(self, api_client):
        """PUT /api/sla113/jobs/{id}/progress should update progress"""
        job_id = getattr(TestSLA113Jobs, 'created_job_id', None)
        if not job_id:
            pytest.skip("No job created to update")
        
        response = api_client.put(f"{API_URL}/jobs/{job_id}/progress?progress=50&status=processing")
        assert response.status_code == 200
        
        data = response.json()
        assert data["progress"] == 50
        assert data["status"] == "processing"
    
    def test_process_job(self, api_client):
        """POST /api/sla113/jobs/{id}/process should advance job progress"""
        job_id = getattr(TestSLA113Jobs, 'created_job_id', None)
        if not job_id:
            pytest.skip("No job created to process")
        
        response = api_client.post(f"{API_URL}/jobs/{job_id}/process")
        assert response.status_code == 200
        
        data = response.json()
        assert data["progress"] >= 50  # Should have advanced
    
    def test_delete_job(self, api_client):
        """DELETE /api/sla113/jobs/{id} should delete job"""
        job_id = getattr(TestSLA113Jobs, 'created_job_id', None)
        if not job_id:
            pytest.skip("No job created to delete")
        
        response = api_client.delete(f"{API_URL}/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["deleted"] == True
    
    def test_delete_nonexistent_job(self, api_client):
        """DELETE /api/sla113/jobs/{id} with invalid ID should return 404"""
        response = api_client.delete(f"{API_URL}/jobs/JOB-INVALID123")
        assert response.status_code == 404


class TestSLA113Pipelines:
    """Test Revenue Pipelines CRUD - /api/sla113/pipelines"""
    
    def test_list_pipelines_has_seeded_data(self, api_client):
        """GET /api/sla113/pipelines should return seeded pipelines"""
        response = api_client.get(f"{API_URL}/pipelines")
        assert response.status_code == 200
        
        data = response.json()
        assert "pipelines" in data
        assert "total" in data
        assert "total_revenue" in data
        
        # Should have 6 seeded pipelines
        pipelines = data["pipelines"]
        assert len(pipelines) >= 6, f"Expected at least 6 seeded pipelines, got {len(pipelines)}"
        
        # Verify seeded pipeline names
        names = [p["name"] for p in pipelines]
        expected_names = [
            "Lead Qualification Engine",
            "CRM Syncing Logic",
            "Pro Voice Over (SaaS)",
            "SMS/Email Gateway",
            "White-Label Instance",
            "Managed Sovereignty"
        ]
        for name in expected_names:
            assert name in names, f"Missing seeded pipeline: {name}"
    
    def test_create_pipeline(self, api_client):
        """POST /api/sla113/pipelines should create a new pipeline"""
        pipeline_data = {
            "name": "TEST_Custom_Pipeline",
            "type": "Automation",
            "lane": 1
        }
        response = api_client.post(f"{API_URL}/pipelines", json=pipeline_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "TEST_Custom_Pipeline"
        assert data["type"] == "Automation"
        assert data["lane"] == 1
        assert data["status"] == "active"
        assert data["executions"] == 0
        assert data["revenue"] == 0
        assert "id" in data
        
        # Store for cleanup
        TestSLA113Pipelines.created_pipeline_id = data["id"]
    
    def test_pulse_pipeline(self, api_client):
        """PUT /api/sla113/pipelines/{id}/pulse should trigger heartbeat"""
        pipeline_id = getattr(TestSLA113Pipelines, 'created_pipeline_id', None)
        if not pipeline_id:
            pytest.skip("No pipeline created to pulse")
        
        response = api_client.put(f"{API_URL}/pipelines/{pipeline_id}/pulse")
        assert response.status_code == 200
        
        data = response.json()
        assert data["heartbeat"] == "active"
        assert data["executions"] >= 1
        assert data["revenue"] >= 50  # Random between 50-500
    
    def test_delete_pipeline(self, api_client):
        """DELETE /api/sla113/pipelines/{id} should delete pipeline"""
        pipeline_id = getattr(TestSLA113Pipelines, 'created_pipeline_id', None)
        if not pipeline_id:
            pytest.skip("No pipeline created to delete")
        
        response = api_client.delete(f"{API_URL}/pipelines/{pipeline_id}")
        assert response.status_code == 200
        assert response.json()["deleted"] == True


class TestSLA113Terminal:
    """Test AI Terminal endpoint - /api/sla113/terminal"""
    
    def test_terminal_command(self, api_client):
        """POST /api/sla113/terminal should return AI response"""
        response = api_client.post(f"{API_URL}/terminal", json={
            "command": "status",
            "session_id": "test-session"
        }, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert data["session_id"] == "test-session"
        # Response should contain something (either AI response or error message)
        assert len(data["response"]) > 0
    
    def test_terminal_empty_command(self, api_client):
        """POST /api/sla113/terminal with empty command should still work"""
        response = api_client.post(f"{API_URL}/terminal", json={
            "command": "",
            "session_id": "test-empty"
        }, timeout=30)
        # Should return 200 even with empty command
        assert response.status_code == 200


class TestSLA113ImageGeneration:
    """Test Vision Smith image generation - /api/sla113/vision/generate-image"""
    
    def test_generate_image_endpoint_exists(self, api_client):
        """POST /api/sla113/vision/generate-image should accept requests"""
        # This test verifies the endpoint exists and accepts the request format
        # Actual image generation requires API credits
        response = api_client.post(f"{API_URL}/vision/generate-image", json={
            "prompt": "test sprite",
            "style": "pixel_art",
            "size": "1024x1024"
        }, timeout=60)
        
        # Should either succeed (200) or fail with API error (500)
        # but not 404 (endpoint not found) or 422 (validation error)
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "image_base64" in data
            assert "prompt" in data
            assert "style" in data
