"""
SLA113 Iteration 17 Backend Tests
Tests for:
1. Deploy Engine - Real static file hosting with live preview URLs
2. Audio Forge - POST /api/sla113/audio/generate and GET /api/sla113/audio/assets
3. Existing endpoints verification
"""
import pytest
import requests
import os
import time
import zipfile
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDeployEngine:
    """Deploy Engine tests - real static file hosting"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Create a project, build, and compile it for deployment testing"""
        self.project_id = None
        self.build_id = None
        self.deploy_id = None
        
        # Create a test project
        resp = requests.post(f"{BASE_URL}/api/sla113/projects", json={
            "name": f"TEST_Deploy_Project_{int(time.time())}",
            "game_type": "fish_shooting",
            "theme": "sovereign",
            "target_platform": "webgl"
        })
        if resp.status_code == 200:
            self.project_id = resp.json().get("id")
            
            # Create a build
            build_resp = requests.post(f"{BASE_URL}/api/sla113/builds", json={
                "project_id": self.project_id,
                "target": "webgl",
                "optimization": "balanced"
            })
            if build_resp.status_code == 200:
                self.build_id = build_resp.json().get("id")
                
                # Compile the build
                compile_resp = requests.post(f"{BASE_URL}/api/sla113/builds/{self.build_id}/compile")
                if compile_resp.status_code == 200:
                    print(f"Build compiled: {self.build_id}")
        
        yield
        
        # Cleanup
        if self.deploy_id:
            requests.delete(f"{BASE_URL}/api/sla113/deploy/{self.deploy_id}")
        if self.build_id:
            requests.delete(f"{BASE_URL}/api/sla113/builds/{self.build_id}")
        if self.project_id:
            requests.delete(f"{BASE_URL}/api/sla113/projects/{self.project_id}")
    
    def test_deploy_creates_live_deployment(self):
        """POST /api/sla113/deploy creates deployment with status 'live' and real preview_url"""
        if not self.build_id:
            pytest.skip("No build available for deployment test")
        
        resp = requests.post(f"{BASE_URL}/api/sla113/deploy", json={
            "build_id": self.build_id,
            "target_cdn": "cloudflare",
            "region": "us-west"
        })
        
        assert resp.status_code == 200, f"Deploy failed: {resp.text}"
        data = resp.json()
        
        # Verify deployment structure
        assert "id" in data, "Deployment should have an ID"
        assert data["id"].startswith("DPL-"), f"Deploy ID should start with DPL-, got {data['id']}"
        self.deploy_id = data["id"]
        
        # Verify status is 'live' (instant deployment)
        assert data["status"] == "live", f"Expected status 'live', got {data['status']}"
        
        # Verify preview_url points to /api/sla113/live/{id}/index.html
        assert "preview_url" in data or "url" in data, "Deployment should have preview_url or url"
        url = data.get("preview_url") or data.get("url")
        assert f"/api/sla113/live/{self.deploy_id}/index.html" in url, f"URL should point to live endpoint, got {url}"
        
        # Verify progress is 100%
        assert data["progress"] == 100, f"Expected progress 100, got {data['progress']}"
        
        print(f"✓ Deploy created: {self.deploy_id} with live URL: {url}")
    
    def test_live_game_serves_html(self):
        """GET /api/sla113/live/{deploy_id}/index.html serves real HTML5 game"""
        if not self.build_id:
            pytest.skip("No build available for deployment test")
        
        # First deploy
        deploy_resp = requests.post(f"{BASE_URL}/api/sla113/deploy", json={
            "build_id": self.build_id,
            "target_cdn": "cloudflare",
            "region": "us-west"
        })
        assert deploy_resp.status_code == 200
        self.deploy_id = deploy_resp.json()["id"]
        
        # Fetch the live HTML
        html_resp = requests.get(f"{BASE_URL}/api/sla113/live/{self.deploy_id}/index.html")
        
        assert html_resp.status_code == 200, f"Failed to fetch index.html: {html_resp.status_code}"
        assert "text/html" in html_resp.headers.get("content-type", ""), "Should return HTML content type"
        
        content = html_resp.text
        # Verify it's a real HTML5 game with PixiJS
        assert "<!DOCTYPE html>" in content or "<html" in content, "Should be valid HTML"
        assert "pixi" in content.lower() or "PIXI" in content, "Should include PixiJS reference"
        assert "game.js" in content, "Should reference game.js"
        
        print(f"✓ Live HTML served successfully for {self.deploy_id}")
    
    def test_live_game_serves_javascript(self):
        """GET /api/sla113/live/{deploy_id}/game.js serves the game JavaScript"""
        if not self.build_id:
            pytest.skip("No build available for deployment test")
        
        # First deploy
        deploy_resp = requests.post(f"{BASE_URL}/api/sla113/deploy", json={
            "build_id": self.build_id,
            "target_cdn": "cloudflare",
            "region": "us-west"
        })
        assert deploy_resp.status_code == 200
        self.deploy_id = deploy_resp.json()["id"]
        
        # Fetch the game.js
        js_resp = requests.get(f"{BASE_URL}/api/sla113/live/{self.deploy_id}/game.js")
        
        assert js_resp.status_code == 200, f"Failed to fetch game.js: {js_resp.status_code}"
        assert "javascript" in js_resp.headers.get("content-type", ""), "Should return JavaScript content type"
        
        content = js_resp.text
        # Verify it's real game code
        assert "PIXI" in content or "pixi" in content.lower(), "Should reference PIXI"
        assert "GAME_CONFIG" in content, "Should have GAME_CONFIG"
        assert "ASSET_MANIFEST" in content, "Should have ASSET_MANIFEST"
        
        print(f"✓ Live game.js served successfully for {self.deploy_id}")
    
    def test_delete_deployment_cleans_up(self):
        """DELETE /api/sla113/deploy/{id} cleans up files and removes deployment"""
        if not self.build_id:
            pytest.skip("No build available for deployment test")
        
        # First deploy
        deploy_resp = requests.post(f"{BASE_URL}/api/sla113/deploy", json={
            "build_id": self.build_id,
            "target_cdn": "cloudflare",
            "region": "us-west"
        })
        assert deploy_resp.status_code == 200
        deploy_id = deploy_resp.json()["id"]
        
        # Verify it exists
        html_resp = requests.get(f"{BASE_URL}/api/sla113/live/{deploy_id}/index.html")
        assert html_resp.status_code == 200, "Deployment should exist before delete"
        
        # Delete it
        delete_resp = requests.delete(f"{BASE_URL}/api/sla113/deploy/{deploy_id}")
        assert delete_resp.status_code == 200, f"Delete failed: {delete_resp.text}"
        assert delete_resp.json().get("deleted") == True
        
        # Verify files are gone
        html_resp_after = requests.get(f"{BASE_URL}/api/sla113/live/{deploy_id}/index.html")
        assert html_resp_after.status_code == 404, "Files should be deleted after deployment removal"
        
        # Verify deployment is removed from list
        list_resp = requests.get(f"{BASE_URL}/api/sla113/deployments")
        deployments = list_resp.json().get("deployments", [])
        deploy_ids = [d["id"] for d in deployments]
        assert deploy_id not in deploy_ids, "Deployment should be removed from list"
        
        self.deploy_id = None  # Already deleted
        print(f"✓ Deployment {deploy_id} deleted and cleaned up successfully")


