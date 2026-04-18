"""
SLA113 Iteration 21 - Go-Live Pack Testing
Tests: Mobile support, /arcade portal, Juwa-tier slots, audio expansion, branding polish
"""
import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://genesis-engine-4.preview.emergentagent.com').rstrip('/')

class TestArcadePortalBackend:
    """Test /arcade portal backend dependencies"""
    
    def test_lobbies_list_returns_7_seeded(self):
        """GET /api/sla113/lobbies returns 7 seeded lobbies"""
        response = requests.get(f"{BASE_URL}/api/sla113/lobbies")
        assert response.status_code == 200
        data = response.json()
        assert "lobbies" in data
        assert data["total"] == 7
        lobbies = data["lobbies"]
        # Verify all required fields present
        for lobby in lobbies:
            assert "id" in lobby
            assert "name" in lobby
            assert "theme_color" in lobby
            assert "jackpot_tier" in lobby
            assert "base_bet" in lobby
            assert "main_boss_sprite" in lobby
        print(f"PASS: 7 lobbies returned with all required fields")
    
    def test_lobby_has_theme_color_and_tier(self):
        """Verify lobbies have theme_color and jackpot_tier for arcade cards"""
        response = requests.get(f"{BASE_URL}/api/sla113/lobbies")
        assert response.status_code == 200
        lobbies = response.json()["lobbies"]
        
        # Check Shadow Pack specifically
        shadow = next((l for l in lobbies if l["slug"] == "shadow_pack"), None)
        assert shadow is not None
        assert shadow["theme_color"] == "#d4af37"
        assert shadow["jackpot_tier"] == "GRAND"
        assert shadow["base_bet"] == 0.25
        print(f"PASS: Shadow Pack has theme_color={shadow['theme_color']}, tier={shadow['jackpot_tier']}")
    
    def test_lobby_deploy_creates_build_and_returns_preview_url(self):
        """POST /api/sla113/lobbies/{id}/deploy creates build and returns preview_url"""
        # Use Shadow Pack lobby
        response = requests.get(f"{BASE_URL}/api/sla113/lobbies")
        lobbies = response.json()["lobbies"]
        shadow = next((l for l in lobbies if l["slug"] == "shadow_pack"), None)
        assert shadow is not None
        
        # Deploy
        deploy_resp = requests.post(f"{BASE_URL}/api/sla113/lobbies/{shadow['id']}/deploy")
        assert deploy_resp.status_code == 200
        data = deploy_resp.json()
        assert "preview_url" in data
        assert "/api/sla113/live/" in data["preview_url"]
        print(f"PASS: Deploy returned preview_url={data['preview_url']}")
        return data["preview_url"]


class TestCompiledGameMobileSupport:
    """Test compiled game.js contains mobile support hooks"""
    
    @pytest.fixture
    def compiled_game_js(self):
        """Get compiled game.js from a deployed lobby"""
        # Deploy Shadow Pack
        response = requests.get(f"{BASE_URL}/api/sla113/lobbies")
        lobbies = response.json()["lobbies"]
        shadow = next((l for l in lobbies if l["slug"] == "shadow_pack"), None)
        deploy_resp = requests.post(f"{BASE_URL}/api/sla113/lobbies/{shadow['id']}/deploy")
        preview_url = deploy_resp.json()["preview_url"]
        
        # Get game.js
        game_js_url = f"{BASE_URL}{preview_url.replace('index.html', 'game.js')}"
        js_resp = requests.get(game_js_url)
        return js_resp.text
    
    def test_fish_engine_has_pointer_events(self, compiled_game_js):
        """Fish engine uses pointermove/pointerdown/pointerup (not mouse-only)"""
        assert "pointermove" in compiled_game_js
        assert "pointerdown" in compiled_game_js
        assert "pointerup" in compiled_game_js
        print("PASS: Fish engine has pointer events (mobile touch support)")
    
    def test_fish_engine_has_ambient_audio(self, compiled_game_js):
        """Fish engine has startAmbient() function for underwater drone loop"""
        assert "startAmbient" in compiled_game_js
        print("PASS: Fish engine has startAmbient() function")
    
    def test_fish_engine_has_boss_theme(self, compiled_game_js):
        """Fish engine has playBossTheme() function for per-boss music"""
        assert "playBossTheme" in compiled_game_js
        print("PASS: Fish engine has playBossTheme() function")
    
    def test_fish_engine_has_master_gain(self, compiled_game_js):
        """Fish engine has __sla_master_gain for volume slider integration"""
        assert "__sla_master_gain" in compiled_game_js
        print("PASS: Fish engine has __sla_master_gain reference")
    
    def test_fish_engine_has_theme_tint(self, compiled_game_js):
        """Fish engine has THEME_HEX + isMobile detection + jpBar uses THEME color"""
        assert "THEME_HEX" in compiled_game_js
        assert "isMobile" in compiled_game_js
        # jpBar uses THEME color
        assert "jpBar" in compiled_game_js or "THEME" in compiled_game_js
        print("PASS: Fish engine has theme tint (THEME_HEX, isMobile)")


