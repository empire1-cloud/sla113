"""
SLA113 - Iteration 13 Tests
Tests new features: Build Pipeline, Compliance Engine, Deploy Engine, Pipeline Pulse
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
API_URL = f"{BASE_URL}/api/sla113"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


# ─── BUILD PIPELINE TESTS ───
class TestSLA113Builds:
    """Test Build Pipeline Engine - /api/sla113/builds"""
    
    @pytest.fixture(autouse=True)
    def setup_project(self, api_client):
        """Create a test project for build tests"""
        project_data = {
            "name": "TEST_Build_Project",
            "game_type": "fish_shooter",
            "theme": "neon",
            "target_platform": "web"
        }
        response = api_client.post(f"{API_URL}/projects", json=project_data)
        if response.status_code == 200:
            self.project_id = response.json()["id"]
        yield
        # Cleanup project
        if hasattr(self, 'project_id'):
            api_client.delete(f"{API_URL}/projects/{self.project_id}")
    
    def test_list_builds(self, api_client):
        """GET /api/sla113/builds should return list of builds"""
        response = api_client.get(f"{API_URL}/builds")
        assert response.status_code == 200
        
        data = response.json()
        assert "builds" in data
        assert "total" in data
        assert isinstance(data["builds"], list)
    
    def test_create_build_from_project(self, api_client):
        """POST /api/sla113/builds should create a build from project_id"""
        if not hasattr(self, 'project_id'):
            pytest.skip("No project created for build test")
        
        build_data = {
            "project_id": self.project_id,
            "target": "webgl",
            "optimization": "balanced",
            "include_assets": True,
            "include_logic": True
        }
        response = api_client.post(f"{API_URL}/builds", json=build_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["project_id"] == self.project_id
        assert data["target"] == "webgl"
        assert data["optimization"] == "balanced"
        assert data["status"] == "queued"
        assert data["progress"] == 0
        assert "id" in data
        assert data["id"].startswith("BLD-")
        assert "stages" in data
        assert len(data["stages"]) == 5  # 5 build stages
        assert data["stages"][0]["name"] == "Asset Compilation"
        
        # Store for further tests
        TestSLA113Builds.created_build_id = data["id"]
    
    def test_create_build_invalid_project(self, api_client):
        """POST /api/sla113/builds with invalid project_id should return 404"""
        response = api_client.post(f"{API_URL}/builds", json={
            "project_id": "invalid-project-id",
            "target": "webgl"
        })
        assert response.status_code == 404
    
    def test_advance_build_stages(self, api_client):
        """POST /api/sla113/builds/{id}/advance should advance build through stages"""
        build_id = getattr(TestSLA113Builds, 'created_build_id', None)
        if not build_id:
            pytest.skip("No build created to advance")
        
        # Advance multiple times to complete all stages (needs ~14 advances for 5 stages)
        for i in range(20):  # Max 20 advances to complete 5 stages
            response = api_client.post(f"{API_URL}/builds/{build_id}/advance")
            assert response.status_code == 200
            
            data = response.json()
            if data["status"] == "completed":
                # Verify completed build has output
                assert data["output"] is not None
                assert data["size_mb"] is not None
                assert data["progress"] == 100
                break
        
        # Verify build is completed
        final_response = api_client.get(f"{API_URL}/builds")
        builds = final_response.json()["builds"]
        build = next((b for b in builds if b["id"] == build_id), None)
        assert build is not None
        assert build["status"] == "completed"
    
    def test_delete_build(self, api_client):
        """DELETE /api/sla113/builds/{id} should delete build"""
        build_id = getattr(TestSLA113Builds, 'created_build_id', None)
        if not build_id:
            pytest.skip("No build created to delete")
        
        response = api_client.delete(f"{API_URL}/builds/{build_id}")
        assert response.status_code == 200
        assert response.json()["deleted"] == True
    
    def test_delete_nonexistent_build(self, api_client):
        """DELETE /api/sla113/builds/{id} with invalid ID should return 404"""
        response = api_client.delete(f"{API_URL}/builds/BLD-INVALID123")
        assert response.status_code == 404


# ─── COMPLIANCE ENGINE TESTS ───
class TestSLA113Compliance:
    """Test Compliance Engine - /api/sla113/compliance"""
    
    @pytest.fixture(autouse=True)
    def setup_project(self, api_client):
        """Create a test project for compliance tests"""
        project_data = {
            "name": "TEST_Compliance_Project",
            "game_type": "slot_machine",
            "theme": "vegas",
            "target_platform": "web"
        }
        response = api_client.post(f"{API_URL}/projects", json=project_data)
        if response.status_code == 200:
            self.project_id = response.json()["id"]
        yield
        # Cleanup project
        if hasattr(self, 'project_id'):
            api_client.delete(f"{API_URL}/projects/{self.project_id}")
    
    def test_list_compliance_reports(self, api_client):
        """GET /api/sla113/compliance should return list of reports"""
        response = api_client.get(f"{API_URL}/compliance")
        assert response.status_code == 200
        
        data = response.json()
        assert "reports" in data
        assert "total" in data
        assert isinstance(data["reports"], list)
    
    def test_run_compliance_check_gli(self, api_client):
        """POST /api/sla113/compliance/check should run GLI compliance scan"""
        if not hasattr(self, 'project_id'):
            pytest.skip("No project created for compliance test")
        
        response = api_client.post(f"{API_URL}/compliance/check", json={
            "project_id": self.project_id,
            "jurisdiction": "GLI",
            "check_type": "full"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["project_id"] == self.project_id
        assert data["jurisdiction"] == "GLI"
        assert data["check_type"] == "full"
        assert "id" in data
        assert data["id"].startswith("CMP-")
        assert "status" in data
        assert data["status"] in ["CERTIFIED", "NEEDS_REMEDIATION"]
        assert "results" in data
        assert len(data["results"]) >= 6  # GLI has 6 checks
        assert "pass_rate" in data
        
        # Store for cleanup
        TestSLA113Compliance.created_report_id = data["id"]
    
    def test_run_compliance_check_mga(self, api_client):
        """POST /api/sla113/compliance/check should run MGA compliance scan"""
        if not hasattr(self, 'project_id'):
            pytest.skip("No project created for compliance test")
        
        response = api_client.post(f"{API_URL}/compliance/check", json={
            "project_id": self.project_id,
            "jurisdiction": "MGA",
            "check_type": "full"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["jurisdiction"] == "MGA"
        assert len(data["results"]) >= 5  # MGA has 5 checks
    
    def test_run_compliance_check_ukgc(self, api_client):
        """POST /api/sla113/compliance/check should run UKGC compliance scan"""
        if not hasattr(self, 'project_id'):
            pytest.skip("No project created for compliance test")
        
        response = api_client.post(f"{API_URL}/compliance/check", json={
            "project_id": self.project_id,
            "jurisdiction": "UKGC",
            "check_type": "full"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["jurisdiction"] == "UKGC"
        assert len(data["results"]) >= 6  # UKGC has 6 checks
    
    def test_run_compliance_check_curacao(self, api_client):
        """POST /api/sla113/compliance/check should run CURACAO compliance scan"""
        if not hasattr(self, 'project_id'):
            pytest.skip("No project created for compliance test")
        
        response = api_client.post(f"{API_URL}/compliance/check", json={
            "project_id": self.project_id,
            "jurisdiction": "CURACAO",
            "check_type": "full"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["jurisdiction"] == "CURACAO"
        assert len(data["results"]) >= 3  # CURACAO has 3 checks
    
    def test_run_compliance_check_invalid_project(self, api_client):
        """POST /api/sla113/compliance/check with invalid project should return 404"""
        response = api_client.post(f"{API_URL}/compliance/check", json={
            "project_id": "invalid-project-id",
            "jurisdiction": "GLI"
        })
        assert response.status_code == 404
    
    def test_delete_compliance_report(self, api_client):
        """DELETE /api/sla113/compliance/{id} should delete report"""
        report_id = getattr(TestSLA113Compliance, 'created_report_id', None)
        if not report_id:
            pytest.skip("No report created to delete")
        
        response = api_client.delete(f"{API_URL}/compliance/{report_id}")
        assert response.status_code == 200
        assert response.json()["deleted"] == True
    
    def test_delete_nonexistent_report(self, api_client):
        """DELETE /api/sla113/compliance/{id} with invalid ID should return 404"""
        response = api_client.delete(f"{API_URL}/compliance/CMP-INVALID123")
        assert response.status_code == 404


# ─── DEPLOY ENGINE TESTS ───
class TestSLA113Deploy:
    """Test Deploy Engine - /api/sla113/deploy"""
    
    @pytest.fixture(autouse=True)
    def setup_completed_build(self, api_client):
        """Create a project and completed build for deploy tests"""
        # Create project
        project_data = {
            "name": "TEST_Deploy_Project",
            "game_type": "fish_shooter",
            "theme": "neon",
            "target_platform": "web"
        }
        response = api_client.post(f"{API_URL}/projects", json=project_data)
        if response.status_code == 200:
            self.project_id = response.json()["id"]
        
        # Create build
        build_response = api_client.post(f"{API_URL}/builds", json={
            "project_id": self.project_id,
            "target": "webgl"
        })
        if build_response.status_code == 200:
            self.build_id = build_response.json()["id"]
            
            # Advance build to completion (needs ~14 advances)
            for _ in range(20):
                adv_response = api_client.post(f"{API_URL}/builds/{self.build_id}/advance")
                if adv_response.json().get("status") == "completed":
                    break
        
        yield
        
        # Cleanup
        if hasattr(self, 'build_id'):
            api_client.delete(f"{API_URL}/builds/{self.build_id}")
        if hasattr(self, 'project_id'):
            api_client.delete(f"{API_URL}/projects/{self.project_id}")
    
    def test_list_deployments(self, api_client):
        """GET /api/sla113/deployments should return list of deployments"""
        response = api_client.get(f"{API_URL}/deployments")
        assert response.status_code == 200
        
        data = response.json()
        assert "deployments" in data
        assert "total" in data
        assert isinstance(data["deployments"], list)
    
    def test_create_deployment_from_completed_build(self, api_client):
        """POST /api/sla113/deploy should create deployment from completed build"""
        if not hasattr(self, 'build_id'):
            pytest.skip("No build created for deploy test")
        
        deploy_data = {
            "build_id": self.build_id,
            "target_cdn": "cloudflare",
            "region": "us-west",
            "auto_ssl": True
        }
        response = api_client.post(f"{API_URL}/deploy", json=deploy_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["build_id"] == self.build_id
        assert data["target_cdn"] == "cloudflare"
        assert data["region"] == "us-west"
        assert data["auto_ssl"] == True
        assert data["status"] == "deploying"
        assert data["progress"] == 0
        assert "id" in data
        assert data["id"].startswith("DPL-")
        
        # Store for further tests
        TestSLA113Deploy.created_deploy_id = data["id"]
    
    def test_create_deployment_invalid_build(self, api_client):
        """POST /api/sla113/deploy with invalid build_id should return 404"""
        response = api_client.post(f"{API_URL}/deploy", json={
            "build_id": "BLD-INVALID123",
            "target_cdn": "cloudflare"
        })
        assert response.status_code == 404
    
    def test_create_deployment_incomplete_build(self, api_client):
        """POST /api/sla113/deploy with incomplete build should return 400"""
        if not hasattr(self, 'project_id'):
            pytest.skip("No project for incomplete build test")
        
        # Create a new build but don't complete it
        build_response = api_client.post(f"{API_URL}/builds", json={
            "project_id": self.project_id,
            "target": "apk"
        })
        if build_response.status_code != 200:
            pytest.skip("Could not create incomplete build")
        
        incomplete_build_id = build_response.json()["id"]
        
        # Try to deploy incomplete build
        response = api_client.post(f"{API_URL}/deploy", json={
            "build_id": incomplete_build_id,
            "target_cdn": "aws"
        })
        assert response.status_code == 400
        assert "completed" in response.json().get("detail", "").lower()
        
        # Cleanup incomplete build
        api_client.delete(f"{API_URL}/builds/{incomplete_build_id}")
    
    def test_advance_deployment_to_live(self, api_client):
        """POST /api/sla113/deploy/{id}/advance should advance deployment to live"""
        deploy_id = getattr(TestSLA113Deploy, 'created_deploy_id', None)
        if not deploy_id:
            pytest.skip("No deployment created to advance")
        
        # Advance multiple times to reach live status
        for _ in range(5):
            response = api_client.post(f"{API_URL}/deploy/{deploy_id}/advance")
            assert response.status_code == 200
            
            data = response.json()
            if data["status"] == "live":
                # Verify live deployment has URL
                assert data["url"] is not None
                assert data["progress"] == 100
                assert data["ssl_status"] == "active"
                break
        
        # Verify deployment is live
        final_response = api_client.get(f"{API_URL}/deployments")
        deployments = final_response.json()["deployments"]
        deploy = next((d for d in deployments if d["id"] == deploy_id), None)
        assert deploy is not None
        assert deploy["status"] == "live"
    
    def test_delete_deployment(self, api_client):
        """DELETE /api/sla113/deploy/{id} should delete deployment"""
        deploy_id = getattr(TestSLA113Deploy, 'created_deploy_id', None)
        if not deploy_id:
            pytest.skip("No deployment created to delete")
        
        response = api_client.delete(f"{API_URL}/deploy/{deploy_id}")
        assert response.status_code == 200
        assert response.json()["deleted"] == True
    
    def test_delete_nonexistent_deployment(self, api_client):
        """DELETE /api/sla113/deploy/{id} with invalid ID should return 404"""
        response = api_client.delete(f"{API_URL}/deploy/DPL-INVALID123")
        assert response.status_code == 404


# ─── PIPELINE PULSE TESTS ───
class TestSLA113PipelinePulse:
    """Test Pipeline Pulse functionality - PUT /api/sla113/pipelines/{id}/pulse"""
    
    def test_pulse_existing_pipeline(self, api_client):
        """PUT /api/sla113/pipelines/{id}/pulse should update revenue and executions"""
        # Get existing pipelines
        response = api_client.get(f"{API_URL}/pipelines")
        assert response.status_code == 200
        
        pipelines = response.json()["pipelines"]
        if len(pipelines) == 0:
            pytest.skip("No pipelines available to pulse")
        
        pipeline = pipelines[0]
        original_executions = pipeline.get("executions", 0)
        original_revenue = pipeline.get("revenue", 0)
        
        # Pulse the pipeline
        pulse_response = api_client.put(f"{API_URL}/pipelines/{pipeline['id']}/pulse")
        assert pulse_response.status_code == 200
        
        data = pulse_response.json()
        assert data["heartbeat"] == "active"
        assert data["executions"] == original_executions + 1
        assert data["revenue"] > original_revenue  # Revenue should increase by 50-500
        assert data["revenue"] - original_revenue >= 50
        assert data["revenue"] - original_revenue <= 500
    
    def test_pulse_nonexistent_pipeline(self, api_client):
        """PUT /api/sla113/pipelines/{id}/pulse with invalid ID should return 404"""
        response = api_client.put(f"{API_URL}/pipelines/invalid-pipeline-id/pulse")
        assert response.status_code == 404
    
    def test_pulse_all_pipelines(self, api_client):
        """Pulse all pipelines and verify total revenue increases"""
        # Get initial state
        initial_response = api_client.get(f"{API_URL}/pipelines")
        assert initial_response.status_code == 200
        
        initial_total = initial_response.json()["total_revenue"]
        pipelines = initial_response.json()["pipelines"]
        
        if len(pipelines) == 0:
            pytest.skip("No pipelines available to pulse")
        
        # Pulse all pipelines
        for p in pipelines:
            api_client.put(f"{API_URL}/pipelines/{p['id']}/pulse")
        
        # Verify total revenue increased
        final_response = api_client.get(f"{API_URL}/pipelines")
        final_total = final_response.json()["total_revenue"]
        
        assert final_total > initial_total
        # Each pulse adds 50-500, so total should increase by at least 50 * num_pipelines
        assert final_total - initial_total >= 50 * len(pipelines)


# ─── FULL FLOW TEST ───
class TestSLA113FullFlow:
    """Test complete flow: Create build -> advance to completion -> deploy to CDN -> advance to live"""
    
    def test_full_build_deploy_flow(self, api_client):
        """Test complete build and deploy workflow"""
        # 1. Create project
        project_response = api_client.post(f"{API_URL}/projects", json={
            "name": "TEST_Full_Flow_Project",
            "game_type": "fish_shooter",
            "theme": "neon",
            "target_platform": "web"
        })
        assert project_response.status_code == 200
        project_id = project_response.json()["id"]
        
        try:
            # 2. Create build
            build_response = api_client.post(f"{API_URL}/builds", json={
                "project_id": project_id,
                "target": "webgl",
                "optimization": "balanced"
            })
            assert build_response.status_code == 200
            build_id = build_response.json()["id"]
            assert build_response.json()["status"] == "queued"
            
            # 3. Advance build to completion (needs ~14 advances)
            for _ in range(20):
                adv_response = api_client.post(f"{API_URL}/builds/{build_id}/advance")
                assert adv_response.status_code == 200
                if adv_response.json()["status"] == "completed":
                    break
            
            # Verify build is completed
            build_check = api_client.get(f"{API_URL}/builds")
            build = next((b for b in build_check.json()["builds"] if b["id"] == build_id), None)
            assert build is not None
            assert build["status"] == "completed"
            assert build["output"] is not None
            
            # 4. Deploy to CDN
            deploy_response = api_client.post(f"{API_URL}/deploy", json={
                "build_id": build_id,
                "target_cdn": "cloudflare",
                "region": "global",
                "auto_ssl": True
            })
            assert deploy_response.status_code == 200
            deploy_id = deploy_response.json()["id"]
            assert deploy_response.json()["status"] == "deploying"
            
            # 5. Advance deployment to live
            for _ in range(5):
                prop_response = api_client.post(f"{API_URL}/deploy/{deploy_id}/advance")
                assert prop_response.status_code == 200
                if prop_response.json()["status"] == "live":
                    break
            
            # Verify deployment is live
            deploy_check = api_client.get(f"{API_URL}/deployments")
            deploy = next((d for d in deploy_check.json()["deployments"] if d["id"] == deploy_id), None)
            assert deploy is not None
            assert deploy["status"] == "live"
            assert deploy["url"] is not None
            assert "cdn.cloudflare.com" in deploy["url"]
            assert deploy["ssl_status"] == "active"
            
            print(f"Full flow completed successfully!")
            print(f"  Project: {project_id}")
            print(f"  Build: {build_id} -> {build['output']} ({build['size_mb']} MB)")
            print(f"  Deploy: {deploy_id} -> {deploy['url']}")
            
            # Cleanup
            api_client.delete(f"{API_URL}/deploy/{deploy_id}")
            api_client.delete(f"{API_URL}/builds/{build_id}")
            
        finally:
            # Always cleanup project
            api_client.delete(f"{API_URL}/projects/{project_id}")
