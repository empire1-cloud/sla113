"""
Phase A & B Tests: Identity & Access Layer + Billing & Usage Layer
Tests for:
- Password Reset Flow (request, validate, confirm)
- OAuth Providers endpoint
- Session Management (revoke all)
- Billing endpoints (team billing, plans, usage)
- API Keys CRUD operations
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "demo@test.com"
TEST_PASSWORD = "TestPass123"


class TestSetup:
    """Setup tests to verify configuration."""
    
    def test_backend_health(self):
        """Verify backend is running."""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Backend healthy: {data['status']}")


class TestPasswordReset:
    """Password reset flow tests (Phase A - Identity & Access)."""
    
    def test_password_reset_request_valid_email(self):
        """POST /api/auth/password-reset/request - Request password reset with valid email."""
        response = requests.post(
            f"{BASE_URL}/api/auth/password-reset/request",
            json={"email": TEST_EMAIL}
        )
        # Should always return success to prevent email enumeration
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "If an account exists" in data["message"]
        assert data.get("expires_in_minutes") == 15
        print(f"✓ Password reset request accepted: {data['message']}")
    
    def test_password_reset_request_unknown_email(self):
        """POST /api/auth/password-reset/request - Request with unknown email (still returns success)."""
        response = requests.post(
            f"{BASE_URL}/api/auth/password-reset/request",
            json={"email": "unknown_email_xyz@nonexistent.com"}
        )
        # Should still return success to prevent email enumeration
        assert response.status_code == 200
        data = response.json()
        assert "If an account exists" in data.get("message", "")
        print("✓ Password reset for unknown email returns generic success (email enumeration protection)")
    
    def test_password_reset_request_invalid_email_format(self):
        """POST /api/auth/password-reset/request - Request with invalid email format."""
        response = requests.post(
            f"{BASE_URL}/api/auth/password-reset/request",
            json={"email": "not-an-email"}
        )
        assert response.status_code == 422  # Validation error
        print("✓ Invalid email format rejected with 422")
    
    def test_password_reset_validate_invalid_token(self):
        """GET /api/auth/password-reset/validate/{token} - Validate invalid token."""
        response = requests.get(
            f"{BASE_URL}/api/auth/password-reset/validate/invalid_token_xyz123"
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("valid") == False
        print("✓ Invalid token validation returns valid=false")
    
    def test_password_reset_confirm_invalid_token(self):
        """POST /api/auth/password-reset/confirm - Confirm with invalid token."""
        response = requests.post(
            f"{BASE_URL}/api/auth/password-reset/confirm",
            json={
                "token": "invalid_token_xyz123_abcdef",
                "new_password": "NewSecurePass123"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "Invalid" in data.get("detail", "") or "expired" in data.get("detail", "")
        print("✓ Invalid token confirmation rejected with 400")
    
    def test_password_reset_confirm_weak_password(self):
        """POST /api/auth/password-reset/confirm - Confirm with weak password."""
        response = requests.post(
            f"{BASE_URL}/api/auth/password-reset/confirm",
            json={
                "token": "some_token_here_for_testing",
                "new_password": "weak"  # Too short
            }
        )
        assert response.status_code == 422  # Validation error for weak password
        print("✓ Weak password rejected with 422")


class TestOAuthProviders:
    """OAuth providers endpoint tests (Phase A - Identity & Access)."""
    
    def test_get_oauth_providers(self):
        """GET /api/auth/oauth/providers - List available OAuth providers."""
        response = requests.get(f"{BASE_URL}/api/auth/oauth/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        providers = data["providers"]
        assert isinstance(providers, list)
        
        # Check provider structure
        for provider in providers:
            assert "name" in provider
            assert "display_name" in provider
            assert "enabled" in provider
        
        # Should have Google and GitHub
        provider_names = [p["name"] for p in providers]
        assert "google" in provider_names
        assert "github" in provider_names
        print(f"✓ OAuth providers returned: {[p['name'] for p in providers]}")
        
        # Check enabled status (should be false without credentials)
        for provider in providers:
            print(f"  - {provider['name']}: enabled={provider['enabled']}")


class TestSessionManagement:
    """Session management tests (Phase A - Identity & Access)."""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers by logging in."""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return {"Authorization": f"Bearer {data['access_token']}"}
    
    def test_revoke_all_sessions_requires_auth(self):
        """POST /api/auth/sessions/revoke-all - Requires authentication."""
        response = requests.post(f"{BASE_URL}/api/auth/sessions/revoke-all")
        assert response.status_code == 401
        print("✓ Revoke all sessions requires auth (401)")
    
    def test_revoke_all_sessions_authenticated(self, auth_headers):
        """POST /api/auth/sessions/revoke-all - Revoke all sessions except current."""
        response = requests.post(
            f"{BASE_URL}/api/auth/sessions/revoke-all",
            headers=auth_headers,
            params={"keep_current": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "count" in data
        print(f"✓ Revoked {data['count']} session(s), kept current")
    
    def test_list_sessions(self, auth_headers):
        """GET /api/auth/sessions - List active sessions."""
        response = requests.get(
            f"{BASE_URL}/api/auth/sessions",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            session = data[0]
            assert "id" in session
            assert "created_at" in session
            assert "last_used_at" in session
        print(f"✓ Listed {len(data)} active session(s)")


class TestBillingEndpoints:
    """Billing endpoints tests (Phase B - Billing & Usage)."""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers by logging in."""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return {"Authorization": f"Bearer {data['access_token']}"}
    
    def test_get_plans_public(self):
        """GET /api/billing/plans - List available plans (public)."""
        response = requests.get(f"{BASE_URL}/api/billing/plans")
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        plans = data["plans"]
        assert isinstance(plans, list)
        assert len(plans) >= 2  # At least free and pro
        
        # Check plan structure
        for plan in plans:
            assert "key" in plan
            assert "name" in plan
            assert "limits" in plan
            assert "features" in plan
        
        # Verify required plans exist
        plan_keys = [p["key"] for p in plans]
        assert "free" in plan_keys
        assert "pro" in plan_keys
        print(f"✓ Plans returned: {plan_keys}")
    
    def test_get_billing_status_public(self):
        """GET /api/billing/status - Get billing configuration status."""
        # Login first to get auth header
        login_res = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert login_res.status_code == 200
        headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}
        
        response = requests.get(f"{BASE_URL}/api/billing/status", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "stripe_configured" in data
        print(f"✓ Billing status: stripe_configured={data['stripe_configured']}")
    
    def test_get_team_billing_requires_auth(self):
        """GET /api/billing/team - Requires authentication."""
        response = requests.get(f"{BASE_URL}/api/billing/team")
        assert response.status_code == 401
        print("✓ Team billing requires auth (401)")
    
    def test_get_team_billing(self, auth_headers):
        """GET /api/billing/team - Get team billing info."""
        response = requests.get(
            f"{BASE_URL}/api/billing/team",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check billing info structure
        assert "billing" in data
        billing = data["billing"]
        assert "plan" in billing
        assert "plan_name" in billing
        assert "limits" in billing
        assert "features" in billing
        
        # Check usage info structure
        assert "usage" in data
        usage = data["usage"]
        assert "plan" in usage
        assert "limits" in usage
        
        print(f"✓ Team billing: plan={billing['plan']}, plan_name={billing['plan_name']}")
    
    def test_get_usage_requires_auth(self):
        """GET /api/billing/usage - Requires authentication."""
        response = requests.get(f"{BASE_URL}/api/billing/usage")
        assert response.status_code == 401
        print("✓ Usage endpoint requires auth (401)")
    
    def test_get_usage(self, auth_headers):
        """GET /api/billing/usage - Get team usage stats."""
        response = requests.get(
            f"{BASE_URL}/api/billing/usage",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "usage" in data
        usage = data["usage"]
        assert "executions_count" in usage
        
        assert "limits" in data
        limits = data["limits"]
        assert "executions_per_month" in limits
        
        assert "plan" in data
        print(f"✓ Usage: {usage['executions_count']} executions, plan={data['plan']}")


class TestAPIKeys:
    """API Keys CRUD tests (Phase B - Usage Layer)."""
    
    @pytest.fixture
    def auth_context(self):
        """Get auth headers and team_id by logging in."""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return {
            "headers": {"Authorization": f"Bearer {data['access_token']}"},
            "team_id": data.get("current_team", {}).get("id")
        }
    
    def test_list_api_keys_requires_auth(self):
        """GET /api/teams/{team_id}/api-keys - Requires authentication."""
        response = requests.get(f"{BASE_URL}/api/teams/some-team-id/api-keys")
        assert response.status_code == 401
        print("✓ List API keys requires auth (401)")
    
    def test_list_api_keys(self, auth_context):
        """GET /api/teams/{team_id}/api-keys - List API keys."""
        team_id = auth_context["team_id"]
        assert team_id, "No team_id found"
        
        response = requests.get(
            f"{BASE_URL}/api/teams/{team_id}/api-keys",
            headers=auth_context["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Listed {len(data)} API key(s)")
    
    def test_create_api_key_requires_auth(self):
        """POST /api/teams/{team_id}/api-keys - Requires authentication."""
        response = requests.post(
            f"{BASE_URL}/api/teams/some-team-id/api-keys",
            json={"name": "Test Key"}
        )
        assert response.status_code == 401
        print("✓ Create API key requires auth (401)")
    
    def test_create_api_key(self, auth_context):
        """POST /api/teams/{team_id}/api-keys - Create new API key."""
        team_id = auth_context["team_id"]
        assert team_id, "No team_id found"
        
        key_name = f"TEST_Phase9_Key_{datetime.now().strftime('%H%M%S')}"
        
        response = requests.post(
            f"{BASE_URL}/api/teams/{team_id}/api-keys",
            headers=auth_context["headers"],
            json={"name": key_name}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "id" in data
        assert "name" in data
        assert "key" in data  # Only shown once!
        assert "key_prefix" in data
        assert "created_at" in data
        
        # Verify key format
        assert data["key"].startswith("hic_")
        assert data["name"] == key_name
        
        # Store key_id for cleanup
        auth_context["created_key_id"] = data["id"]
        auth_context["created_key_name"] = data["name"]
        
        print(f"✓ Created API key: {data['key_prefix']}...")
        return data
    
    def test_create_and_verify_api_key(self, auth_context):
        """POST then GET - Create API key and verify it appears in list."""
        team_id = auth_context["team_id"]
        assert team_id, "No team_id found"
        
        key_name = f"TEST_Verify_Key_{datetime.now().strftime('%H%M%S')}"
        
        # Create
        create_res = requests.post(
            f"{BASE_URL}/api/teams/{team_id}/api-keys",
            headers=auth_context["headers"],
            json={"name": key_name}
        )
        assert create_res.status_code == 200
        created_key = create_res.json()
        
        # Verify in list
        list_res = requests.get(
            f"{BASE_URL}/api/teams/{team_id}/api-keys",
            headers=auth_context["headers"]
        )
        assert list_res.status_code == 200
        keys = list_res.json()
        
        key_ids = [k["id"] for k in keys]
        assert created_key["id"] in key_ids
        print(f"✓ Created key appears in list")
        
        # Cleanup - revoke the key
        revoke_res = requests.delete(
            f"{BASE_URL}/api/teams/{team_id}/api-keys/{created_key['id']}",
            headers=auth_context["headers"]
        )
        assert revoke_res.status_code == 200
        print(f"✓ Cleaned up test key")
    
    def test_revoke_api_key_requires_auth(self):
        """DELETE /api/teams/{team_id}/api-keys/{id} - Requires authentication."""
        response = requests.delete(
            f"{BASE_URL}/api/teams/some-team-id/api-keys/some-key-id"
        )
        assert response.status_code == 401
        print("✓ Revoke API key requires auth (401)")
    
    def test_revoke_api_key(self, auth_context):
        """DELETE /api/teams/{team_id}/api-keys/{id} - Revoke API key."""
        team_id = auth_context["team_id"]
        assert team_id, "No team_id found"
        
        # First create a key to revoke
        key_name = f"TEST_Revoke_Key_{datetime.now().strftime('%H%M%S')}"
        create_res = requests.post(
            f"{BASE_URL}/api/teams/{team_id}/api-keys",
            headers=auth_context["headers"],
            json={"name": key_name}
        )
        assert create_res.status_code == 200
        created_key = create_res.json()
        
        # Revoke
        revoke_res = requests.delete(
            f"{BASE_URL}/api/teams/{team_id}/api-keys/{created_key['id']}",
            headers=auth_context["headers"]
        )
        assert revoke_res.status_code == 200
        data = revoke_res.json()
        assert "message" in data
        print(f"✓ Revoked API key: {data['message']}")
        
        # Verify no longer in active list
        list_res = requests.get(
            f"{BASE_URL}/api/teams/{team_id}/api-keys",
            headers=auth_context["headers"]
        )
        assert list_res.status_code == 200
        keys = list_res.json()
        key_ids = [k["id"] for k in keys]
        assert created_key["id"] not in key_ids
        print("✓ Revoked key no longer appears in list")
    
    def test_revoke_nonexistent_key(self, auth_context):
        """DELETE /api/teams/{team_id}/api-keys/{id} - Revoke non-existent key."""
        team_id = auth_context["team_id"]
        assert team_id, "No team_id found"
        
        response = requests.delete(
            f"{BASE_URL}/api/teams/{team_id}/api-keys/000000000000000000000000",
            headers=auth_context["headers"]
        )
        assert response.status_code == 404
        print("✓ Revoke non-existent key returns 404")
    
    def test_create_duplicate_name_key(self, auth_context):
        """POST /api/teams/{team_id}/api-keys - Duplicate name should fail."""
        team_id = auth_context["team_id"]
        assert team_id, "No team_id found"
        
        key_name = f"TEST_Duplicate_{datetime.now().strftime('%H%M%S')}"
        
        # Create first key
        create_res1 = requests.post(
            f"{BASE_URL}/api/teams/{team_id}/api-keys",
            headers=auth_context["headers"],
            json={"name": key_name}
        )
        assert create_res1.status_code == 200
        created_key = create_res1.json()
        
        # Try to create duplicate
        create_res2 = requests.post(
            f"{BASE_URL}/api/teams/{team_id}/api-keys",
            headers=auth_context["headers"],
            json={"name": key_name}
        )
        # Could be 400 (duplicate name) or 429 (rate limit exceeded)
        assert create_res2.status_code in [400, 429]
        print(f"✓ Duplicate/rate-limit key rejected with {create_res2.status_code}")
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/teams/{team_id}/api-keys/{created_key['id']}",
            headers=auth_context["headers"]
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
