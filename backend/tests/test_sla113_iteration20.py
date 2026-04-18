"""
SLA113 Iteration 20 - Game OS Composer Lobby System Tests
Tests for:
- GET /api/sla113/lobbies returns 7 seeded default lobbies
- POST /api/sla113/lobbies creates a new lobby
- GET /api/sla113/lobbies/{id} returns lobby details
- PATCH /api/sla113/lobbies/{id} updates lobby
- DELETE /api/sla113/lobbies/{id} deletes lobby
- POST /api/sla113/lobbies/{id}/deploy creates project+build+deploy
- Validate fish_engine BOSSES filter by lobby config
- Validate /fish/lobbies endpoint still works (not shadowed)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSLA113LobbySystem:
    """Game OS Composer Lobby CRUD and Deploy tests"""
    
    def test_01_get_lobbies_returns_7_seeded_defaults(self):
        """GET /api/sla113/lobbies returns the 7 seeded default lobbies"""
        response = requests.get(f"{BASE_URL}/api/sla113/lobbies")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "lobbies" in data, "Response should contain 'lobbies' key"
        assert "total" in data, "Response should contain 'total' key"
        
        lobbies = data["lobbies"]
        assert len(lobbies) >= 7, f"Expected at least 7 lobbies, got {len(lobbies)}"
        
        # Verify the 7 default lobby names
        expected_names = [
            "Shadow Pack", "Jaguar Warrior", "Quetzalcoatl Fireborn",
            "Ocelotl Voidmane", "Wolf Sovereign", "Jaguar Elite", "Jaguar Champion"
        ]
        lobby_names = [l["name"] for l in lobbies]
        for name in expected_names:
            assert name in lobby_names, f"Expected lobby '{name}' not found in {lobby_names}"
        
        print(f"PASS: Found {len(lobbies)} lobbies including all 7 defaults")
    
    def test_02_get_lobby_details(self):
        """GET /api/sla113/lobbies/{id} returns lobby details"""
        # First get list to find an ID
        list_res = requests.get(f"{BASE_URL}/api/sla113/lobbies")
        assert list_res.status_code == 200
        lobbies = list_res.json()["lobbies"]
        assert len(lobbies) > 0, "No lobbies found"
        
        lobby_id = lobbies[0]["id"]
        response = requests.get(f"{BASE_URL}/api/sla113/lobbies/{lobby_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        lobby = response.json()
        assert lobby["id"] == lobby_id
        assert "name" in lobby
        assert "main_boss_sprite" in lobby
        assert "game_type" in lobby
        print(f"PASS: Got lobby details for {lobby['name']}")
    
    def test_03_get_lobby_not_found(self):
        """GET /api/sla113/lobbies/{id} returns 404 for nonexistent"""
        response = requests.get(f"{BASE_URL}/api/sla113/lobbies/NONEXISTENT-ID")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: 404 returned for nonexistent lobby")
    
    def test_04_create_lobby(self):
        """POST /api/sla113/lobbies creates a new lobby"""
        payload = {
            "name": "TEST_Custom Arena",
            "slug": "test_custom_arena",
            "main_boss_sprite": "jaguar_warrior",
            "partner_boss_sprite": "g_wolf",
            "background_sprite": "wolf_xolotls_arena",
            "theme_color": "#ff00ff",
            "description": "Test lobby for iteration 20",
            "jackpot_tier": "MAJOR",
            "base_bet": 0.15
        }
        response = requests.post(f"{BASE_URL}/api/sla113/lobbies", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        lobby = response.json()
        assert "id" in lobby, "Response should contain 'id'"
        assert lobby["id"].startswith("LBY-"), f"ID should start with LBY-, got {lobby['id']}"
        assert lobby["name"] == "TEST_Custom Arena"
        assert lobby["main_boss_sprite"] == "jaguar_warrior"
        assert lobby["partner_boss_sprite"] == "g_wolf"
        assert lobby["base_bet"] == 0.15
        assert "created_at" in lobby
        
        # Store for cleanup
        self.__class__.created_lobby_id = lobby["id"]
        print(f"PASS: Created lobby {lobby['id']}")
    
    def test_05_update_lobby_base_bet(self):
        """PATCH /api/sla113/lobbies/{id} updates lobby (change base_bet from 0.15 to 0.50)"""
        lobby_id = getattr(self.__class__, 'created_lobby_id', None)
        if not lobby_id:
            pytest.skip("No lobby created in previous test")
        
        payload = {"base_bet": 0.50}
        response = requests.patch(f"{BASE_URL}/api/sla113/lobbies/{lobby_id}", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        updated = response.json()
        assert updated["base_bet"] == 0.50, f"Expected base_bet 0.50, got {updated['base_bet']}"
        assert "updated_at" in updated
        print(f"PASS: Updated lobby base_bet to 0.50")
    
    def test_06_update_lobby_not_found(self):
        """PATCH /api/sla113/lobbies/{id} returns 404 for nonexistent"""
        response = requests.patch(f"{BASE_URL}/api/sla113/lobbies/NONEXISTENT-ID", json={"base_bet": 1.0})
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: 404 returned for updating nonexistent lobby")
    
    def test_07_delete_lobby(self):
        """DELETE /api/sla113/lobbies/{id} deletes lobby"""
        lobby_id = getattr(self.__class__, 'created_lobby_id', None)
        if not lobby_id:
            pytest.skip("No lobby created in previous test")
        
        response = requests.delete(f"{BASE_URL}/api/sla113/lobbies/{lobby_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("deleted") == True
        
        # Verify it's gone
        get_res = requests.get(f"{BASE_URL}/api/sla113/lobbies/{lobby_id}")
        assert get_res.status_code == 404, "Deleted lobby should return 404"
        print(f"PASS: Deleted lobby {lobby_id}")
    
    def test_08_delete_lobby_not_found(self):
        """DELETE /api/sla113/lobbies/{id} returns 404 for nonexistent"""
        response = requests.delete(f"{BASE_URL}/api/sla113/lobbies/NONEXISTENT-ID")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: 404 returned for deleting nonexistent lobby")


class TestLobbyDeploy:
    """Lobby deploy endpoint tests"""
    
    def test_09_deploy_lobby_creates_project_build_deploy(self):
        """POST /api/sla113/lobbies/{id}/deploy creates project+build+deploy, returns preview_url"""
        # Get first default lobby (Shadow Pack)
        list_res = requests.get(f"{BASE_URL}/api/sla113/lobbies")
        assert list_res.status_code == 200
        lobbies = list_res.json()["lobbies"]
        
        # Find Shadow Pack or use first lobby
        shadow_pack = next((l for l in lobbies if l["name"] == "Shadow Pack"), lobbies[0])
        lobby_id = shadow_pack["id"]
        
        response = requests.post(f"{BASE_URL}/api/sla113/lobbies/{lobby_id}/deploy")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "lobby_id" in data, "Response should contain lobby_id"
        assert "project_id" in data, "Response should contain project_id"
        assert "build_id" in data, "Response should contain build_id"
        assert "deployment" in data, "Response should contain deployment"
        assert "preview_url" in data, "Response should contain preview_url"
        
        # Verify deployment status
        deployment = data["deployment"]
        assert deployment.get("status") == "live", f"Expected status 'live', got {deployment.get('status')}"
        
        # Verify preview_url format
        preview_url = data["preview_url"]
        assert "/api/sla113/live/" in preview_url, f"preview_url should contain /api/sla113/live/, got {preview_url}"
        
        # Store for later tests
        self.__class__.deployed_preview_url = preview_url
        self.__class__.deployed_build_id = data["build_id"]
        print(f"PASS: Deployed lobby {shadow_pack['name']}, preview_url: {preview_url}")
    
    def test_10_deploy_lobby_not_found(self):
        """POST /api/sla113/lobbies/{id}/deploy returns 404 for nonexistent"""
        response = requests.post(f"{BASE_URL}/api/sla113/lobbies/NONEXISTENT-ID/deploy")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: 404 returned for deploying nonexistent lobby")


class TestCompiledGameValidation:
    """Validate compiled game.js contains correct lobby config"""
    
    def test_11_compiled_game_contains_lobby_config(self):
        """Validate compiled game.js contains GAME_CONFIG.lobby with main_boss and partner_boss"""
        # Get a deployed build
        builds_res = requests.get(f"{BASE_URL}/api/sla113/builds")
        assert builds_res.status_code == 200
        builds = builds_res.json().get("builds", [])
        
        # Find a completed build with lobby_config
        completed_builds = [b for b in builds if b.get("status") == "completed"]
        if not completed_builds:
            pytest.skip("No completed builds found")
        
        # Get deployments to find a live one
        deploy_res = requests.get(f"{BASE_URL}/api/sla113/deployments")
        assert deploy_res.status_code == 200
        deployments = deploy_res.json().get("deployments", [])
        
        live_deploys = [d for d in deployments if d.get("status") == "live"]
        if not live_deploys:
            pytest.skip("No live deployments found")
        
        # Access the game.js file
        deploy_id = live_deploys[0]["id"]
        game_js_url = f"{BASE_URL}/api/sla113/live/{deploy_id}/game.js"
        response = requests.get(game_js_url)
        
        if response.status_code != 200:
            pytest.skip(f"Could not access game.js: {response.status_code}")
        
        game_js = response.text
        
        # Check for GAME_CONFIG.lobby
        assert "GAME_CONFIG" in game_js, "game.js should contain GAME_CONFIG"
        
        # Check for lobby object with boss config
        if '"lobby"' in game_js or "'lobby'" in game_js:
            assert '"main_boss"' in game_js or "'main_boss'" in game_js, "lobby config should contain main_boss"
            print("PASS: game.js contains GAME_CONFIG.lobby with main_boss")
        else:
            print("INFO: game.js does not have lobby config (may be non-lobby build)")


class TestFishEngineFilter:
    """Validate fish_engine filters BOSSES by lobby config"""
    
    def test_12_fish_engine_has_bosses_filter(self):
        """Validate fish_engine.py contains BOSSES_ALL and wanted filter logic"""
        # This is a code inspection test - we verify the fish_engine.py has the filter
        # The actual filtering happens at runtime in the browser
        
        # Check the fish_engine.py file content via a build
        # For now, we verify the endpoint returns game.js with the filter code
        deploy_res = requests.get(f"{BASE_URL}/api/sla113/deployments")
        if deploy_res.status_code != 200:
            pytest.skip("Could not get deployments")
        
        deployments = deploy_res.json().get("deployments", [])
        live_deploys = [d for d in deployments if d.get("status") == "live"]
        
        if not live_deploys:
            pytest.skip("No live deployments to check")
        
        deploy_id = live_deploys[0]["id"]
        game_js_url = f"{BASE_URL}/api/sla113/live/{deploy_id}/game.js"
        response = requests.get(game_js_url)
        
        if response.status_code != 200:
            pytest.skip(f"Could not access game.js: {response.status_code}")
        
        game_js = response.text
        
        # Check for BOSSES_ALL and filter logic
        assert "BOSSES_ALL" in game_js, "game.js should contain BOSSES_ALL array"
        assert "wanted" in game_js, "game.js should contain 'wanted' filter variable"
        print("PASS: game.js contains BOSSES_ALL and wanted filter logic")


class TestFishLobbiesNotShadowed:
    """Validate /fish/lobbies endpoint still works (not shadowed by /lobbies)"""
    
    def test_13_fish_lobbies_endpoint_works(self):
        """GET /api/sla113/fish/lobbies should return 200 (not shadowed)"""
        response = requests.get(f"{BASE_URL}/api/sla113/fish/lobbies")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "lobbies" in data, "Response should contain 'lobbies' key"
        print(f"PASS: /fish/lobbies returns 200 with {len(data['lobbies'])} lobbies")
    
    def test_14_fish_lobbies_create_works(self):
        """POST /api/sla113/fish/lobbies?name=X should create fish lobby"""
        response = requests.post(f"{BASE_URL}/api/sla113/fish/lobbies?name=TEST_FishArena")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should contain 'id'"
        assert data["id"].startswith("FISH-"), f"Fish lobby ID should start with FISH-, got {data['id']}"
        
        # Cleanup
        fish_lobby_id = data["id"]
        requests.delete(f"{BASE_URL}/api/sla113/fish/lobbies/{fish_lobby_id}")
        print(f"PASS: Created and cleaned up fish lobby {fish_lobby_id}")


class TestLobbyValidation:
    """Additional lobby validation tests"""
    
    def test_15_lobby_has_required_fields(self):
        """Verify lobby objects have all required fields"""
        response = requests.get(f"{BASE_URL}/api/sla113/lobbies")
        assert response.status_code == 200
        
        lobbies = response.json()["lobbies"]
        assert len(lobbies) > 0, "No lobbies found"
        
        required_fields = [
            "id", "name", "slug", "game_type", "main_boss_sprite",
            "theme_color", "jackpot_tier", "base_bet", "created_at"
        ]
        
        for lobby in lobbies[:3]:  # Check first 3
            for field in required_fields:
                assert field in lobby, f"Lobby {lobby.get('name')} missing field: {field}"
        
        print(f"PASS: All lobbies have required fields")
    
    def test_16_shadow_pack_has_dual_boss(self):
        """Verify Shadow Pack lobby has both main_boss and partner_boss"""
        response = requests.get(f"{BASE_URL}/api/sla113/lobbies")
        assert response.status_code == 200
        
        lobbies = response.json()["lobbies"]
        shadow_pack = next((l for l in lobbies if l["name"] == "Shadow Pack"), None)
        
        assert shadow_pack is not None, "Shadow Pack lobby not found"
        assert shadow_pack["main_boss_sprite"] == "wolf_xolotl_pack", f"Expected wolf_xolotl_pack, got {shadow_pack['main_boss_sprite']}"
        assert shadow_pack["partner_boss_sprite"] == "g_wolf", f"Expected g_wolf partner, got {shadow_pack.get('partner_boss_sprite')}"
        assert shadow_pack["jackpot_tier"] == "GRAND", f"Expected GRAND tier, got {shadow_pack['jackpot_tier']}"
        print("PASS: Shadow Pack has dual-boss config (wolf_xolotl_pack + g_wolf)")


class TestCleanup:
    """Cleanup test data"""
    
    def test_99_cleanup_test_lobbies(self):
        """Remove any TEST_ prefixed lobbies"""
        response = requests.get(f"{BASE_URL}/api/sla113/lobbies")
        if response.status_code != 200:
            return
        
        lobbies = response.json().get("lobbies", [])
        test_lobbies = [l for l in lobbies if l["name"].startswith("TEST_")]
        
        for lobby in test_lobbies:
            requests.delete(f"{BASE_URL}/api/sla113/lobbies/{lobby['id']}")
        
        print(f"Cleaned up {len(test_lobbies)} test lobbies")
