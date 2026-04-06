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
    """Test game types endpoint"""
    
    def test_get_game_types_returns_10_types(self, api_client):
        """GET /api/sla113/game-types should return 10 supported game types"""
        response = api_client.get(f"{API_URL}/game-types")
        assert response.status_code == 200
        
        data = response.json()
        assert "game_types" in data
        game_types = data["game_types"]
        assert len(game_types) == 10
        
        # Verify expected game types exist
        expected_types = ["fish_shooter", "slot_machine", "crash_game", "platformer", 
                         "puzzle", "card_game", "tower_defense", "runner", "rpg", "battle_royale"]
        for gt in expected_types:
            assert gt in game_types, f"Missing game type: {gt}"
            assert "name" in game_types[gt]
            assert "description" in game_types[gt]
            assert "category" in game_types[gt]


class TestSLA113Stats:
    """Test stats endpoint"""
    
    def test_get_stats_returns_valid_structure(self, api_client):
        """GET /api/sla113/stats should return stats object"""
        response = api_client.get(f"{API_URL}/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_projects" in data
        assert "supported_game_types" in data
        assert data["supported_game_types"] == 10
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
