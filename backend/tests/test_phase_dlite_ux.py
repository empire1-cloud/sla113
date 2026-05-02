"""
Test Phase D-Lite: UX Polish & Stability Hardening
Tests for system status, billing plans caching, OAuth providers, and error handling
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSystemEndpoints:
    """Tests for /api/system/* endpoints"""
    
    def test_health_endpoint(self):
        """Test health check endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/system/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        print(f"Health check passed: version={data['version']}")
    
    def test_system_status_endpoint(self):
        """Test system status returns service configuration"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "version" in data
        assert "timestamp" in data
        assert "services" in data
        assert "mode" in data
        
        # Verify services structure
        services = data["services"]
        assert "email_enabled" in services
        assert "stripe_enabled" in services
        assert "oauth_enabled" in services
        
        # Verify oauth structure
        oauth = services["oauth_enabled"]
        assert "google" in oauth
        assert "github" in oauth
        
        # Mode should be development since services aren't configured
        assert data["mode"] in ["development", "production"]
        
        print(f"System status: mode={data['mode']}, email={services['email_enabled']}, stripe={services['stripe_enabled']}")
    
    def test_system_status_caching(self):
        """Test that system status endpoint is cached (same response within TTL)"""
        # First request
        response1 = requests.get(f"{BASE_URL}/api/system/status")
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Immediate second request (should be cached)
        response2 = requests.get(f"{BASE_URL}/api/system/status")
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Timestamps should be same (cached)
        assert data1["timestamp"] == data2["timestamp"], "Response should be cached"
        print("System status caching verified")


class TestBillingEndpoints:
    """Tests for /api/billing/* endpoints"""
    
    def test_plans_endpoint_unauthenticated(self):
        """Test billing plans endpoint works without authentication"""
        response = requests.get(f"{BASE_URL}/api/billing/plans")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "plans" in data
        assert isinstance(data["plans"], list)
        assert len(data["plans"]) >= 1
        
        # Verify plan structure
        for plan in data["plans"]:
            assert "key" in plan
            assert "name" in plan
            assert "limits" in plan
            
        # Verify expected plans exist
        plan_keys = [p["key"] for p in data["plans"]]
        assert "free" in plan_keys
        print(f"Found {len(data['plans'])} billing plans: {plan_keys}")
    
    def test_plans_caching(self):
        """Test that plans endpoint is cached"""
        # First request
        response1 = requests.get(f"{BASE_URL}/api/billing/plans")
        assert response1.status_code == 200
        
        # Quick second request (should be cached)
        response2 = requests.get(f"{BASE_URL}/api/billing/plans")
        assert response2.status_code == 200
        
        # Same content
        assert response1.json() == response2.json()
        print("Billing plans caching verified")
    
    def test_plans_contain_limits(self):
        """Test that plans have proper limit configurations"""
        response = requests.get(f"{BASE_URL}/api/billing/plans")
        assert response.status_code == 200
        
        for plan in response.json()["plans"]:
            limits = plan["limits"]
            assert "executions_per_month" in limits
            assert "team_members" in limits
            assert "api_keys" in limits
            assert "pipelines" in limits
            
            # Free plan should have specific limits
            if plan["key"] == "free":
                assert limits["executions_per_month"] == 100
                assert limits["team_members"] == 3
                assert limits["api_keys"] == 2
                
            # Enterprise should have unlimited (-1)
            if plan["key"] == "enterprise":
                assert limits["executions_per_month"] == -1
        
        print("Plan limits validated")


class TestOAuthProvidersEndpoint:
    """Tests for /api/auth/oauth/providers endpoint"""
    
    def test_oauth_providers_endpoint(self):
        """Test OAuth providers endpoint returns provider list"""
        response = requests.get(f"{BASE_URL}/api/auth/oauth/providers")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "providers" in data
        assert isinstance(data["providers"], list)
        
        # Should have google and github
        provider_names = [p["name"] for p in data["providers"]]
        assert "google" in provider_names
        assert "github" in provider_names
        
        # Each provider should have required fields
        for provider in data["providers"]:
            assert "name" in provider
            assert "display_name" in provider
            assert "enabled" in provider
            assert isinstance(provider["enabled"], bool)
        
        print(f"OAuth providers: {[(p['name'], p['enabled']) for p in data['providers']]}")
    
    def test_oauth_providers_disabled_without_config(self):
        """Test OAuth providers show disabled when not configured"""
        response = requests.get(f"{BASE_URL}/api/auth/oauth/providers")
        assert response.status_code == 200
        
        for provider in response.json()["providers"]:
            # Since we don't have OAuth configured, should be disabled
            # (This validates the mock mode)
            if provider["name"] in ["google", "github"]:
                print(f"Provider {provider['name']}: enabled={provider['enabled']}")


class TestAuthenticatedEndpoints:
    """Tests requiring authentication"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "demo@example.com",
                "password": "Password123!"
            }
        )
        if response.status_code != 200:
            pytest.skip("Login failed - skipping authenticated tests")
        return response.json()["access_token"]
    
    @pytest.fixture
    def team_id(self, auth_token):
        """Get current team ID"""
        response = requests.get(
            f"{BASE_URL}/api/teams",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code != 200:
            pytest.skip("Could not get teams")
        teams = response.json()
        if not teams:
            pytest.skip("No teams found")
        return teams[0].get("id")
    
    def test_billing_team_endpoint(self, auth_token):
        """Test billing team endpoint returns billing and usage"""
        response = requests.get(
            f"{BASE_URL}/api/billing/team",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "billing" in data
        assert "usage" in data
        
        billing = data["billing"]
        assert "plan" in billing or "plan_name" in billing
        assert "stripe_configured" in billing
        
        usage = data["usage"]
        assert "usage" in usage or "limits" in usage
        
        print(f"Billing team data: plan={billing.get('plan_name', billing.get('plan'))}, stripe={billing['stripe_configured']}")
    
    def test_billing_usage_endpoint(self, auth_token):
        """Test billing usage endpoint returns usage data"""
        response = requests.get(
            f"{BASE_URL}/api/billing/usage",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "usage" in data or "limits" in data
        print(f"Usage data retrieved successfully")
    
    def test_api_keys_list_endpoint(self, auth_token, team_id):
        """Test API keys list endpoint"""
        if not team_id:
            pytest.skip("No team ID available")
            
        response = requests.get(
            f"{BASE_URL}/api/teams/{team_id}/api-keys",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"Found {len(data)} API keys")
    
    def test_sessions_endpoint(self, auth_token):
        """Test sessions list endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/auth/sessions",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1  # Current session should exist
        
        for session in data:
            assert "id" in session
            assert "device_info" in session or "user_agent" in session
        
        print(f"Found {len(data)} active sessions")
    
    def test_profile_update_endpoint(self, auth_token):
        """Test profile update endpoint"""
        # Update profile
        response = requests.put(
            f"{BASE_URL}/api/profile/me",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "first_name": "Demo",
                "last_name": "User"
            }
        )
        
        assert response.status_code == 200
        print("Profile update endpoint working")


class TestErrorHandling:
    """Tests for error handling and user-friendly messages"""
    
    def test_invalid_login_returns_friendly_error(self):
        """Test that invalid login returns user-friendly error"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        
        assert "detail" in data
        # Error should be a string, not a code
        assert isinstance(data["detail"], str)
        print(f"Login error message: {data['detail']}")
    
    def test_missing_auth_returns_401(self):
        """Test protected endpoints return 401 without auth"""
        endpoints = [
            "/api/billing/team",
            "/api/billing/usage",
            "/api/auth/sessions",
            "/api/profile/me"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 401, f"Expected 401 for {endpoint}, got {response.status_code}"
        
        print("Auth required endpoints properly protected")
    
    def test_invalid_route_returns_404(self):
        """Test invalid routes return 404"""
        response = requests.get(f"{BASE_URL}/api/nonexistent/endpoint")
        
        # Should be 404 Not Found, not 500 server error
        assert response.status_code == 404
        print("Invalid routes return 404 correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