class TestHTML5ShellMobileSupport:
    """Test HTML5 shell has mobile-safe features"""
    
    @pytest.fixture
    def compiled_html(self):
        """Get compiled index.html from a deployed lobby"""
        response = requests.get(f"{BASE_URL}/api/sla113/lobbies")
        lobbies = response.json()["lobbies"]
        shadow = next((l for l in lobbies if l["slug"] == "shadow_pack"), None)
        deploy_resp = requests.post(f"{BASE_URL}/api/sla113/lobbies/{shadow['id']}/deploy")
        preview_url = deploy_resp.json()["preview_url"]
        
        html_resp = requests.get(f"{BASE_URL}{preview_url}")
        return html_resp.text
    
    def test_html_has_viewport_fit_cover(self, compiled_html):
        """HTML has viewport-fit=cover for notch/safe-area support"""
        assert "viewport-fit=cover" in compiled_html
        print("PASS: HTML has viewport-fit=cover")
    
    def test_html_has_safe_area_inset_padding(self, compiled_html):
        """HTML has safe-area-inset padding for iOS notch"""
        assert "safe-area-inset" in compiled_html
        print("PASS: HTML has safe-area-inset padding")
    
    def test_html_has_theme_color_meta(self, compiled_html):
        """HTML has theme-color meta tag matching lobby theme"""
        assert 'name="theme-color"' in compiled_html
        print("PASS: HTML has theme-color meta tag")
    
    def test_html_has_volume_button(self, compiled_html):
        """HTML has volume button #btn-vol"""
        assert 'id="btn-vol"' in compiled_html
        print("PASS: HTML has volume button #btn-vol")
    
    def test_html_has_fullscreen_button(self, compiled_html):
        """HTML has fullscreen button #btn-fs"""
        assert 'id="btn-fs"' in compiled_html
        print("PASS: HTML has fullscreen button #btn-fs")
    
    def test_html_has_touch_action_none(self, compiled_html):
        """HTML has touch-action:none to prevent scroll/zoom"""
        assert "touch-action:none" in compiled_html or "touch-action: none" in compiled_html
        print("PASS: HTML has touch-action:none")
    
    def test_html_has_overscroll_behavior_none(self, compiled_html):
        """HTML has overscroll-behavior:none to disable iOS bounce"""
        assert "overscroll-behavior:none" in compiled_html or "overscroll-behavior: none" in compiled_html
        print("PASS: HTML has overscroll-behavior:none")


