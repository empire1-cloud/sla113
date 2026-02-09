"""
Phase 4 Backend Tests: Auth + Team-Scoped Routes
Tests authentication, team management, and team-scoped pipelines/history endpoints.
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestAuthSignup:
    """Test POST /api/auth/signup - creates user and personal team"""
    
    def test_signup_creates_user_and_team(self):
        """Signup should create user and personal team"""
        unique_email = f"test_signup_{uuid.uuid4().hex[:8]}@example.com"
        payload = {
            "email": unique_email,
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "Signup"
        }
        response = requests.post(f"{BASE_URL}/api/auth/signup", json=payload)
        
        assert response.status_code == 200, f"Signup failed: {response.text}"
        data = response.json()
        
        # Verify tokens returned
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
        
        # Verify user data
        assert "user" in data
        assert data["user"]["email"] == unique_email.lower()
        assert data["user"]["first_name"] == "Test"
        assert data["user"]["last_name"] == "Signup"
        
        # Verify personal team created
        assert "current_team" in data
        assert data["current_team"]["type"] == "personal"
        assert data["current_team"]["role"] == "owner"
    
    def test_signup_duplicate_email_fails(self):
        """Signup with existing email should fail"""
        payload = {
            "email": "test@example.com",  # Existing user
            "password": "TestPass123!",
            "first_name": "Duplicate",
            "last_name": "User"
        }
        response = requests.post(f"{BASE_URL}/api/auth/signup", json=payload)
        
        assert response.status_code == 409, f"Expected 409, got {response.status_code}"


class TestAuthLogin:
    """Test POST /api/auth/login - returns tokens and user info"""
    
    def test_login_success(self):
        """Login with valid credentials returns tokens"""
        payload = {
            "email": "test@example.com",
            "password": "Test1234!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        
        # Verify tokens
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
        
        # Verify user data
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"
        assert "id" in data["user"]
        
        # Verify current_team
        assert "current_team" in data
        assert "id" in data["current_team"]
        assert "name" in data["current_team"]
        assert "role" in data["current_team"]
    
    def test_login_invalid_password(self):
        """Login with wrong password fails"""
        payload = {
            "email": "test@example.com",
            "password": "WrongPassword123!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self):
        """Login with non-existent email fails"""
        payload = {
            "email": "nonexistent@example.com",
            "password": "Test1234!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        
        assert response.status_code == 401


class TestAuthMe:
    """Test GET /api/auth/me - returns user with teams array"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test1234!"
        })
        return response.json()["access_token"]
    
    def test_me_returns_user_with_teams(self, auth_token):
        """GET /api/auth/me returns user info with teams"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify user fields
        assert "id" in data
        assert "email" in data
        assert data["email"] == "test@example.com"
        assert "first_name" in data
        assert "last_name" in data
        
        # Verify teams array
        assert "teams" in data
        assert isinstance(data["teams"], list)
        assert len(data["teams"]) > 0
        
        # Verify team structure
        team = data["teams"][0]
        assert "id" in team
        assert "name" in team
        assert "role" in team
    
    def test_me_without_auth_fails(self):
        """GET /api/auth/me without token returns 401"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        
        assert response.status_code == 401


