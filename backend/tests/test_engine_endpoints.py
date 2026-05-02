"""
Backend API Tests for Hybrid Intelligence Core - Engine Endpoints
Tests all GET endpoints for the 15 modular engine routers after refactoring.
"""
import pytest
import requests
import os

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestHealthEndpoint:
    """Test /api/health endpoint - should return all 18 engines"""
    
    def test_health_returns_200(self):
        """Health endpoint should return 200 OK"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
    
    def test_health_returns_all_18_engines(self):
        """Health endpoint should list all 18 engines"""
        response = requests.get(f"{BASE_URL}/api/health")
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "engines" in data
        assert len(data["engines"]) == 18
        
        # Verify key engines are present
        expected_engines = [
            "hybrid_intelligence_core",
            "routing_engine",
            "strategy_engine",
            "plan_builder_engine",
            "analysis_engine",
            "opportunity_mapper_engine",
            "evaluator_engine",
            "pricing_engine",
            "blueprint_engine",
            "persona_engine",
            "anime_character_engine",
            "anime_lore_engine",
            "anime_story_engine",
            "art_direction_engine",
            "pipeline_composer_engine",
            "canon_enforcer",
            "drift_monitor",
            "error_handler"
        ]
        for engine in expected_engines:
            assert engine in data["engines"], f"Missing engine: {engine}"
    
    def test_health_returns_model_availability(self):
        """Health endpoint should show model availability"""
        response = requests.get(f"{BASE_URL}/api/health")
        data = response.json()
        
        assert "models" in data
        assert data["models"]["gpt-5.2"] == "available"
        assert data["models"]["claude-sonnet-4.5"] == "available"
        assert data["models"]["gemini-3-flash"] == "available"


class TestArtDirectionEndpoints:
    """Test /api/art-direction/* endpoints"""
    
    def test_get_style_templates(self):
        """GET /api/art-direction/styles should return style templates"""
        response = requests.get(f"{BASE_URL}/api/art-direction/styles")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify expected styles exist
        expected_styles = ["anime", "cinematic", "painterly", "stylized", "minimalist"]
        for style in expected_styles:
            assert style in data, f"Missing style: {style}"
    
    def test_get_color_moods(self):
        """GET /api/art-direction/color-moods should return color mood presets"""
        response = requests.get(f"{BASE_URL}/api/art-direction/color-moods")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify expected moods exist
        expected_moods = ["warm_heroic", "cool_mysterious", "pastel_dreamy", "dark_dramatic", "cyberpunk"]
        for mood in expected_moods:
            assert mood in data, f"Missing mood: {mood}"
    
    def test_post_art_direction_endpoint_exists(self):
        """POST /api/art-direction should accept ArtDirectionRequest"""
        # Test that endpoint exists and accepts the request format
        payload = {
            "project": "TEST_art_project",
            "genre": "anime",
            "mood": "dramatic"
        }
        response = requests.post(f"{BASE_URL}/api/art-direction", json=payload)
        
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404, "POST /api/art-direction endpoint not found"
        # Should not return 422 (validation error) for valid payload
        assert response.status_code != 422, f"Validation error: {response.json()}"


class TestAnimeEndpoints:
    """Test /api/anime/* endpoints"""
    
    def test_get_anime_genres(self):
        """GET /api/anime/genres should return anime genres"""
        response = requests.get(f"{BASE_URL}/api/anime/genres")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify expected genres exist
        expected_genres = ["shonen", "shojo", "seinen", "isekai", "mecha", "slice_of_life"]
        for genre in expected_genres:
            assert genre in data, f"Missing genre: {genre}"
    
    def test_get_character_archetypes(self):
        """GET /api/anime/archetypes should return character archetypes"""
        response = requests.get(f"{BASE_URL}/api/anime/archetypes")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify archetype categories exist
        assert "protagonist" in data
        assert "antagonist" in data
        assert "support" in data
    
    def test_post_anime_lore_endpoint_exists(self):
        """POST /api/anime/lore should accept AnimeLoreRequest"""
        payload = {
            "world_concept": "TEST_world_concept",
            "genre": "shonen"
        }
        response = requests.post(f"{BASE_URL}/api/anime/lore", json=payload)
        
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404, "POST /api/anime/lore endpoint not found"
        # Should not return 422 (validation error) for valid payload
        assert response.status_code != 422, f"Validation error: {response.json()}"
    
    def test_post_anime_story_endpoint_exists(self):
        """POST /api/anime/story should accept AnimeStoryRequest"""
        payload = {
            "concept": "TEST_story_concept",
            "genre": "shonen"
        }
        response = requests.post(f"{BASE_URL}/api/anime/story", json=payload)
        
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404, "POST /api/anime/story endpoint not found"
        # Should not return 422 (validation error) for valid payload
        assert response.status_code != 422, f"Validation error: {response.json()}"


class TestPipelineEndpoints:
    """Test /api/pipeline/* endpoints"""
    
    def test_get_available_engines(self):
        """GET /api/pipeline/engines should return available engines"""
        response = requests.get(f"{BASE_URL}/api/pipeline/engines")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify key engines are listed
        expected_engines = ["strategy_engine", "plan_builder_engine", "analysis_engine", "persona_engine"]
        for engine in expected_engines:
            assert engine in data, f"Missing engine: {engine}"
    
    def test_get_pipeline_templates(self):
        """GET /api/pipeline/templates should return pipeline templates"""
        response = requests.get(f"{BASE_URL}/api/pipeline/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify expected templates exist
        expected_templates = ["full_business_plan", "product_launch", "startup_validation", "system_design"]
        for template in expected_templates:
            assert template in data, f"Missing template: {template}"


class TestEvaluatorEndpoints:
    """Test /api/evaluate/* endpoints"""
    
    def test_get_evaluation_presets(self):
        """GET /api/evaluate/presets should return evaluation presets"""
        response = requests.get(f"{BASE_URL}/api/evaluate/presets")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify expected presets exist
        expected_presets = ["strategy", "idea", "plan", "offer"]
        for preset in expected_presets:
            assert preset in data, f"Missing preset: {preset}"


class TestPricingEndpoints:
    """Test /api/pricing/* endpoints"""
    
    def test_get_pricing_models(self):
        """GET /api/pricing/models should return pricing models"""
        response = requests.get(f"{BASE_URL}/api/pricing/models")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify expected pricing models exist
        expected_models = ["subscription", "usage-based", "hybrid", "one-time"]
        for model in expected_models:
            assert model in data, f"Missing pricing model: {model}"


class TestBlueprintEndpoints:
    """Test /api/blueprint/* endpoints"""
    
    def test_get_component_types(self):
        """GET /api/blueprint/component-types should return component types"""
        response = requests.get(f"{BASE_URL}/api/blueprint/component-types")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify expected component types exist
        expected_types = ["service", "module", "datastore", "ui", "integration", "queue", "gateway", "worker"]
        for comp_type in expected_types:
            assert comp_type in data, f"Missing component type: {comp_type}"


class TestPersonaEndpoints:
    """Test /api/persona/* endpoints"""
    
    def test_get_persona_templates(self):
        """GET /api/persona/templates should return persona templates"""
        response = requests.get(f"{BASE_URL}/api/persona/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify expected templates exist
        expected_templates = ["b2b_buyer", "consumer", "developer", "founder"]
        for template in expected_templates:
            assert template in data, f"Missing template: {template}"


class TestCoreEndpoints:
    """Test /api/core/* endpoints"""
    
    def test_get_core_status(self):
        """GET /api/core/status should return system status"""
        response = requests.get(f"{BASE_URL}/api/core/status")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_core_log(self):
        """GET /api/core/log should return execution log"""
        response = requests.get(f"{BASE_URL}/api/core/log")
        assert response.status_code == 200
        
        data = response.json()
        assert "log" in data
        assert "total_executions" in data


class TestDriftEndpoints:
    """Test /api/drift-report endpoint"""
    
    def test_get_drift_report(self):
        """GET /api/drift-report should return drift metrics"""
        response = requests.get(f"{BASE_URL}/api/drift-report")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