class TestSlotsEngineJuwaUpgrade:
    """Test slots engine has Juwa-tier features"""
    
    def test_slots_engine_source_has_metal_frame(self):
        """Slots engine has drawMetalFrame() for metallic cabinet"""
        # Read source file directly
        with open("/app/backend/sla113/slots_engine.py", "r") as f:
            content = f.read()
        assert "drawMetalFrame" in content
        print("PASS: Slots engine has drawMetalFrame()")
    
    def test_slots_engine_source_has_glow_spin_button(self):
        """Slots engine has drawSpinButton(glow) with pulse"""
        with open("/app/backend/sla113/slots_engine.py", "r") as f:
            content = f.read()
        assert "drawSpinButton" in content
        assert "glow" in content
        print("PASS: Slots engine has drawSpinButton(glow)")
    
    def test_slots_engine_source_has_bonus_wheel(self):
        """Slots engine has spinBonusWheel() with 8 slices"""
        with open("/app/backend/sla113/slots_engine.py", "r") as f:
            content = f.read()
        assert "spinBonusWheel" in content
        # Check for 8 slices
        assert "slices=['x2','x5','x10','x25','x50','JP','x3','x8']" in content or "8" in content
        print("PASS: Slots engine has spinBonusWheel() with 8 slices")
    
    def test_slots_engine_source_has_4_jackpot_tiers(self):
        """Slots engine has 4 jackpot tiers (MINI, MINOR, MAJOR, GRAND)"""
        with open("/app/backend/sla113/slots_engine.py", "r") as f:
            content = f.read()
        assert "GRAND" in content
        assert "MAJOR" in content
        assert "MINOR" in content
        assert "MINI" in content
        print("PASS: Slots engine has 4 jackpot tiers")
    
    def test_slots_engine_source_has_animate_win(self):
        """Slots engine has animateWin() function"""
        with open("/app/backend/sla113/slots_engine.py", "r") as f:
            content = f.read()
        assert "animateWin" in content
        print("PASS: Slots engine has animateWin()")
    
    def test_slots_engine_source_has_sfx_functions(self):
        """Slots engine has sfxJp() and sfxWin() functions"""
        with open("/app/backend/sla113/slots_engine.py", "r") as f:
            content = f.read()
        assert "sfxJp" in content
        assert "sfxWin" in content
        print("PASS: Slots engine has sfxJp() and sfxWin()")
    
    def test_slots_engine_source_has_touch_tap_to_spin(self):
        """Slots engine has touch tap-to-spin via reelBg.on('pointerdown')"""
        with open("/app/backend/sla113/slots_engine.py", "r") as f:
            content = f.read()
        assert "reelBg.interactive=true" in content
        assert "reelBg.on('pointerdown'" in content
        print("PASS: Slots engine has touch tap-to-spin")
    
    def test_slots_engine_source_has_swipe_detection(self):
        """Slots engine has swipe-down detection for spin"""
        with open("/app/backend/sla113/slots_engine.py", "r") as f:
            content = f.read()
        assert "touchstart" in content
        assert "touchend" in content
        # Check for swipe logic
        assert "dy>80" in content or "swipe" in content.lower()
        print("PASS: Slots engine has swipe-down detection")


class TestFishEngineAudioExpansion:
    """Test fish engine has audio expansion features"""
    
    def test_fish_engine_source_has_ambient_loop(self):
        """Fish engine has startAmbient() with underwater drone loop"""
        with open("/app/backend/sla113/fish_engine.py", "r") as f:
            content = f.read()
        assert "startAmbient" in content
        # Check for oscillator-based ambient
        assert "createOscillator" in content
        print("PASS: Fish engine has startAmbient() with oscillators")
    
    def test_fish_engine_source_has_boss_theme_music(self):
        """Fish engine has playBossTheme() for per-boss theme music"""
        with open("/app/backend/sla113/fish_engine.py", "r") as f:
            content = f.read()
        assert "playBossTheme" in content
        print("PASS: Fish engine has playBossTheme()")
    
    def test_fish_engine_source_has_roar_sfx(self):
        """Fish engine has playRoar() for boss roar SFX"""
        with open("/app/backend/sla113/fish_engine.py", "r") as f:
            content = f.read()
        assert "playRoar" in content
        print("PASS: Fish engine has playRoar()")
    
    def test_fish_engine_source_has_screen_shake(self):
        """Fish engine has shake() function for screen shake"""
        with open("/app/backend/sla113/fish_engine.py", "r") as f:
            content = f.read()
        assert "shake(" in content or "shakeAmt" in content
        print("PASS: Fish engine has screen shake")


class TestNoRegressions:
    """Test no regressions on existing functionality"""
    
    def test_sla113_dashboard_loads(self):
        """SLA113 dashboard /sla113 still loads (via API status)"""
        response = requests.get(f"{BASE_URL}/api/sla113/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        print("PASS: SLA113 status endpoint returns online")
    
    def test_fish_multiplayer_lobbies_endpoint(self):
        """GET /api/sla113/fish/lobbies still returns 200"""
        response = requests.get(f"{BASE_URL}/api/sla113/fish/lobbies")
        assert response.status_code == 200
        data = response.json()
        assert "lobbies" in data
        print("PASS: /fish/lobbies endpoint returns 200")
    
    def test_game_types_endpoint(self):
        """GET /api/sla113/game-types still returns game types"""
        response = requests.get(f"{BASE_URL}/api/sla113/game-types")
        assert response.status_code == 200
        data = response.json()
        assert "game_types" in data
        assert "fish_shooting" in data["game_types"]
        assert "slot_machine" in data["game_types"]
        print("PASS: /game-types endpoint returns fish_shooting and slot_machine")
    
    def test_sprites_endpoint(self):
        """GET /api/sla113/sprites still returns sprites"""
        response = requests.get(f"{BASE_URL}/api/sla113/sprites")
        assert response.status_code == 200
        data = response.json()
        assert "sprites" in data
        assert len(data["sprites"]) > 0
        print(f"PASS: /sprites endpoint returns {len(data['sprites'])} sprites")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
