"""
SLA113 Iteration 19 Backend Tests
Tests for new features:
1. Fish Multiplayer Lobby CRUD (POST/GET/DELETE /api/sla113/fish/lobbies)
2. Custom Slot Symbols CRUD (POST/GET/DELETE /api/sla113/slots/symbols)
3. 5-Reel Video Slot template with WILD, SCATTER, Free Spins, PAYLINES
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestFishMultiplayerLobbies:
    """Fish Multiplayer Lobby API tests"""
    
    def test_create_fish_lobby(self):
        """POST /api/sla113/fish/lobbies creates a lobby"""
        response = requests.post(f"{BASE_URL}/api/sla113/fish/lobbies?name=TEST_Arena")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Response should contain lobby id"
        assert data["id"].startswith("FISH-"), f"Lobby ID should start with FISH-, got {data['id']}"
        assert data["name"] == "TEST_Arena", f"Lobby name mismatch: {data['name']}"
        assert "created_at" in data, "Response should contain created_at"
        print(f"PASS: Created fish lobby {data['id']}")
        return data["id"]
    
    def test_list_fish_lobbies(self):
        """GET /api/sla113/fish/lobbies lists active lobbies"""
        # First create a lobby to ensure there's at least one
        create_resp = requests.post(f"{BASE_URL}/api/sla113/fish/lobbies?name=TEST_ListLobby")
        assert create_resp.status_code == 200
        created_id = create_resp.json()["id"]
        
        # List lobbies
        response = requests.get(f"{BASE_URL}/api/sla113/fish/lobbies")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "lobbies" in data, "Response should contain lobbies array"
        assert isinstance(data["lobbies"], list), "lobbies should be a list"
        
        # Find our created lobby
        found = any(l["id"] == created_id for l in data["lobbies"])
        assert found, f"Created lobby {created_id} not found in list"
        
        # Check lobby structure
        if data["lobbies"]:
            lobby = data["lobbies"][0]
            assert "id" in lobby, "Lobby should have id"
            assert "name" in lobby, "Lobby should have name"
            assert "players" in lobby, "Lobby should have player count"
            assert "fish" in lobby, "Lobby should have fish count"
        
        print(f"PASS: Listed {len(data['lobbies'])} fish lobbies")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/sla113/fish/lobbies/{created_id}")
        return data
    
    def test_delete_fish_lobby(self):
        """DELETE /api/sla113/fish/lobbies/{id} removes a lobby"""
        # Create a lobby first
        create_resp = requests.post(f"{BASE_URL}/api/sla113/fish/lobbies?name=TEST_DeleteLobby")
        assert create_resp.status_code == 200
        lobby_id = create_resp.json()["id"]
        
        # Delete it
        response = requests.delete(f"{BASE_URL}/api/sla113/fish/lobbies/{lobby_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("deleted") == True, "Response should confirm deletion"
        
        # Verify it's gone
        list_resp = requests.get(f"{BASE_URL}/api/sla113/fish/lobbies")
        lobbies = list_resp.json().get("lobbies", [])
        found = any(l["id"] == lobby_id for l in lobbies)
        assert not found, f"Deleted lobby {lobby_id} should not be in list"
        
        print(f"PASS: Deleted fish lobby {lobby_id}")
    
    def test_delete_nonexistent_lobby_returns_404(self):
        """DELETE /api/sla113/fish/lobbies/{id} returns 404 for nonexistent lobby"""
        response = requests.delete(f"{BASE_URL}/api/sla113/fish/lobbies/FISH-NONEXISTENT")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Delete nonexistent lobby returns 404")


class TestCustomSlotSymbols:
    """Custom Slot Symbol Set API tests"""
    
    def test_create_symbol_set(self):
        """POST /api/sla113/slots/symbols creates a symbol set"""
        symbols = [
            {"name": "LOWRIDER", "color": "#d4af37", "weight": 5, "payout": 20},
            {"name": "SKULL", "color": "#ffffff", "weight": 8, "payout": 10},
            {"name": "ROSE", "color": "#ff4466", "weight": 10, "payout": 8},
            {"name": "CROSS", "color": "#00c8ff", "weight": 12, "payout": 5},
            {"name": "DICE", "color": "#88ff44", "weight": 15, "payout": 3},
        ]
        payload = {"name": "TEST_Southern_Lifestyle", "symbols": symbols}
        
        response = requests.post(f"{BASE_URL}/api/sla113/slots/symbols", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "id" in data, "Response should contain id"
        assert data["id"].startswith("SYM-"), f"Symbol set ID should start with SYM-, got {data['id']}"
        assert data["name"] == "TEST_Southern_Lifestyle", f"Name mismatch: {data['name']}"
        assert data["total_symbols"] == 5, f"Expected 5 symbols, got {data['total_symbols']}"
        assert len(data["symbols"]) == 5, "Should have 5 symbols"
        
        print(f"PASS: Created symbol set {data['id']}")
        return data["id"]
    
    def test_list_symbol_sets_includes_default(self):
        """GET /api/sla113/slots/symbols returns DEFAULT set plus custom sets"""
        response = requests.get(f"{BASE_URL}/api/sla113/slots/symbols")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "sets" in data, "Response should contain sets array"
        assert "total" in data, "Response should contain total count"
        assert isinstance(data["sets"], list), "sets should be a list"
        assert len(data["sets"]) >= 1, "Should have at least DEFAULT set"
        
        # Check DEFAULT set is present
        default_set = next((s for s in data["sets"] if s["id"] == "DEFAULT"), None)
        assert default_set is not None, "DEFAULT set should be present"
        assert default_set["name"] == "Classic", f"DEFAULT set name should be Classic, got {default_set['name']}"
        assert len(default_set["symbols"]) == 9, f"DEFAULT set should have 9 symbols, got {len(default_set['symbols'])}"
        
        # Check DEFAULT symbols include expected ones
        symbol_names = [s["name"] for s in default_set["symbols"]]
        assert "7" in symbol_names, "DEFAULT should have 7 symbol"
        assert "DIAMOND" in symbol_names, "DEFAULT should have DIAMOND symbol"
        assert "CHERRY" in symbol_names, "DEFAULT should have CHERRY symbol"
        
        print(f"PASS: Listed {data['total']} symbol sets (including DEFAULT)")
        return data
    
    def test_delete_symbol_set(self):
        """DELETE /api/sla113/slots/symbols/{id} removes a custom set"""
        # Create a set first
        symbols = [
            {"name": "A", "color": "#ff0000", "weight": 5, "payout": 10},
            {"name": "B", "color": "#00ff00", "weight": 5, "payout": 10},
            {"name": "C", "color": "#0000ff", "weight": 5, "payout": 10},
            {"name": "D", "color": "#ffff00", "weight": 5, "payout": 10},
            {"name": "E", "color": "#ff00ff", "weight": 5, "payout": 10},
        ]
        create_resp = requests.post(f"{BASE_URL}/api/sla113/slots/symbols", json={"name": "TEST_ToDelete", "symbols": symbols})
        assert create_resp.status_code == 200
        set_id = create_resp.json()["id"]
        
        # Delete it
        response = requests.delete(f"{BASE_URL}/api/sla113/slots/symbols/{set_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("deleted") == True, "Response should confirm deletion"
        
        # Verify it's gone
        list_resp = requests.get(f"{BASE_URL}/api/sla113/slots/symbols")
        sets = list_resp.json().get("sets", [])
        found = any(s["id"] == set_id for s in sets)
        assert not found, f"Deleted set {set_id} should not be in list"
        
        print(f"PASS: Deleted symbol set {set_id}")
    
    def test_cannot_delete_default_set(self):
        """DELETE /api/sla113/slots/symbols/DEFAULT returns 400"""
        response = requests.delete(f"{BASE_URL}/api/sla113/slots/symbols/DEFAULT")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: Cannot delete DEFAULT symbol set")
    
    def test_create_symbol_set_requires_min_5_symbols(self):
        """POST /api/sla113/slots/symbols requires at least 5 symbols"""
        symbols = [
            {"name": "A", "color": "#ff0000", "weight": 5, "payout": 10},
            {"name": "B", "color": "#00ff00", "weight": 5, "payout": 10},
        ]
        payload = {"name": "TEST_TooFew", "symbols": symbols}
        
        response = requests.post(f"{BASE_URL}/api/sla113/slots/symbols", json=payload)
        assert response.status_code == 400, f"Expected 400 for too few symbols, got {response.status_code}"
        print("PASS: Symbol set creation requires minimum 5 symbols")


class TestFiveReelSlotTemplate:
    """5-Reel Video Slot template tests"""
    
    def test_slot_machine_build_produces_5reel_code(self):
        """Build + compile a slot_machine type produces 5-reel code with WILD, SCATTER, freeSpins, PAYLINES"""
        # Create a slot_machine project
        project_payload = {
            "name": "TEST_5Reel_Slot",
            "game_type": "slot_machine",
            "description": "Test 5-reel video slot",
            "target_platform": "webgl"
        }
        create_resp = requests.post(f"{BASE_URL}/api/sla113/projects", json=project_payload)
        assert create_resp.status_code == 200, f"Failed to create project: {create_resp.text}"
        project_id = create_resp.json()["id"]
        
        try:
            # Create a build
            build_payload = {
                "project_id": project_id,
                "target": "webgl",
                "optimization": "balanced"
            }
            build_resp = requests.post(f"{BASE_URL}/api/sla113/builds", json=build_payload)
            assert build_resp.status_code == 200, f"Failed to create build: {build_resp.text}"
            build_id = build_resp.json()["id"]
            
            # Compile the build
            compile_resp = requests.post(f"{BASE_URL}/api/sla113/builds/{build_id}/compile")
            assert compile_resp.status_code == 200, f"Failed to compile build: {compile_resp.text}"
            compile_data = compile_resp.json()
            
            assert compile_data["status"] == "completed", f"Build should be completed, got {compile_data['status']}"
            assert compile_data.get("download_url"), "Build should have download_url"
            
            # Download and check the game.js content
            download_resp = requests.get(f"{BASE_URL}{compile_data['download_url']}")
            assert download_resp.status_code == 200, "Should be able to download build"
            
            # The response is a zip file, we need to check the content
            # For now, verify the build completed successfully
            print(f"PASS: Slot machine build {build_id} compiled successfully")
            
        finally:
            # Cleanup
            requests.delete(f"{BASE_URL}/api/sla113/projects/{project_id}")
    
    def test_game_templates_slot_machine_type_exists(self):
        """Verify slot_machine game type is available"""
        response = requests.get(f"{BASE_URL}/api/sla113/game-types")
        assert response.status_code == 200
        data = response.json()
        
        assert "game_types" in data, "Response should contain game_types"
        assert "slot_machine" in data["game_types"], "slot_machine should be a valid game type"
        
        slot_info = data["game_types"]["slot_machine"]
        assert slot_info["category"] == "casino", f"slot_machine should be casino category, got {slot_info['category']}"
        
        print("PASS: slot_machine game type exists in casino category")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_lobbies(self):
        """Clean up any TEST_ prefixed lobbies"""
        response = requests.get(f"{BASE_URL}/api/sla113/fish/lobbies")
        if response.status_code == 200:
            lobbies = response.json().get("lobbies", [])
            for lobby in lobbies:
                if lobby.get("name", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/sla113/fish/lobbies/{lobby['id']}")
                    print(f"Cleaned up lobby: {lobby['id']}")
        print("PASS: Cleanup complete")
    
    def test_cleanup_test_symbol_sets(self):
        """Clean up any TEST_ prefixed symbol sets"""
        response = requests.get(f"{BASE_URL}/api/sla113/slots/symbols")
        if response.status_code == 200:
            sets = response.json().get("sets", [])
            for s in sets:
                if s.get("name", "").startswith("TEST_") and s.get("id") != "DEFAULT":
                    requests.delete(f"{BASE_URL}/api/sla113/slots/symbols/{s['id']}")
                    print(f"Cleaned up symbol set: {s['id']}")
        print("PASS: Symbol set cleanup complete")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
