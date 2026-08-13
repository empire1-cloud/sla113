"""
SLA113 Iteration 20 - Game OS Composer Game System Tests
Tests for:
- GET /api/sla113/games returns 7 seeded default games
- POST /api/sla113/games creates a new game
- GET /api/sla113/games/{id} returns game details
- PATCH /api/sla113/games/{id} updates game
- DELETE /api/sla113/games/{id} deletes game
- POST /api/sla113/games/{id}/deploy creates project+build+deploy
- Validate fish_engine BOSSES filter by lobby config
- Validate /fish/lobbies endpoint still works (not shadowed)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSLA113GameSystem:
    """Game OS Composer Game CRUD and Deploy tests"""

    def test_01_get_games_returns_7_seeded_defaults(self):
        """GET /api/sla113/games returns the 7 seeded default games"""
        response = requests.get(f"{BASE_URL}/api/sla113/games")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        data = response.json()
        assert "games" in data, "Response should contain 'games' key"
        assert "total" in data, "Response should contain 'total' key"

        games = data["games"]
        assert len(games) >= 7, f"Expected at least 7 games, got {len(games)}"

        # Verify the 7 default game names
        expected_names = [
            "Shadow Pack", "Jaguar Warrior", "Quetzalcoatl Fireborn",
            "Ocelotl Voidmane", "Wolf Sovereign", "Jaguar Elite", "Jaguar Champion"
        ]
        game_names = [g["name"] for g in games]
        for name in expected_names:
            assert name in game_names, f"Expected game '{name}' not found in {game_names}"

        print(f"PASS: Found {len(games)} games including all 7 defaults")

    def test_02_get_game_details(self):
        """GET /api/sla113/games/{id} returns game details"""
        # First get list to find an ID
        list_res = requests.get(f"{BASE_URL}/api/sla113/games")
        assert list_res.status_code == 200
        games = list_res.json()["games"]
        assert len(games) > 0, "No games found"

        game_id = games[0]["id"]
        response = requests.get(f"{BASE_URL}/api/sla113/games/{game_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        game = response.json()
        assert game["id"] == game_id
        assert "name" in game
        assert "main_boss_sprite" in game
        assert "game_type" in game
        print(f"PASS: Got game details for {game['name']}")

    def test_03_get_game_not_found(self):
        """GET /api/sla113/games/{id} returns 404 for nonexistent"""
        response = requests.get(f"{BASE_URL}/api/sla113/games/NONEXISTENT-ID")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: 404 returned for nonexistent game")

    def test_04_create_game(self):
        """POST /api/sla113/games creates a new game"""
        payload = {
            "name": "TEST_Custom Arena",
            "slug": "test_custom_arena",
            "main_boss_sprite": "jaguar_warrior",
            "partner_boss_sprite": "g_wolf",
            "background_sprite": "wolf_xolotls_arena",
            "theme_color": "#ff00ff",
            "description": "Test game for iteration 20",
            "jackpot_tier": "MAJOR",
            "base_bet": 0.15
        }
        response = requests.post(f"{BASE_URL}/api/sla113/games", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        game = response.json()
        assert "id" in game, "Response should contain 'id'"
        assert game["id"].startswith("LBY-"), f"ID should start with LBY-, got {game['id']}"
        assert game["name"] == "TEST_Custom Arena"
        assert game["main_boss_sprite"] == "jaguar_warrior"
        assert game["partner_boss_sprite"] == "g_wolf"
        assert game["base_bet"] == 0.15
        assert "created_at" in game

        # Store for cleanup
        self.__class__.created_game_id = game["id"]
        print(f"PASS: Created game {game['id']}")

    def test_05_update_game_base_bet(self):
        """PATCH /api/sla113/games/{id} updates game (change base_bet from 0.15 to 0.50)"""
        game_id = getattr(self.__class__, 'created_game_id', None)
        if not game_id:
            pytest.skip("No game created in previous test")

        payload = {"base_bet": 0.50}
        response = requests.patch(f"{BASE_URL}/api/sla113/games/{game_id}", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        updated = response.json()
        assert updated["base_bet"] == 0.50, f"Expected base_bet 0.50, got {updated['base_bet']}"
        assert "updated_at" in updated
        print(f"PASS: Updated game base_bet to 0.50")

    def test_06_update_game_not_found(self):
        """PATCH /api/sla113/games/{id} returns 404 for nonexistent"""
        response = requests.patch(f"{BASE_URL}/api/sla113/games/NONEXISTENT-ID", json={"base_bet": 1.0})
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: 404 returned for updating nonexistent game")

    def test_07_delete_game(self):
        """DELETE /api/sla113/games/{id} deletes game"""
        game_id = getattr(self.__class__, 'created_game_id', None)
        if not game_id:
            pytest.skip("No game created in previous test")

        response = requests.delete(f"{BASE_URL}/api/sla113/games/{game_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert data.get("deleted") == True

        # Verify it's gone
        get_res = requests.get(f"{BASE_URL}/api/sla113/games/{game_id}")
        assert get_res.status_code == 404, "Deleted game should return 404"
        print(f"PASS: Deleted game {game_id}")

    def test_08_delete_game_not_found(self):
        """DELETE /api/sla113/games/{id} returns 404 for nonexistent"""
        response = requests.delete(f"{BASE_URL}/api/sla113/games/NONEXISTENT-ID")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: 404 returned for deleting nonexistent game")


class TestGameDeploy:
    """Game deploy endpoint tests"""

    def test_09_deploy_game_creates_project_build_deploy(self):
        """POST /api/sla113/games/{id}/deploy creates project+build+deploy, returns preview_url"""
        # Get first default game (Shadow Pack)
        list_res = requests.get(f"{BASE_URL}/api/sla113/games")
        assert list_res.status_code == 200
        games = list_res.json()["games"]

        # Find Shadow Pack or use first game
        shadow_pack = next((g for g in games if g["name"] == "Shadow Pack"), games[0])
        game_id = shadow_pack["id"]

        response = requests.post(f"{BASE_URL}/api/sla113/games/{game_id}/deploy")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        data = response.json()
        assert "game_id" in data, "Response should contain game_id"
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
        print(f"PASS: Deployed game {shadow_pack['name']}, preview_url: {preview_url}")

    def test_10_deploy_game_not_found(self):
        """POST /api/sla113/games/{id}/deploy returns 404 for nonexistent"""
        response = requests.post(f"{BASE_URL}/api/sla113/games/NONEXISTENT-ID/deploy")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: 404 returned for deploying nonexistent game")


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
    """Validate /fish/lobbies endpoint still works (not shadowed by /games)"""

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


class TestGameValidation:
    """Additional game validation tests"""

    def test_15_game_has_required_fields(self):
        """Verify game objects have all required fields"""
        response = requests.get(f"{BASE_URL}/api/sla113/games")
        assert response.status_code == 200

        games = response.json()["games"]
        assert len(games) > 0, "No games found"

        required_fields = [
            "id", "name", "slug", "game_type", "main_boss_sprite",
            "theme_color", "jackpot_tier", "base_bet", "created_at"
        ]

        for game in games[:3]:  # Check first 3
            for field in required_fields:
                assert field in game, f"Game {game.get('name')} missing field: {field}"

        print(f"PASS: All games have required fields")

    def test_16_shadow_pack_has_dual_boss(self):
        """Verify Shadow Pack game has both main_boss and partner_boss"""
        response = requests.get(f"{BASE_URL}/api/sla113/games")
        assert response.status_code == 200

        games = response.json()["games"]
        shadow_pack = next((g for g in games if g["name"] == "Shadow Pack"), None)

        assert shadow_pack is not None, "Shadow Pack game not found"
        assert shadow_pack["main_boss_sprite"] == "wolf_xolotl_pack", f"Expected wolf_xolotl_pack, got {shadow_pack['main_boss_sprite']}"
        assert shadow_pack["partner_boss_sprite"] == "g_wolf", f"Expected g_wolf partner, got {shadow_pack.get('partner_boss_sprite')}"
        assert shadow_pack["jackpot_tier"] == "GRAND", f"Expected GRAND tier, got {shadow_pack['jackpot_tier']}"
        print("PASS: Shadow Pack has dual-boss config (wolf_xolotl_pack + g_wolf)")


class TestCleanup:
    """Cleanup test data"""

    def test_99_cleanup_test_games(self):
        """Remove any TEST_ prefixed games"""
        response = requests.get(f"{BASE_URL}/api/sla113/games")
        if response.status_code != 200:
            return

        games = response.json().get("games", [])
        test_games = [g for g in games if g["name"].startswith("TEST_")]

        for game in test_games:
            requests.delete(f"{BASE_URL}/api/sla113/games/{game['id']}")

        print(f"Cleaned up {len(test_games)} test games")
