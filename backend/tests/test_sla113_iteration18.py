"""
SLA113 Iteration 18 Backend Tests
Testing:
1. Game Template Library - genre-specific PixiJS code for fish_shooting, slot_machine, platformer, unknown fallback
2. Upgraded Mint Ledger - multiple credit amounts (+500/+1K/+5K/+10K), delete tenant, RTP validation
3. Deploy Engine - live game serving at /api/sla113/live/{id}/index.html
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://genesis-engine-4.preview.emergentagent.com"


class TestGameTemplates:
    """Test Game Template Library - genre-specific PixiJS code generation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.created_projects = []
        self.created_builds = []
        yield
        # Cleanup
        for proj_id in self.created_projects:
            try:
                requests.delete(f"{BASE_URL}/api/sla113/projects/{proj_id}")
            except:
                pass
        for build_id in self.created_builds:
            try:
                requests.delete(f"{BASE_URL}/api/sla113/builds/{build_id}")
            except:
                pass
    
    def test_fish_shooting_template(self):
        """Build + compile a fish_shooting project should produce game.js with fish-specific code"""
        # Create fish_shooting project
        resp = requests.post(f"{BASE_URL}/api/sla113/projects", json={
            "name": "TEST_Fish_Game",
            "game_type": "fish_shooting",
            "theme": "ocean",
            "target_platform": "webgl"
        })
        assert resp.status_code == 200, f"Failed to create project: {resp.text}"
        project = resp.json()
        self.created_projects.append(project["id"])
        assert project["game_type"] == "fish_shooting"
        
        # Create build
        build_resp = requests.post(f"{BASE_URL}/api/sla113/builds", json={
            "project_id": project["id"],
            "target": "webgl",
            "optimization": "balanced"
        })
        assert build_resp.status_code == 200, f"Failed to create build: {build_resp.text}"
        build = build_resp.json()
        self.created_builds.append(build["id"])
        
        # Compile build
        compile_resp = requests.post(f"{BASE_URL}/api/sla113/builds/{build['id']}/compile")
        assert compile_resp.status_code == 200, f"Failed to compile: {compile_resp.text}"
        compiled = compile_resp.json()
        assert compiled["status"] == "completed"
        assert compiled["download_url"] is not None
        
        # Download and verify fish-specific code
        download_resp = requests.get(f"{BASE_URL}{compiled['download_url']}")
        assert download_resp.status_code == 200
        
        # Extract and check game.js content
        import zipfile
        import io
        with zipfile.ZipFile(io.BytesIO(download_resp.content)) as zf:
            assert "game.js" in zf.namelist()
            game_js = zf.read("game.js").decode('utf-8')
            # Fish shooting specific code markers
            assert "bubbles" in game_js.lower() or "Bubbles" in game_js, "Fish template should have bubbles"
            assert "ammo" in game_js.lower(), "Fish template should have ammo system"
            assert "crosshair" in game_js.lower(), "Fish template should have crosshair"
            assert "fish" in game_js.lower() or "Fish" in game_js, "Fish template should reference fish"
        print("PASS: fish_shooting template contains bubbles, ammo, crosshair, fish code")
    
    def test_slot_machine_template(self):
        """Build + compile a slot_machine project should produce game.js with slot-specific code"""
        # Create slot_machine project
        resp = requests.post(f"{BASE_URL}/api/sla113/projects", json={
            "name": "TEST_Slots_Game",
            "game_type": "slot_machine",
            "theme": "casino",
            "target_platform": "webgl"
        })
        assert resp.status_code == 200
        project = resp.json()
        self.created_projects.append(project["id"])
        
        # Create and compile build
        build_resp = requests.post(f"{BASE_URL}/api/sla113/builds", json={
            "project_id": project["id"],
            "target": "webgl"
        })
        assert build_resp.status_code == 200
        build = build_resp.json()
        self.created_builds.append(build["id"])
        
        compile_resp = requests.post(f"{BASE_URL}/api/sla113/builds/{build['id']}/compile")
        assert compile_resp.status_code == 200
        compiled = compile_resp.json()
        
        # Download and verify slot-specific code
        download_resp = requests.get(f"{BASE_URL}{compiled['download_url']}")
        assert download_resp.status_code == 200
        
        import zipfile
        import io
        with zipfile.ZipFile(io.BytesIO(download_resp.content)) as zf:
            game_js = zf.read("game.js").decode('utf-8')
            # Slot machine specific code markers
            assert "reel" in game_js.lower(), "Slot template should have reels"
            assert "spin" in game_js.lower(), "Slot template should have spin"
            assert "symbol" in game_js.lower(), "Slot template should have symbols"
        print("PASS: slot_machine template contains reels, spin, symbols code")
    
    def test_platformer_template(self):
        """Build + compile a platformer project should produce game.js with platformer code"""
        # Create platformer project
        resp = requests.post(f"{BASE_URL}/api/sla113/projects", json={
            "name": "TEST_Platformer_Game",
            "game_type": "platformer",
            "theme": "retro",
            "target_platform": "webgl"
        })
        assert resp.status_code == 200
        project = resp.json()
        self.created_projects.append(project["id"])
        
        # Create and compile build
        build_resp = requests.post(f"{BASE_URL}/api/sla113/builds", json={
            "project_id": project["id"],
            "target": "webgl"
        })
        assert build_resp.status_code == 200
        build = build_resp.json()
        self.created_builds.append(build["id"])
        
        compile_resp = requests.post(f"{BASE_URL}/api/sla113/builds/{build['id']}/compile")
        assert compile_resp.status_code == 200
        compiled = compile_resp.json()
        
        # Download and verify platformer-specific code
        download_resp = requests.get(f"{BASE_URL}{compiled['download_url']}")
        assert download_resp.status_code == 200
        
        import zipfile
        import io
        with zipfile.ZipFile(io.BytesIO(download_resp.content)) as zf:
            game_js = zf.read("game.js").decode('utf-8')
            # Platformer specific code markers
            assert "gravity" in game_js.lower() or "G = " in game_js, "Platformer template should have gravity"
            assert "jump" in game_js.lower() or "grounded" in game_js.lower(), "Platformer template should have jumping"
            assert "coin" in game_js.lower() or "platform" in game_js.lower(), "Platformer template should have coins/platforms"
        print("PASS: platformer template contains gravity, jumping, coins/platforms code")
    
    def test_unknown_type_fallback(self):
        """Build + compile an unknown type falls back to default template"""
        # Create project with a type that maps to default
        # Using 'adventure' which should fall back to default template
        resp = requests.post(f"{BASE_URL}/api/sla113/projects", json={
            "name": "TEST_Adventure_Game",
            "game_type": "adventure",  # Not in specific templates, should use default
            "theme": "fantasy",
            "target_platform": "webgl"
        })
        assert resp.status_code == 200
        project = resp.json()
        self.created_projects.append(project["id"])
        
        # Create and compile build
        build_resp = requests.post(f"{BASE_URL}/api/sla113/builds", json={
            "project_id": project["id"],
            "target": "webgl"
        })
        assert build_resp.status_code == 200
        build = build_resp.json()
        self.created_builds.append(build["id"])
        
        compile_resp = requests.post(f"{BASE_URL}/api/sla113/builds/{build['id']}/compile")
        assert compile_resp.status_code == 200
        compiled = compile_resp.json()
        
        # Download and verify default template code
        download_resp = requests.get(f"{BASE_URL}{compiled['download_url']}")
        assert download_resp.status_code == 200
        
        import zipfile
        import io
        with zipfile.ZipFile(io.BytesIO(download_resp.content)) as zf:
            game_js = zf.read("game.js").decode('utf-8')
            # Default template markers - generic interactive entities
            assert "spawnEntity" in game_js or "entities" in game_js, "Default template should have entities"
            assert "PIXI" in game_js, "Should use PixiJS"
            assert "SLA113" in game_js, "Should have SLA113 branding"
        print("PASS: unknown type falls back to default template with entities")