class TestAuthRefresh:
    """Test POST /api/auth/refresh - rotates tokens"""
    
    def test_refresh_rotates_tokens(self):
        """Refresh token returns new token pair"""
        # First login to get tokens
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test1234!"
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh tokens
        response = requests.post(f"{BASE_URL}/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == 200, f"Refresh failed: {response.text}"
        data = response.json()
        
        # Verify new tokens returned
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        
        # New tokens should be different
        assert data["refresh_token"] != refresh_token
    
    def test_refresh_invalid_token_fails(self):
        """Refresh with invalid token fails"""
        response = requests.post(f"{BASE_URL}/api/auth/refresh", json={
            "refresh_token": "invalid_token"
        })
        
        assert response.status_code == 401


class TestTeams:
    """Test /api/teams endpoints"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers for test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test1234!"
        })
        data = response.json()
        return {
            "Authorization": f"Bearer {data['access_token']}",
            "X-Team-ID": data["current_team"]["id"]
        }
    
    def test_create_team(self, auth_headers):
        """POST /api/teams creates new team"""
        payload = {
            "name": f"TEST_Team_{uuid.uuid4().hex[:8]}",
            "type": "organization"
        }
        response = requests.post(f"{BASE_URL}/api/teams", json=payload, headers=auth_headers)
        
        assert response.status_code == 200, f"Create team failed: {response.text}"
        data = response.json()
        
        assert "id" in data
        assert data["name"] == payload["name"]
        assert data["type"] == "organization"
    
    def test_list_teams(self, auth_headers):
        """GET /api/teams returns user's teams"""
        response = requests.get(f"{BASE_URL}/api/teams", headers=auth_headers)
        
        assert response.status_code == 200, f"List teams failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify team structure
        team = data[0]
        assert "id" in team
        assert "name" in team
        assert "role" in team


class TestHistoryProtected:
    """Test /api/history endpoints (protected, team-scoped)"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers for test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test1234!"
        })
        data = response.json()
        return {
            "Authorization": f"Bearer {data['access_token']}",
            "X-Team-ID": data["current_team"]["id"]
        }
    
    def test_history_without_auth_returns_401(self):
        """GET /api/history without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/history")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_history_with_auth_returns_team_logs(self, auth_headers):
        """GET /api/history with auth returns team-scoped logs"""
        response = requests.get(f"{BASE_URL}/api/history", headers=auth_headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "logs" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["logs"], list)
    
    def test_history_log_creates_execution_log(self, auth_headers):
        """POST /api/history/log creates execution log with team context"""
        payload = {
            "engine": "TEST_engine",
            "endpoint": "/api/test",
            "method": "POST",
            "input_data": {"test": "data"},
            "output_data": {"result": "success"},
            "duration_ms": 100,
            "source": "api"
        }
        response = requests.post(f"{BASE_URL}/api/history/log", json=payload, headers=auth_headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data["status"] == "logged"
        assert "id" in data
    
    def test_history_stats_returns_team_stats(self, auth_headers):
        """GET /api/history/stats returns team execution statistics"""
        response = requests.get(f"{BASE_URL}/api/history/stats", headers=auth_headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify stats structure
        assert "total_executions" in data
        assert "success_count" in data
        assert "error_count" in data
        assert "success_rate" in data
        assert "avg_duration_ms" in data
        assert "engines" in data


class TestPipelinesProtected:
    """Test /api/pipelines endpoints (protected, team-scoped)"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers for test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test1234!"
        })
        data = response.json()
        return {
            "Authorization": f"Bearer {data['access_token']}",
            "X-Team-ID": data["current_team"]["id"]
        }
    
    def test_pipelines_without_auth_returns_401(self):
        """GET /api/pipelines without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/pipelines")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_pipelines_with_auth_returns_team_pipelines(self, auth_headers):
        """GET /api/pipelines with auth returns team-scoped pipelines"""
        response = requests.get(f"{BASE_URL}/api/pipelines", headers=auth_headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "pipelines" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["pipelines"], list)
    
    def test_create_pipeline_with_team_id(self, auth_headers):
        """POST /api/pipelines creates pipeline with team_id"""
        payload = {
            "name": f"TEST_Pipeline_{uuid.uuid4().hex[:8]}",
            "description": "Test pipeline for Phase 4",
            "steps": [
                {
                    "engine": "strategy_engine",
                    "config": {"goal": "$.input.goal"},
                    "order": 1
                }
            ],
            "is_template": False
        }
        response = requests.post(f"{BASE_URL}/api/pipelines", json=payload, headers=auth_headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "id" in data
        assert data["name"] == payload["name"]
        assert "team_id" in data
        assert "created_by" in data
    
    def test_get_pipeline_by_id(self, auth_headers):
        """GET /api/pipelines/{id} returns pipeline details"""
        # First create a pipeline
        create_payload = {
            "name": f"TEST_GetPipeline_{uuid.uuid4().hex[:8]}",
            "description": "Test get pipeline",
            "steps": [],
            "is_template": False
        }
        create_response = requests.post(f"{BASE_URL}/api/pipelines", json=create_payload, headers=auth_headers)
        pipeline_id = create_response.json()["id"]
        
        # Get pipeline by ID
        response = requests.get(f"{BASE_URL}/api/pipelines/{pipeline_id}", headers=auth_headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data["id"] == pipeline_id
        assert data["name"] == create_payload["name"]
    
    def test_update_pipeline(self, auth_headers):
        """PUT /api/pipelines/{id} updates pipeline"""
        # First create a pipeline
        create_payload = {
            "name": f"TEST_UpdatePipeline_{uuid.uuid4().hex[:8]}",
            "description": "Original description",
            "steps": [],
            "is_template": False
        }
        create_response = requests.post(f"{BASE_URL}/api/pipelines", json=create_payload, headers=auth_headers)
        pipeline_id = create_response.json()["id"]
        
        # Update pipeline
        update_payload = {
            "name": f"TEST_UpdatedPipeline_{uuid.uuid4().hex[:8]}",
            "description": "Updated description"
        }
        response = requests.put(f"{BASE_URL}/api/pipelines/{pipeline_id}", json=update_payload, headers=auth_headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data["name"] == update_payload["name"]
        assert data["description"] == update_payload["description"]
    
    def test_delete_pipeline_soft_delete(self, auth_headers):
        """DELETE /api/pipelines/{id} soft deletes pipeline"""
        # First create a pipeline
        create_payload = {
            "name": f"TEST_DeletePipeline_{uuid.uuid4().hex[:8]}",
            "description": "To be deleted",
            "steps": [],
            "is_template": False
        }
        create_response = requests.post(f"{BASE_URL}/api/pipelines", json=create_payload, headers=auth_headers)
        pipeline_id = create_response.json()["id"]
        
        # Delete pipeline
        response = requests.delete(f"{BASE_URL}/api/pipelines/{pipeline_id}", headers=auth_headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["message"] == "Pipeline deleted"
        
        # Verify pipeline is no longer accessible
        get_response = requests.get(f"{BASE_URL}/api/pipelines/{pipeline_id}", headers=auth_headers)
        assert get_response.status_code == 404


class TestTeamIsolation:
    """Test team isolation - User A cannot see User B's data"""
    
    @pytest.fixture
    def user_a_auth(self):
        """Get auth for User A (test@example.com)"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test1234!"
        })
        data = response.json()
        return {
            "Authorization": f"Bearer {data['access_token']}",
            "X-Team-ID": data["current_team"]["id"]
        }, data["current_team"]["id"]
    
    @pytest.fixture
    def user_b_auth(self):
        """Create and get auth for User B"""
        unique_email = f"test_userb_{uuid.uuid4().hex[:8]}@example.com"
        
        # Create User B
        signup_response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "TestPass123!",
            "first_name": "User",
            "last_name": "B"
        })
        
        if signup_response.status_code != 200:
            pytest.skip(f"Could not create User B: {signup_response.text}")
        
        data = signup_response.json()
        return {
            "Authorization": f"Bearer {data['access_token']}",
            "X-Team-ID": data["current_team"]["id"]
        }, data["current_team"]["id"]
    
    def test_user_cannot_see_other_team_pipelines(self, user_a_auth, user_b_auth):
        """User A cannot see User B's pipelines"""
        user_a_headers, team_a_id = user_a_auth
        user_b_headers, team_b_id = user_b_auth
        
        # User B creates a pipeline
        create_payload = {
            "name": f"TEST_UserB_Pipeline_{uuid.uuid4().hex[:8]}",
            "description": "User B's private pipeline",
            "steps": [],
            "is_template": False
        }
        create_response = requests.post(f"{BASE_URL}/api/pipelines", json=create_payload, headers=user_b_headers)
        assert create_response.status_code == 200
        pipeline_id = create_response.json()["id"]
        
        # User A tries to access User B's pipeline
        get_response = requests.get(f"{BASE_URL}/api/pipelines/{pipeline_id}", headers=user_a_headers)
        
        # Should return 404 (not found) because it's in a different team
        assert get_response.status_code == 404, f"User A should not see User B's pipeline"
    
    def test_user_cannot_see_other_team_history(self, user_a_auth, user_b_auth):
        """User A cannot see User B's execution history"""
        user_a_headers, team_a_id = user_a_auth
        user_b_headers, team_b_id = user_b_auth
        
        # User B creates an execution log
        log_payload = {
            "engine": "TEST_isolation_engine",
            "endpoint": "/api/test",
            "method": "POST",
            "input_data": {"secret": "user_b_data"},
            "duration_ms": 50,
            "source": "api"
        }
        log_response = requests.post(f"{BASE_URL}/api/history/log", json=log_payload, headers=user_b_headers)
        assert log_response.status_code == 200
        
        # User A gets their history
        history_response = requests.get(f"{BASE_URL}/api/history?engine=TEST_isolation_engine", headers=user_a_headers)
        assert history_response.status_code == 200
        
        # User A should not see User B's logs
        logs = history_response.json()["logs"]
        for log in logs:
            assert log.get("team_id") != team_b_id, "User A should not see User B's logs"


class TestXTeamIDHeader:
    """Test X-Team-ID header switches team context"""
    
    def test_x_team_id_switches_context(self):
        """X-Team-ID header changes team context"""
        # Login to get tokens
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test1234!"
        })
        data = login_response.json()
        access_token = data["access_token"]
        default_team_id = data["current_team"]["id"]
        
        # Create a new team
        create_team_response = requests.post(
            f"{BASE_URL}/api/teams",
            json={"name": f"TEST_SwitchTeam_{uuid.uuid4().hex[:8]}", "type": "organization"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert create_team_response.status_code == 200
        new_team_id = create_team_response.json()["id"]
        
        # Create pipeline in new team using X-Team-ID header
        pipeline_payload = {
            "name": f"TEST_NewTeamPipeline_{uuid.uuid4().hex[:8]}",
            "description": "Pipeline in new team",
            "steps": [],
            "is_template": False
        }
        create_pipeline_response = requests.post(
            f"{BASE_URL}/api/pipelines",
            json=pipeline_payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Team-ID": new_team_id
            }
        )
        assert create_pipeline_response.status_code == 200
        pipeline_data = create_pipeline_response.json()
        
        # Verify pipeline is in the new team
        assert pipeline_data["team_id"] == new_team_id
        
        # Verify pipeline is NOT visible in default team
        default_team_pipelines = requests.get(
            f"{BASE_URL}/api/pipelines",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Team-ID": default_team_id
            }
        )
        pipeline_ids = [p["id"] for p in default_team_pipelines.json()["pipelines"]]
        assert pipeline_data["id"] not in pipeline_ids, "Pipeline should not be in default team"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
