"""
Phase 6 Backend Tests: Profile API and Role-based features

Tests:
- Profile API endpoints (/profile/me GET/PUT)
- Sessions API (/auth/sessions)
- Password change (/auth/password)
- Legacy endpoint removal (/api/engines/history should 404)
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "demo@test.com"
TEST_PASSWORD = "TestPass123"


class TestLegacyEndpointRemoval:
    """Verify legacy /api/engines/history is removed (returns 404)"""
    
    def test_legacy_engines_history_returns_404(self):
        """Legacy /api/engines/history should return 404"""
        response = requests.get(f"{BASE_URL}/api/engines/history")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✅ Legacy /api/engines/history correctly returns 404")


class TestProfileAPI:
    """Profile API endpoints tests"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Login and get auth token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user = login_response.json()["user"]
    
    def test_get_profile_me(self):
        """GET /profile/me returns user profile with teams"""
        response = requests.get(
            f"{BASE_URL}/api/profile/me",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify profile structure
        assert "id" in data
        assert "email" in data
        assert data["email"] == TEST_EMAIL
        assert "first_name" in data
        assert "last_name" in data
        assert "system_role" in data
        assert "created_at" in data
        assert "teams" in data
        assert isinstance(data["teams"], list)
        
        # Verify at least one team exists (personal team)
        assert len(data["teams"]) > 0
        team = data["teams"][0]
        assert "id" in team
        assert "name" in team
        assert "type" in team
        assert "role" in team
        
        print(f"✅ Profile GET returns correct structure with {len(data['teams'])} teams")
    
    def test_get_profile_unauthorized(self):
        """GET /profile/me without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/profile/me")
        assert response.status_code == 401
        print("✅ Profile GET correctly returns 401 without auth")
    
    def test_update_profile_name(self):
        """PUT /profile/me updates first and last name"""
        # Update profile
        response = requests.put(
            f"{BASE_URL}/api/profile/me",
            headers=self.headers,
            json={"first_name": "Demo", "last_name": "User"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Profile updated successfully"
        
        # Verify update persisted
        verify_response = requests.get(
            f"{BASE_URL}/api/profile/me",
            headers=self.headers
        )
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["first_name"] == "Demo"
        assert verify_data["last_name"] == "User"
        
        print("✅ Profile UPDATE persists name changes")
    
    def test_update_profile_no_data_returns_400(self):
        """PUT /profile/me with empty body returns 400"""
        response = requests.put(
            f"{BASE_URL}/api/profile/me",
            headers=self.headers,
            json={}
        )
        assert response.status_code == 400
        assert "No fields to update" in response.json().get("detail", "")
        print("✅ Profile UPDATE correctly returns 400 when no fields provided")


class TestSessionsAPI:
    """Sessions API endpoints tests"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Login and get auth token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert login_response.status_code == 200
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_sessions_list(self):
        """GET /auth/sessions returns list of active sessions"""
        response = requests.get(
            f"{BASE_URL}/api/auth/sessions",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0  # At least current session
        
        # Verify session structure
        session = data[0]
        assert "id" in session
        assert "ip_address" in session
        assert "created_at" in session
        assert "last_used_at" in session
        
        print(f"✅ Sessions GET returns {len(data)} active sessions")
    
    def test_get_sessions_unauthorized(self):
        """GET /auth/sessions without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/auth/sessions")
        assert response.status_code == 401
        print("✅ Sessions GET correctly returns 401 without auth")


class TestPasswordChangeAPI:
    """Password change endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Login and get auth token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert login_response.status_code == 200
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_change_password_wrong_current(self):
        """PUT /auth/password with wrong current password returns 400"""
        response = requests.put(
            f"{BASE_URL}/api/auth/password",
            headers=self.headers,
            json={
                "current_password": "WrongPassword123",
                "new_password": "NewPass1234!"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "incorrect" in data.get("detail", "").lower()
        print("✅ Password change correctly returns 400 for wrong current password")
    
    def test_change_password_unauthorized(self):
        """PUT /auth/password without auth returns 401"""
        response = requests.put(
            f"{BASE_URL}/api/auth/password",
            json={
                "current_password": "test",
                "new_password": "test"
            }
        )
        assert response.status_code == 401
        print("✅ Password change correctly returns 401 without auth")


class TestProtectedHistoryEndpoint:
    """Verify protected /api/history endpoint works"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Login and get auth token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert login_response.status_code == 200
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_protected_history_requires_auth(self):
        """GET /history without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/history")
        assert response.status_code == 401
        print("✅ Protected /api/history correctly returns 401 without auth")
    
    def test_protected_history_with_auth(self):
        """GET /history with auth works"""
        response = requests.get(
            f"{BASE_URL}/api/history",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total" in data
        print(f"✅ Protected /api/history returns {data['total']} logs with auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