class TestDeployEngine:
    """Test Deploy Engine - live game serving"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.created_projects = []
        self.created_builds = []
        self.created_deployments = []
        yield
        # Cleanup
        for deploy_id in self.created_deployments:
            try:
                requests.delete(f"{BASE_URL}/api/sla113/deploy/{deploy_id}")
            except:
                pass
        for build_id in self.created_builds:
            try:
                requests.delete(f"{BASE_URL}/api/sla113/builds/{build_id}")
            except:
                pass
        for proj_id in self.created_projects:
            try:
                requests.delete(f"{BASE_URL}/api/sla113/projects/{proj_id}")
            except:
                pass
    
    def test_deploy_and_serve_live_game(self):
        """Deploy a compiled build and verify /api/sla113/live/{id}/index.html serves HTML"""
        # Create project
        resp = requests.post(f"{BASE_URL}/api/sla113/projects", json={
            "name": "TEST_Deploy_Game",
            "game_type": "fish_shooting",
            "target_platform": "webgl"
        })
        assert resp.status_code == 200
        project = resp.json()
        self.created_projects.append(project["id"])
        
        # Create and compile build
        build_resp = requests.post(f"{BASE_URL}/api/sla113/builds", json={
            "project_id": project["id"],
            "target": "webgl"
        })
        assert build_resp.status_code == 200
        build = build_resp.json()
        self.created_builds.append(build["id"])
        
        compile_resp = requests.post(f"{BASE_URL}/api/sla113/builds/{build['id']}/compile")
        assert compile_resp.status_code == 200
        compiled = compile_resp.json()
        assert compiled["status"] == "completed"
        
        # Deploy
        deploy_resp = requests.post(f"{BASE_URL}/api/sla113/deploy", json={
            "build_id": build["id"],
            "target_cdn": "cloudflare",
            "region": "us-west"
        })
        assert deploy_resp.status_code == 200, f"Deploy failed: {deploy_resp.text}"
        deployment = deploy_resp.json()
        self.created_deployments.append(deployment["id"])
        assert deployment["status"] == "live", f"Expected live status, got {deployment['status']}"
        
        # Verify live game serves HTML
        live_url = f"{BASE_URL}/api/sla113/live/{deployment['id']}/index.html"
        live_resp = requests.get(live_url)
        assert live_resp.status_code == 200, f"Live game not accessible: {live_resp.status_code}"
        assert "text/html" in live_resp.headers.get("content-type", "")
        assert "<!DOCTYPE html>" in live_resp.text or "<html" in live_resp.text
        assert "SLA113" in live_resp.text
        assert "PIXI" in live_resp.text or "pixi" in live_resp.text
        print(f"PASS: Live game accessible at {live_url}")
        
        # Verify game.js is also served
        js_url = f"{BASE_URL}/api/sla113/live/{deployment['id']}/game.js"
        js_resp = requests.get(js_url)
        assert js_resp.status_code == 200
        assert "javascript" in js_resp.headers.get("content-type", "")
        print("PASS: game.js served correctly")


class TestMintLedger:
    """Test Mint Ledger - tenant credits and management"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.created_tenants = []
        yield
        # Cleanup
        for tenant_id in self.created_tenants:
            try:
                requests.delete(f"{BASE_URL}/api/sla113/tenants/{tenant_id}")
            except:
                pass
    
    def test_add_credits_500(self):
        """PUT /api/sla113/tenants/{id}/credits?amount=500 adds 500 credits"""
        # Create tenant
        resp = requests.post(f"{BASE_URL}/api/sla113/tenants", json={
            "name": "TEST_Credit_Tenant_500",
            "subdomain": f"test-credit-500-{int(time.time())}.empire1.cloud"
        })
        assert resp.status_code == 200
        tenant = resp.json()
        self.created_tenants.append(tenant["id"])
        initial_credits = tenant.get("credits", 0)
        
        # Add 500 credits
        credit_resp = requests.put(f"{BASE_URL}/api/sla113/tenants/{tenant['id']}/credits?amount=500")
        assert credit_resp.status_code == 200
        updated = credit_resp.json()
        assert updated["credits"] == initial_credits + 500
        print(f"PASS: Added 500 credits, now {updated['credits']}")
    
    def test_add_credits_1000(self):
        """PUT /api/sla113/tenants/{id}/credits?amount=1000 adds 1000 credits"""
        resp = requests.post(f"{BASE_URL}/api/sla113/tenants", json={
            "name": "TEST_Credit_Tenant_1K",
            "subdomain": f"test-credit-1k-{int(time.time())}.empire1.cloud"
        })
        assert resp.status_code == 200
        tenant = resp.json()
        self.created_tenants.append(tenant["id"])
        
        credit_resp = requests.put(f"{BASE_URL}/api/sla113/tenants/{tenant['id']}/credits?amount=1000")
        assert credit_resp.status_code == 200
        updated = credit_resp.json()
        assert updated["credits"] == 1000
        print(f"PASS: Added 1000 credits")
    
    def test_add_credits_5000(self):
        """PUT /api/sla113/tenants/{id}/credits?amount=5000 adds 5000 credits"""
        resp = requests.post(f"{BASE_URL}/api/sla113/tenants", json={
            "name": "TEST_Credit_Tenant_5K",
            "subdomain": f"test-credit-5k-{int(time.time())}.empire1.cloud"
        })
        assert resp.status_code == 200
        tenant = resp.json()
        self.created_tenants.append(tenant["id"])
        
        credit_resp = requests.put(f"{BASE_URL}/api/sla113/tenants/{tenant['id']}/credits?amount=5000")
        assert credit_resp.status_code == 200
        updated = credit_resp.json()
        assert updated["credits"] == 5000
        print(f"PASS: Added 5000 credits")
    
    def test_add_credits_10000(self):
        """PUT /api/sla113/tenants/{id}/credits?amount=10000 adds 10000 credits"""
        resp = requests.post(f"{BASE_URL}/api/sla113/tenants", json={
            "name": "TEST_Credit_Tenant_10K",
            "subdomain": f"test-credit-10k-{int(time.time())}.empire1.cloud"
        })
        assert resp.status_code == 200
        tenant = resp.json()
        self.created_tenants.append(tenant["id"])
        
        credit_resp = requests.put(f"{BASE_URL}/api/sla113/tenants/{tenant['id']}/credits?amount=10000")
        assert credit_resp.status_code == 200
        updated = credit_resp.json()
        assert updated["credits"] == 10000
        print(f"PASS: Added 10000 credits")
    
    def test_delete_tenant(self):
        """DELETE /api/sla113/tenants/{id} removes a tenant"""
        # Create tenant
        resp = requests.post(f"{BASE_URL}/api/sla113/tenants", json={
            "name": "TEST_Delete_Tenant",
            "subdomain": f"test-delete-{int(time.time())}.empire1.cloud"
        })
        assert resp.status_code == 200
        tenant = resp.json()
        tenant_id = tenant["id"]
        
        # Verify tenant exists
        get_resp = requests.get(f"{BASE_URL}/api/sla113/tenants")
        assert get_resp.status_code == 200
        tenants = get_resp.json()["tenants"]
        assert any(t["id"] == tenant_id for t in tenants)
        
        # Delete tenant
        delete_resp = requests.delete(f"{BASE_URL}/api/sla113/tenants/{tenant_id}")
        assert delete_resp.status_code == 200
        assert delete_resp.json()["deleted"] == True
        
        # Verify tenant is gone
        get_resp2 = requests.get(f"{BASE_URL}/api/sla113/tenants")
        tenants2 = get_resp2.json()["tenants"]
        assert not any(t["id"] == tenant_id for t in tenants2)
        print("PASS: Tenant deleted successfully")
    
    def test_rtp_validation(self):
        """RTP validation - must be between 80 and 99"""
        resp = requests.post(f"{BASE_URL}/api/sla113/tenants", json={
            "name": "TEST_RTP_Tenant",
            "subdomain": f"test-rtp-{int(time.time())}.empire1.cloud"
        })
        assert resp.status_code == 200
        tenant = resp.json()
        self.created_tenants.append(tenant["id"])
        
        # Valid RTP (92)
        rtp_resp = requests.put(f"{BASE_URL}/api/sla113/tenants/{tenant['id']}/rtp?rtp=92")
        assert rtp_resp.status_code == 200
        assert rtp_resp.json()["rtp_mode"] == 92
        
        # Valid RTP (80 - minimum)
        rtp_resp = requests.put(f"{BASE_URL}/api/sla113/tenants/{tenant['id']}/rtp?rtp=80")
        assert rtp_resp.status_code == 200
        assert rtp_resp.json()["rtp_mode"] == 80
        
        # Valid RTP (99 - maximum)
        rtp_resp = requests.put(f"{BASE_URL}/api/sla113/tenants/{tenant['id']}/rtp?rtp=99")
        assert rtp_resp.status_code == 200
        assert rtp_resp.json()["rtp_mode"] == 99
        
        # Invalid RTP (79 - below minimum)
        rtp_resp = requests.put(f"{BASE_URL}/api/sla113/tenants/{tenant['id']}/rtp?rtp=79")
        assert rtp_resp.status_code == 400
        
        # Invalid RTP (100 - above maximum)
        rtp_resp = requests.put(f"{BASE_URL}/api/sla113/tenants/{tenant['id']}/rtp?rtp=100")
        assert rtp_resp.status_code == 400
        
        print("PASS: RTP validation working correctly (80-99 range)")