class TestAudioForge:
    """Audio Forge tests - generation and asset management"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.created_asset_ids = []
        yield
        # Cleanup
        for asset_id in self.created_asset_ids:
            requests.delete(f"{BASE_URL}/api/sla113/audio/assets/{asset_id}")
    
    def test_audio_generate_creates_asset(self):
        """POST /api/sla113/audio/generate creates audio asset with DSP parameters"""
        resp = requests.post(f"{BASE_URL}/api/sla113/audio/generate", json={
            "audio_type": "sfx",
            "title": "TEST_Explosion_Sound",
            "game_type": "fish_shooting",
            "engine": "FMOD",
            "custom_params": {
                "physical_modeling_parameters": {
                    "transient_sharpness": 0.95,
                    "decay_tail_ms": 4500
                },
                "pda_environmental_dsp": {
                    "reverb_wet_mix": 0.65,
                    "low_frequency_rumble_hz": 35
                }
            }
        })
        
        assert resp.status_code == 200, f"Audio generate failed: {resp.text}"
        data = resp.json()
        
        # Verify asset structure
        assert "id" in data, "Audio asset should have an ID"
        self.created_asset_ids.append(data["id"])
        
        assert "sfx_metadata" in data, "Should have sfx_metadata"
        assert data["sfx_metadata"]["title"] == "TEST_Explosion_Sound"
        assert data["sfx_metadata"]["audio_type"] == "sfx"
        assert data["sfx_metadata"]["engine"] == "FMOD"
        
        # Verify audio properties
        assert "duration_ms" in data, "Should have duration_ms"
        assert "sample_rate" in data, "Should have sample_rate"
        assert "bit_depth" in data, "Should have bit_depth"
        assert "channels" in data, "Should have channels"
        assert "waveform_preview" in data, "Should have waveform_preview"
        
        # Verify DSP parameters
        assert "physical_modeling_parameters" in data, "Should have physical_modeling_parameters"
        assert "pda_environmental_dsp" in data, "Should have pda_environmental_dsp"
        
        print(f"✓ Audio asset created: {data['id']}")
    
    def test_audio_assets_list(self):
        """GET /api/sla113/audio/assets lists audio assets"""
        # First create an asset
        create_resp = requests.post(f"{BASE_URL}/api/sla113/audio/generate", json={
            "audio_type": "ambience",
            "title": "TEST_Ambient_Wind",
            "game_type": "open_world",
            "engine": "SonicForge"
        })
        assert create_resp.status_code == 200
        asset_id = create_resp.json()["id"]
        self.created_asset_ids.append(asset_id)
        
        # List assets
        list_resp = requests.get(f"{BASE_URL}/api/sla113/audio/assets")
        assert list_resp.status_code == 200
        data = list_resp.json()
        
        assert "assets" in data, "Should have assets array"
        assert "total" in data, "Should have total count"
        
        # Verify our asset is in the list
        asset_ids = [a["id"] for a in data["assets"]]
        assert asset_id in asset_ids, "Created asset should be in list"
        
        print(f"✓ Audio assets list returned {data['total']} assets")
    
    def test_audio_generate_different_types(self):
        """POST /api/sla113/audio/generate works for all audio types"""
        audio_types = ["sfx", "ambience", "foley", "music_cues", "stems", "loops"]
        
        for audio_type in audio_types:
            resp = requests.post(f"{BASE_URL}/api/sla113/audio/generate", json={
                "audio_type": audio_type,
                "title": f"TEST_{audio_type}_sample",
                "game_type": "fish_shooting",
                "engine": "FMOD"
            })
            
            assert resp.status_code == 200, f"Failed for audio_type={audio_type}: {resp.text}"
            data = resp.json()
            self.created_asset_ids.append(data["id"])
            assert data["sfx_metadata"]["audio_type"] == audio_type
            print(f"  ✓ {audio_type} generated")
        
        print(f"✓ All {len(audio_types)} audio types work correctly")


class TestExistingEndpoints:
    """Verify existing endpoints still work after refactor"""
    
    def test_status_endpoint(self):
        """GET /api/sla113/status returns platform status"""
        resp = requests.get(f"{BASE_URL}/api/sla113/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["universe"] == "sla113"
        assert data["status"] == "online"
        print("✓ Status endpoint working")
    
    def test_game_types_endpoint(self):
        """GET /api/sla113/game-types returns game types"""
        resp = requests.get(f"{BASE_URL}/api/sla113/game-types")
        assert resp.status_code == 200
        data = resp.json()
        assert "game_types" in data
        assert "audio_middleware" in data
        assert "audio_engines" in data
        print(f"✓ Game types endpoint returned {len(data['game_types'])} types")
    
    def test_nexus_pipelines(self):
        """GET /api/sla113/nexus/pipelines returns 8 pipeline archetypes"""
        resp = requests.get(f"{BASE_URL}/api/sla113/nexus/pipelines")
        assert resp.status_code == 200
        data = resp.json()
        assert "pipelines" in data
        assert len(data["pipelines"]) == 8, f"Expected 8 pipelines, got {len(data['pipelines'])}"
        
        # Verify structure
        for p in data["pipelines"]:
            assert "id" in p
            assert "name" in p
            assert "tags" in p
            assert "color" in p
            assert "status" in p
        
        print("✓ Nexus pipelines endpoint returned 8 archetypes")
    
    def test_nexus_matrix(self):
        """GET /api/sla113/nexus/matrix returns engine parameters"""
        resp = requests.get(f"{BASE_URL}/api/sla113/nexus/matrix")
        assert resp.status_code == 200
        data = resp.json()
        
        assert "parameters" in data
        assert "fmodel_utility" in data
        
        # Verify 5 engine params
        params = data["parameters"]
        expected_params = ["physics_engine", "audio_middleware", "render_pipeline", "biome", "archetype"]
        for param in expected_params:
            assert param in params, f"Missing parameter: {param}"
        
        print("✓ Matrix parameters endpoint working")
    
    def test_nexus_os_modules(self):
        """GET /api/sla113/nexus/os-modules returns 8 module mappings"""
        resp = requests.get(f"{BASE_URL}/api/sla113/nexus/os-modules")
        assert resp.status_code == 200
        data = resp.json()
        
        assert "modules" in data
        assert len(data["modules"]) == 8, f"Expected 8 modules, got {len(data['modules'])}"
        
        # Verify structure
        for m in data["modules"]:
            assert "os_module" in m
            assert "fmodel_utility" in m
            assert "functional_output" in m
        
        print("✓ OS modules endpoint returned 8 mappings")
    
    def test_audio_templates(self):
        """GET /api/sla113/audio/templates returns audio type templates"""
        resp = requests.get(f"{BASE_URL}/api/sla113/audio/templates")
        assert resp.status_code == 200
        data = resp.json()
        
        assert "audio_types" in data
        assert "engines" in data
        
        expected_types = ["sfx", "ambience", "foley", "music_cues", "stems", "loops"]
        for t in expected_types:
            assert t in data["audio_types"], f"Missing audio type: {t}"
        
        print(f"✓ Audio templates endpoint returned {len(data['audio_types'])} types")


class TestBuildPipeline:
    """Build Pipeline tests - verify compile still works"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.project_id = None
        self.build_id = None
        
        # Create a test project
        resp = requests.post(f"{BASE_URL}/api/sla113/projects", json={
            "name": f"TEST_Build_Project_{int(time.time())}",
            "game_type": "slot_machine",
            "theme": "casino",
            "target_platform": "webgl"
        })
        if resp.status_code == 200:
            self.project_id = resp.json().get("id")
        
        yield
        
        # Cleanup
        if self.build_id:
            requests.delete(f"{BASE_URL}/api/sla113/builds/{self.build_id}")
        if self.project_id:
            requests.delete(f"{BASE_URL}/api/sla113/projects/{self.project_id}")
    
    def test_build_compile_creates_download(self):
        """POST /api/sla113/builds/{id}/compile creates downloadable zip"""
        if not self.project_id:
            pytest.skip("No project available")
        
        # Create build
        build_resp = requests.post(f"{BASE_URL}/api/sla113/builds", json={
            "project_id": self.project_id,
            "target": "webgl",
            "optimization": "balanced"
        })
        assert build_resp.status_code == 200
        self.build_id = build_resp.json()["id"]
        
        # Compile
        compile_resp = requests.post(f"{BASE_URL}/api/sla113/builds/{self.build_id}/compile")
        assert compile_resp.status_code == 200
        data = compile_resp.json()
        
        assert data["status"] == "completed"
        assert data["progress"] == 100
        assert "download_url" in data
        assert data["download_url"] == f"/api/sla113/builds/{self.build_id}/download"
        
        # Verify download works
        download_resp = requests.get(f"{BASE_URL}{data['download_url']}")
        assert download_resp.status_code == 200
        assert "application/zip" in download_resp.headers.get("content-type", "")
        
        # Verify zip contents
        zip_buffer = io.BytesIO(download_resp.content)
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            names = zf.namelist()
            assert "index.html" in names, "Zip should contain index.html"
            assert "game.js" in names, "Zip should contain game.js"
            assert "game.json" in names, "Zip should contain game.json"
        
        print(f"✓ Build {self.build_id} compiled with valid zip download")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
