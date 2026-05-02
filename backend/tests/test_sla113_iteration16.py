"""
SLA113 Iteration 16 Backend Tests
Testing: Audio Forge Engine, Build Pipeline Compile/Download, Admin Control Vault (Nexus + Matrix)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://genesis-engine-4.preview.emergentagent.com')
API = f"{BASE_URL}/api/sla113"


class TestAudioForgeEngine:
    """Audio Forge Engine - Sound Asset Generation with AI-enhanced DSP"""
    
    def test_audio_templates_returns_templates_and_engines(self):
        """GET /api/sla113/audio/templates should return template definitions and engine list"""
        response = requests.get(f"{API}/audio/templates")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "templates" in data, "Response should contain 'templates'"
        assert "audio_types" in data, "Response should contain 'audio_types'"
        assert "engines" in data, "Response should contain 'engines'"
        
        # Verify audio types
        expected_types = ["sfx", "ambience", "foley", "music_cues", "stems", "loops"]
        for t in expected_types:
            assert t in data["audio_types"], f"Missing audio type: {t}"
        
        # Verify engines
        expected_engines = ["FMOD", "SonicForge", "AudioKing", "VoiceKing"]
        for e in expected_engines:
            assert e in data["engines"], f"Missing engine: {e}"
        
        # Verify template structure
        assert "sfx" in data["templates"], "Templates should contain 'sfx'"
        sfx_template = data["templates"]["sfx"]
        assert "category" in sfx_template
        assert "physical_modeling_parameters" in sfx_template
        assert "pda_environmental_dsp" in sfx_template
        print(f"✓ Audio templates: {len(data['audio_types'])} types, {len(data['engines'])} engines")
    
    def test_audio_generate_sfx_with_ai_dsp(self):
        """POST /api/sla113/audio/generate should return audio asset with AI-enhanced DSP"""
        payload = {
            "audio_type": "sfx",
            "title": "TEST_Vault_Lock_Impact",
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
        }
        
        response = requests.post(f"{API}/audio/generate", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify asset structure
        assert "id" in data, "Response should contain 'id'"
        assert data["id"].startswith("AUD-"), f"ID should start with 'AUD-', got {data['id']}"
        
        # Verify sfx_metadata
        assert "sfx_metadata" in data
        meta = data["sfx_metadata"]
        assert meta["title"] == "TEST_Vault_Lock_Impact"
        assert meta["audio_type"] == "sfx"
        assert meta["engine"] == "FMOD"
        assert "dna_tag_preview" in meta
        
        # Verify physical modeling parameters
        assert "physical_modeling_parameters" in data
        phys = data["physical_modeling_parameters"]
        assert "transient_sharpness" in phys
        assert "decay_tail_ms" in phys
        
        # Verify PDA environmental DSP
        assert "pda_environmental_dsp" in data
        dsp = data["pda_environmental_dsp"]
        assert "reverb_wet_mix" in dsp
        assert "low_frequency_rumble_hz" in dsp
        
        # Verify waveform data
        assert "waveform_preview" in data
        assert isinstance(data["waveform_preview"], list)
        assert len(data["waveform_preview"]) > 0
        
        # Verify audio specs
        assert data["sample_rate"] == 48000
        assert data["bit_depth"] == 24
        assert data["channels"] == 2
        assert data["format"] == "wav"
        assert "duration_ms" in data
        
        # AI enhancement may or may not be present depending on API availability
        print(f"✓ Generated audio asset: {data['id']}, AI enhanced: {data.get('ai_dsp_enhancement') is not None}")
        
        # Store for cleanup
        self.__class__.generated_audio_id = data["id"]
    
    def test_audio_assets_list(self):
        """GET /api/sla113/audio/assets should list generated audio assets"""
        response = requests.get(f"{API}/audio/assets")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "assets" in data
        assert "total" in data
        assert isinstance(data["assets"], list)
        print(f"✓ Audio assets list: {data['total']} assets")
    
    def test_audio_generate_ambience(self):
        """POST /api/sla113/audio/generate with ambience type"""
        payload = {
            "audio_type": "ambience",
            "title": "TEST_Canyon_Wind",
            "game_type": "open_world",
            "engine": "SonicForge"
        }
        
        response = requests.post(f"{API}/audio/generate", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["sfx_metadata"]["audio_type"] == "ambience"
        assert data["sfx_metadata"]["category"] == "Environmental Soundscape"
        print(f"✓ Generated ambience asset: {data['id']}")
        
        self.__class__.ambience_audio_id = data["id"]
    
    def test_audio_delete_asset(self):
        """DELETE /api/sla113/audio/assets/{id} should delete the audio asset"""
        # Delete the test assets we created
        if hasattr(self.__class__, 'generated_audio_id'):
            response = requests.delete(f"{API}/audio/assets/{self.__class__.generated_audio_id}")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            data = response.json()
            assert data["deleted"] == True
            print(f"✓ Deleted audio asset: {self.__class__.generated_audio_id}")
        
        if hasattr(self.__class__, 'ambience_audio_id'):
            response = requests.delete(f"{API}/audio/assets/{self.__class__.ambience_audio_id}")
            assert response.status_code == 200
            print(f"✓ Deleted ambience asset: {self.__class__.ambience_audio_id}")
    
    def test_audio_generate_invalid_type(self):
        """POST /api/sla113/audio/generate with invalid type should return 400"""
        payload = {
            "audio_type": "invalid_type",
            "title": "TEST_Invalid",
            "game_type": "generic",
            "engine": "FMOD"
        }
        
        response = requests.post(f"{API}/audio/generate", json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Invalid audio type correctly rejected")


class TestBuildPipelineCompile:
    """Build Pipeline - HTML5/PixiJS Compilation with Real Zip Download"""
    
    @pytest.fixture(autouse=True)
    def setup_project(self):
        """Create a test project for build testing"""
        # First check if we have existing projects
        response = requests.get(f"{API}/projects")
        if response.status_code == 200:
            projects = response.json().get("projects", [])
            if projects:
                self.__class__.project_id = projects[0]["id"]
                self.__class__.project_name = projects[0]["name"]
                print(f"Using existing project: {self.__class__.project_id}")
                return
        
        # Create a new project if none exist
        payload = {
            "name": "TEST_Build_Project",
            "game_type": "fish_shooting",
            "theme": "sovereign",
            "target_platform": "web"
        }
        response = requests.post(f"{API}/projects", json=payload)
        if response.status_code == 200:
            data = response.json()
            self.__class__.project_id = data["id"]
            self.__class__.project_name = data["name"]
            print(f"Created test project: {self.__class__.project_id}")
    
    def test_create_build_queued_status(self):
        """POST /api/sla113/builds creates a build in 'queued' status"""
        if not hasattr(self.__class__, 'project_id'):
            pytest.skip("No project available for build testing")
        
        payload = {
            "project_id": self.__class__.project_id,
            "target": "webgl",
            "optimization": "balanced",
            "include_assets": True,
            "include_logic": True
        }
        
        response = requests.post(f"{API}/builds", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert data["id"].startswith("BLD-"), f"Build ID should start with 'BLD-', got {data['id']}"
        assert data["status"] == "queued", f"Expected 'queued' status, got {data['status']}"
        assert data["project_id"] == self.__class__.project_id
        assert data["target"] == "webgl"
        assert data["optimization"] == "balanced"
        assert "stages" in data
        assert len(data["stages"]) == 5  # 5 compilation stages
        
        self.__class__.build_id = data["id"]
        print(f"✓ Created build: {data['id']} with status '{data['status']}'")
    
    def test_compile_build_creates_zip(self):
        """POST /api/sla113/builds/{id}/compile compiles HTML5/PixiJS zip bundle"""
        if not hasattr(self.__class__, 'build_id'):
            pytest.skip("No build available for compilation")
        
        response = requests.post(f"{API}/builds/{self.__class__.build_id}/compile")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "completed", f"Expected 'completed' status, got {data['status']}"
        assert data["progress"] == 100
        assert "download_url" in data, "Compiled build should have download_url"
        assert data["download_url"].startswith("/api/sla113/builds/")
        assert "size_mb" in data
        assert "output" in data
        assert data["output"].endswith(".zip")
        
        # Verify all stages completed
        for stage in data["stages"]:
            assert stage["status"] == "completed", f"Stage '{stage['name']}' not completed"
            assert stage["progress"] == 100
        
        self.__class__.download_url = data["download_url"]
        print(f"✓ Compiled build: {data['id']}, size: {data['size_mb']} MB, download: {data['download_url']}")
    
    def test_download_build_returns_zip(self):
        """GET /api/sla113/builds/{id}/download returns a zip file"""
        if not hasattr(self.__class__, 'build_id'):
            pytest.skip("No build available for download")
        
        response = requests.get(f"{API}/builds/{self.__class__.build_id}/download")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify content type is zip
        content_type = response.headers.get("content-type", "")
        assert "application/zip" in content_type or "application/octet-stream" in content_type, \
            f"Expected zip content type, got {content_type}"
        
        # Verify content disposition header
        content_disp = response.headers.get("content-disposition", "")
        assert "attachment" in content_disp, "Should have attachment disposition"
        assert ".zip" in content_disp, "Filename should be .zip"
        
        # Verify we got actual content
        assert len(response.content) > 0, "Zip file should have content"
        
        # Verify it's a valid zip (starts with PK)
        assert response.content[:2] == b'PK', "Content should be a valid zip file"
        
        print(f"✓ Downloaded zip: {len(response.content)} bytes")
    
    def test_list_builds(self):
        """GET /api/sla113/builds should list all builds"""
        response = requests.get(f"{API}/builds")
        assert response.status_code == 200
        
        data = response.json()
        assert "builds" in data
        assert "total" in data
        print(f"✓ Builds list: {data['total']} builds")
    
    def test_delete_build(self):
        """DELETE /api/sla113/builds/{id} should delete the build"""
        if not hasattr(self.__class__, 'build_id'):
            pytest.skip("No build to delete")
        
        response = requests.delete(f"{API}/builds/{self.__class__.build_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] == True
        print(f"✓ Deleted build: {self.__class__.build_id}")


class TestAdminControlVaultNexus:
    """Admin Control Vault - ArtTech Nexus Generator"""
    
    def test_nexus_pipelines_returns_8_archetypes(self):
        """GET /api/sla113/nexus/pipelines returns 8 pipeline archetypes"""
        response = requests.get(f"{API}/nexus/pipelines")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "pipelines" in data
        pipelines = data["pipelines"]
        assert len(pipelines) == 8, f"Expected 8 pipelines, got {len(pipelines)}"
        
        # Verify pipeline structure
        expected_ids = ["arcade", "open_world", "tactical_fps", "epic_rpg", "pano_arte", "casino_suite", "horror", "racing"]
        for p in pipelines:
            assert "id" in p
            assert "name" in p
            assert "tags" in p
            assert "color" in p
            assert "status" in p
            assert isinstance(p["tags"], list)
            assert p["color"].startswith("#")
        
        # Verify all expected pipelines present
        pipeline_ids = [p["id"] for p in pipelines]
        for expected_id in expected_ids:
            assert expected_id in pipeline_ids, f"Missing pipeline: {expected_id}"
        
        print(f"✓ Nexus pipelines: {len(pipelines)} archetypes")
        for p in pipelines:
            print(f"  - {p['name']}: {', '.join(p['tags'])}")
    
    def test_nexus_os_modules_returns_8_mappings(self):
        """GET /api/sla113/nexus/os-modules returns 8 OS module functional mappings"""
        response = requests.get(f"{API}/nexus/os-modules")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "modules" in data
        modules = data["modules"]
        assert len(modules) == 8, f"Expected 8 modules, got {len(modules)}"
        
        # Verify module structure
        for m in modules:
            assert "os_module" in m
            assert "fmodel_utility" in m
            assert "functional_output" in m
        
        print(f"✓ OS Modules: {len(modules)} functional mappings")
        for m in modules:
            print(f"  - {m['os_module']}: {m['fmodel_utility']}")


class TestAdminControlVaultMatrix:
    """Admin Control Vault - Matrix Parameters"""
    
    def test_matrix_parameters_returns_engine_config(self):
        """GET /api/sla113/nexus/matrix returns engine parameters and fmodel_utility status"""
        response = requests.get(f"{API}/nexus/matrix")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify parameters section
        assert "parameters" in data
        params = data["parameters"]
        
        expected_params = ["physics_engine", "audio_middleware", "render_pipeline", "biome", "archetype"]
        for param_name in expected_params:
            assert param_name in params, f"Missing parameter: {param_name}"
            param = params[param_name]
            assert "value" in param
            assert "status" in param
            assert "icon" in param
        
        # Verify specific values
        assert params["physics_engine"]["value"] == "Unity 6 // DOTS"
        assert params["audio_middleware"]["value"] == "FMOD Studio"
        assert params["render_pipeline"]["value"] == "Lumen RTX"
        
        # Verify fmodel_utility section
        assert "fmodel_utility" in data
        fmodel = data["fmodel_utility"]
        
        expected_fmodel_keys = ["texture_link", "mesh_buffer", "operator_environment", "admin_id", "system_status"]
        for key in expected_fmodel_keys:
            assert key in fmodel, f"Missing fmodel_utility key: {key}"
        
        assert fmodel["texture_link"] == "ACTIVE"
        assert fmodel["mesh_buffer"] == "READY"
        assert fmodel["system_status"] == "STABLE"
        
        print(f"✓ Matrix parameters: {len(params)} engine params, fmodel_utility status: {fmodel['system_status']}")
        for name, param in params.items():
            print(f"  - {name}: {param['value']} [{param['status']}]")


class TestExistingEndpointsRegression:
    """Regression tests for existing SLA113 endpoints"""
    
    def test_sla113_status(self):
        """GET /api/sla113/status should return platform status"""
        response = requests.get(f"{API}/status")
        assert response.status_code == 200
        data = response.json()
        assert data["universe"] == "sla113"
        assert data["status"] == "online"
        print(f"✓ SLA113 status: {data['status']}")
    
    def test_game_types(self):
        """GET /api/sla113/game-types should return game types"""
        response = requests.get(f"{API}/game-types")
        assert response.status_code == 200
        data = response.json()
        assert "game_types" in data
        assert len(data["game_types"]) > 0
        print(f"✓ Game types: {len(data['game_types'])} types")
    
    def test_universes(self):
        """GET /api/sla113/universes should return registered universes"""
        response = requests.get(f"{API}/universes")
        assert response.status_code == 200
        data = response.json()
        assert "universes" in data
        assert len(data["universes"]) >= 4  # At least 4 core universes
        print(f"✓ Universes: {data['total']} registered")
    
    def test_frontline_snapshot(self):
        """GET /api/sla113/frontline/snapshot should return metrics"""
        response = requests.get(f"{API}/frontline/snapshot")
        assert response.status_code == 200
        data = response.json()
        assert "total_projects" in data
        assert "universes_online" in data
        print(f"✓ Frontline snapshot: {data['total_projects']} projects, {data['universes_online']} universes")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