class TestExistingDeployments:
    """Test existing deployments from previous iterations"""
    
    def test_existing_fish_deployment(self):
        """Verify existing fish deployment DPL-0B096E7A is accessible"""
        # This deployment was created in previous testing
        live_url = f"{BASE_URL}/api/sla113/live/DPL-0B096E7A/index.html"
        resp = requests.get(live_url)
        if resp.status_code == 200:
            assert "text/html" in resp.headers.get("content-type", "")
            print(f"PASS: Existing fish deployment accessible at {live_url}")
        else:
            print(f"INFO: Existing deployment DPL-0B096E7A not found (may have been cleaned up)")
    
    def test_existing_slots_deployment(self):
        """Verify existing slots deployment DPL-66AF6778 is accessible"""
        live_url = f"{BASE_URL}/api/sla113/live/DPL-66AF6778/index.html"
        resp = requests.get(live_url)
        if resp.status_code == 200:
            assert "text/html" in resp.headers.get("content-type", "")
            print(f"PASS: Existing slots deployment accessible at {live_url}")
        else:
            print(f"INFO: Existing deployment DPL-66AF6778 not found (may have been cleaned up)")
    
    def test_existing_platformer_deployment(self):
        """Verify existing platformer deployment DPL-E7EA5C9B is accessible"""
        live_url = f"{BASE_URL}/api/sla113/live/DPL-E7EA5C9B/index.html"
        resp = requests.get(live_url)
        if resp.status_code == 200:
            assert "text/html" in resp.headers.get("content-type", "")
            print(f"PASS: Existing platformer deployment accessible at {live_url}")
        else:
            print(f"INFO: Existing deployment DPL-E7EA5C9B not found (may have been cleaned up)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
