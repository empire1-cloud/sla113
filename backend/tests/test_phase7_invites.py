"""
Phase 7: Team Invitation System Tests
Tests invite CRUD, validation, acceptance, and signup/login integration flows.
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

# Test credentials
TEST_USER_EMAIL = "demo@test.com"
TEST_USER_PASSWORD = "TestPass123"


@pytest.fixture(scope="module")
def auth_session():
    """Get authenticated session with demo user"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    # Login with demo user
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    
    if response.status_code != 200:
        pytest.skip(f"Login failed: {response.text}")
    
    data = response.json()
    token = data.get("token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    # Store user info for later
    session.user_info = data.get("user", {})
    session.token = token
    
    return session


@pytest.fixture(scope="module")
def team_id(auth_session):
    """Get or create a team for invite testing"""
    # Get user's teams
    response = auth_session.get(f"{BASE_URL}/api/teams")
    assert response.status_code == 200
    
    teams = response.json()
    if teams:
        # Use first team where user is owner or admin
        for team in teams:
            if team.get("role") in ["owner", "admin"]:
                return team["id"]
    
    # Create a team if none exists
    response = auth_session.post(f"{BASE_URL}/api/teams", json={
        "name": "Test Invite Team",
        "type": "organization"
    })
    
    if response.status_code == 201 or response.status_code == 200:
        return response.json().get("id")
    
    pytest.skip("Could not get or create team for testing")


class TestInviteCreation:
    """Tests for POST /api/teams/{team_id}/invites"""
    
    def test_create_invite_success(self, auth_session, team_id):
        """Create invite with valid email and role"""
        unique_email = f"test_invite_{uuid.uuid4().hex[:8]}@example.com"
        
        response = auth_session.post(f"{BASE_URL}/api/teams/{team_id}/invites", json={
            "email": unique_email,
            "role": "member"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "invite_id" in data, "Response should contain invite_id"
        assert "token" in data, "Response should contain token for testing"
        assert "expires_at" in data, "Response should contain expiration date"
        
        # Store token for later tests
        auth_session.last_invite_token = data["token"]
        auth_session.last_invite_email = unique_email
        auth_session.last_invite_id = data["invite_id"]
    
    def test_create_admin_invite(self, auth_session, team_id):
        """Create invite with admin role"""
        unique_email = f"test_admin_{uuid.uuid4().hex[:8]}@example.com"
        
        response = auth_session.post(f"{BASE_URL}/api/teams/{team_id}/invites", json={
            "email": unique_email,
            "role": "admin"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "invite_id" in data
        
    def test_create_invite_duplicate_email(self, auth_session, team_id):
        """Cannot create duplicate invite for same email"""
        unique_email = f"test_dup_{uuid.uuid4().hex[:8]}@example.com"
        
        # First invite
        response1 = auth_session.post(f"{BASE_URL}/api/teams/{team_id}/invites", json={
            "email": unique_email,
            "role": "member"
        })
        assert response1.status_code == 200
        
        # Second invite same email - should fail
        response2 = auth_session.post(f"{BASE_URL}/api/teams/{team_id}/invites", json={
            "email": unique_email,
            "role": "member"
        })
        assert response2.status_code == 400, f"Expected 400 for duplicate, got {response2.status_code}"
        assert "already" in response2.json().get("detail", "").lower()


class TestInviteList:
    """Tests for GET /api/teams/{team_id}/invites"""
    
    def test_list_pending_invites(self, auth_session, team_id):
        """Get list of pending invites for team"""
        response = auth_session.get(f"{BASE_URL}/api/teams/{team_id}/invites")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        invites = response.json()
        assert isinstance(invites, list), "Response should be a list"
        
        # Should have at least one invite from previous tests
        if invites:
            invite = invites[0]
            assert "id" in invite
            assert "email" in invite
            assert "role" in invite
            assert "invited_by_name" in invite
            assert "created_at" in invite
            assert "expires_at" in invite


class TestInviteValidation:
    """Tests for GET /api/invites/validate/{token} (public endpoint)"""
    
    def test_validate_valid_token(self, auth_session, team_id):
        """Validate a valid invite token"""
        # First create an invite
        unique_email = f"test_validate_{uuid.uuid4().hex[:8]}@example.com"
        
        create_response = auth_session.post(f"{BASE_URL}/api/teams/{team_id}/invites", json={
            "email": unique_email,
            "role": "member"
        })
        assert create_response.status_code == 200
        token = create_response.json()["token"]
        
        # Validate token (public endpoint - no auth needed)
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/invites/validate/{token}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("valid") is True, "Token should be valid"
        assert data.get("email") == unique_email, "Email should match"
        assert data.get("role") == "member", "Role should match"
        assert data.get("team_name") is not None, "Team name should be present"
        assert data.get("invited_by_name") is not None, "Inviter name should be present"
    
    def test_validate_invalid_token(self):
        """Invalid token returns valid=False with error"""
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/invites/validate/invalid_token_12345")
        
        assert response.status_code == 200, f"Expected 200 even for invalid token, got {response.status_code}"
        
        data = response.json()
        assert data.get("valid") is False, "Invalid token should return valid=False"
        assert data.get("error") is not None, "Should have error message"


class TestInviteRevoke:
    """Tests for DELETE /api/teams/{team_id}/invites/{invite_id}"""
    
    def test_revoke_invite(self, auth_session, team_id):
        """Revoke a pending invite"""
        # First create an invite to revoke
        unique_email = f"test_revoke_{uuid.uuid4().hex[:8]}@example.com"
        
        create_response = auth_session.post(f"{BASE_URL}/api/teams/{team_id}/invites", json={
            "email": unique_email,
            "role": "member"
        })
        assert create_response.status_code == 200
        invite_id = create_response.json()["invite_id"]
        token = create_response.json()["token"]
        
        # Revoke the invite
        response = auth_session.delete(f"{BASE_URL}/api/teams/{team_id}/invites/{invite_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify token is now invalid
        session = requests.Session()
        validate_response = session.get(f"{BASE_URL}/api/invites/validate/{token}")
        assert validate_response.status_code == 200
        assert validate_response.json().get("valid") is False, "Revoked invite should be invalid"
    
    def test_revoke_nonexistent_invite(self, auth_session, team_id):
        """Attempting to revoke non-existent invite returns 404"""
        fake_invite_id = "6000000000000000000000ff"  # Valid ObjectId format
        
        response = auth_session.delete(f"{BASE_URL}/api/teams/{team_id}/invites/{fake_invite_id}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestInviteAccept:
    """Tests for POST /api/teams/invites/accept"""
    
    def test_accept_invite_wrong_email(self, auth_session, team_id):
        """Cannot accept invite sent to different email"""
        # Create invite for a different email
        different_email = f"other_user_{uuid.uuid4().hex[:8]}@example.com"
        
        create_response = auth_session.post(f"{BASE_URL}/api/teams/{team_id}/invites", json={
            "email": different_email,
            "role": "member"
        })
        assert create_response.status_code == 200
        token = create_response.json()["token"]
        
        # Try to accept with demo user (different email)
        response = auth_session.post(f"{BASE_URL}/api/teams/invites/accept", json={
            "token": token
        })
        
        assert response.status_code == 403, f"Expected 403 for wrong email, got {response.status_code}"
        assert "different email" in response.json().get("detail", "").lower()
    
    def test_accept_invalid_token(self, auth_session):
        """Cannot accept with invalid token"""
        response = auth_session.post(f"{BASE_URL}/api/teams/invites/accept", json={
            "token": "invalid_token_xyz123"
        })
        
        assert response.status_code == 400, f"Expected 400 for invalid token, got {response.status_code}"


class TestUnauthorizedAccess:
    """Tests for unauthorized/unauthenticated access"""
    
    def test_create_invite_no_auth(self):
        """Cannot create invite without authentication"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        response = session.post(f"{BASE_URL}/api/teams/123/invites", json={
            "email": "test@example.com",
            "role": "member"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_list_invites_no_auth(self):
        """Cannot list invites without authentication"""
        session = requests.Session()
        
        response = session.get(f"{BASE_URL}/api/teams/123/invites")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_revoke_invite_no_auth(self):
        """Cannot revoke invite without authentication"""
        session = requests.Session()
        
        response = session.delete(f"{BASE_URL}/api/teams/123/invites/456")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_accept_invite_no_auth(self):
        """Cannot accept invite without authentication"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        response = session.post(f"{BASE_URL}/api/teams/invites/accept", json={
            "token": "some_token"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestEmailCheck:
    """Tests for GET /api/invites/check-email/{token}/{email}"""
    
    def test_check_email_match(self, auth_session, team_id):
        """Check if email matches invite"""
        # Create invite
        unique_email = f"test_check_{uuid.uuid4().hex[:8]}@example.com"
        
        create_response = auth_session.post(f"{BASE_URL}/api/teams/{team_id}/invites", json={
            "email": unique_email,
            "role": "member"
        })
        assert create_response.status_code == 200
        token = create_response.json()["token"]
        
        # Check with matching email
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/invites/check-email/{token}/{unique_email}")
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("matches") is True
    
    def test_check_email_no_match(self, auth_session, team_id):
        """Check email that doesn't match invite"""
        # Create invite
        unique_email = f"test_nomatch_{uuid.uuid4().hex[:8]}@example.com"
        
        create_response = auth_session.post(f"{BASE_URL}/api/teams/{team_id}/invites", json={
            "email": unique_email,
            "role": "member"
        })
        assert create_response.status_code == 200
        token = create_response.json()["token"]
        
        # Check with different email
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/invites/check-email/{token}/other@example.com")
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("matches") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
