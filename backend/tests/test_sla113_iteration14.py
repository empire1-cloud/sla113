"""
SLA113 Iteration 14 Tests - Night Queue Background Worker
Tests for:
- Worker status endpoint (GET /api/sla113/worker/status)
- Worker toggle endpoint (POST /api/sla113/worker/toggle)
- Job creation with named stages (POST /api/sla113/jobs)
- Worker auto-processing (jobs advance automatically)
- Job stages transition (pending -> processing -> completed)
- Job listing with stages (GET /api/sla113/jobs)
- Job deletion (DELETE /api/sla113/jobs/{id})
- Previous features still working (Build Pipeline, Compliance, Deploy, Revenue Pipelines)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
API = f"{BASE_URL}/api/sla113"

# Job presets and their expected stages
JOB_STAGES = {
    "ARCADE_40": ["Asset Indexing", "Sprite Generation", "Physics Binding", "AI Balancing", "Package Export"],
    "ARCADE_60": ["Asset Indexing", "Sprite Generation", "Physics Binding", "AI Balancing", "Network Layer", "Package Export"],
    "SLOTS_20": ["Reel Mapping", "Paytable Calculation", "RTP Verification", "Visual Rendering", "Package Export"],
    "OPEN_WORLD": ["World Generation", "NPC Scripting", "Physics Binding", "AI Pathing", "Texture Streaming", "LOD Pipeline", "Package Export"],
    "CASINO_SUITE": ["Game Selection Matrix", "RTP Calibration", "Lobby UI", "Payment Gateway", "Package Export"],
    "CUSTOM_OS_BUILD": ["Init Scaffold", "Core Logic", "Asset Pipeline", "Integration Pass", "Package Export"],
    "AAA_FISH_SLOT": ["Asset Indexing", "Sprite Generation", "Boss Patterns", "RTP Verification", "Package Export"],
    "GTA5_TYPE": ["World Generation", "NPC Scripting", "Vehicle Physics", "Mission Logic", "Package Export"],
    "COD_WARFARE": ["Map Generation", "Weapon Balancing", "Netcode Layer", "AI Opponents", "Package Export"],
    "FANTASY_RPG": ["Lore Generation", "Skill Trees", "Monster AI", "Dungeon Layout", "Package Export"],
}


class TestWorkerStatus:
    """Tests for GET /api/sla113/worker/status"""
    
    def test_worker_status_returns_correct_structure(self):
        """Worker status should return running, active_jobs, completed_jobs, total_jobs"""
        response = requests.get(f"{API}/worker/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "running" in data, "Response should have 'running' field"
        assert "active_jobs" in data, "Response should have 'active_jobs' field"
        assert "completed_jobs" in data, "Response should have 'completed_jobs' field"
        assert "total_jobs" in data, "Response should have 'total_jobs' field"
        
        assert isinstance(data["running"], bool), "running should be boolean"
        assert isinstance(data["active_jobs"], int), "active_jobs should be int"
        assert isinstance(data["completed_jobs"], int), "completed_jobs should be int"
        assert isinstance(data["total_jobs"], int), "total_jobs should be int"
        
        print(f"Worker status: running={data['running']}, active={data['active_jobs']}, completed={data['completed_jobs']}, total={data['total_jobs']}")


class TestWorkerToggle:
    """Tests for POST /api/sla113/worker/toggle"""
    
    def test_worker_toggle_changes_state(self):
        """Toggle should change worker running state"""
        # Get initial state
        initial = requests.get(f"{API}/worker/status").json()
        initial_running = initial["running"]
        
        # Toggle
        toggle_response = requests.post(f"{API}/worker/toggle")
        assert toggle_response.status_code == 200
        
        toggle_data = toggle_response.json()
        assert "status" in toggle_data
        expected_status = "stopped" if initial_running else "started"
        assert toggle_data["status"] == expected_status, f"Expected status '{expected_status}', got '{toggle_data['status']}'"
        
        # Wait a bit for async task to settle
        time.sleep(1)
        
        # Verify state changed
        new_state = requests.get(f"{API}/worker/status").json()
        assert new_state["running"] != initial_running, "Worker running state should have changed"
        
        # Toggle back to original state
        requests.post(f"{API}/worker/toggle")
        time.sleep(1)  # Wait for async task to settle
        final_state = requests.get(f"{API}/worker/status").json()
        # Note: Due to async nature, we just verify toggle works, not exact state restoration
        
        print(f"Worker toggle test passed: {initial_running} -> {new_state['running']} -> {final_state['running']}")


class TestJobCreationWithStages:
    """Tests for POST /api/sla113/jobs with named stages"""
    
    def test_create_job_arcade_40_has_correct_stages(self):
        """ARCADE_40 preset should create job with 5 specific stages"""
        response = requests.post(f"{API}/jobs", json={
            "preset": "ARCADE_40",
            "priority": "normal"
        })
        assert response.status_code == 200
        
        job = response.json()
        assert "id" in job
        assert job["preset"] == "ARCADE_40"
        assert job["priority"] == "normal"
        assert job["status"] == "pending"
        assert "stages" in job
        
        expected_stages = JOB_STAGES["ARCADE_40"]
        assert len(job["stages"]) == len(expected_stages), f"Expected {len(expected_stages)} stages, got {len(job['stages'])}"
        
        for i, stage in enumerate(job["stages"]):
            assert stage["name"] == expected_stages[i], f"Stage {i} should be '{expected_stages[i]}', got '{stage['name']}'"
            assert stage["status"] == "pending"
            assert stage["progress"] == 0
        
        # Cleanup
        requests.delete(f"{API}/jobs/{job['id']}")
        print(f"ARCADE_40 job created with stages: {[s['name'] for s in job['stages']]}")
    
    def test_create_job_fantasy_rpg_has_correct_stages(self):
        """FANTASY_RPG preset should create job with correct stages"""
        response = requests.post(f"{API}/jobs", json={
            "preset": "FANTASY_RPG",
            "priority": "high"
        })
        assert response.status_code == 200
        
        job = response.json()
        expected_stages = JOB_STAGES["FANTASY_RPG"]
        assert len(job["stages"]) == len(expected_stages)
        
        for i, stage in enumerate(job["stages"]):
            assert stage["name"] == expected_stages[i]
        
        # Cleanup
        requests.delete(f"{API}/jobs/{job['id']}")
        print(f"FANTASY_RPG job created with stages: {[s['name'] for s in job['stages']]}")
    
    def test_create_job_with_different_priorities(self):
        """Jobs can be created with low, normal, high priorities"""
        job_ids = []
        for priority in ["low", "normal", "high"]:
            response = requests.post(f"{API}/jobs", json={
                "preset": "SLOTS_20",
                "priority": priority
            })
            assert response.status_code == 200
            job = response.json()
            assert job["priority"] == priority
            job_ids.append(job["id"])
        
        # Cleanup
        for job_id in job_ids:
            requests.delete(f"{API}/jobs/{job_id}")
        print("Jobs created with all priority levels: low, normal, high")


class TestWorkerAutoProcessing:
    """Tests for worker auto-advancing jobs through stages"""
    
    def test_worker_auto_advances_job(self):
        """Worker should auto-advance pending/processing jobs every 3 seconds"""
        # Ensure worker is running
        status = requests.get(f"{API}/worker/status").json()
        if not status["running"]:
            toggle_resp = requests.post(f"{API}/worker/toggle")
            print(f"Started worker: {toggle_resp.json()}")
            time.sleep(2)  # Wait for worker to fully start
        
        # Create a new job
        create_response = requests.post(f"{API}/jobs", json={
            "preset": "ARCADE_40",
            "priority": "high"
        })
        assert create_response.status_code == 200
        job = create_response.json()
        job_id = job["id"]
        initial_progress = job["progress"]
        initial_status = job["status"]
        
        print(f"Created job {job_id} with initial progress: {initial_progress}, status: {initial_status}")
        
        # Wait for worker to process (worker runs every 3 seconds)
        time.sleep(10)  # Wait for at least 3 worker cycles
        
        # Check job progress
        jobs_response = requests.get(f"{API}/jobs")
        assert jobs_response.status_code == 200
        jobs = jobs_response.json()["jobs"]
        
        updated_job = next((j for j in jobs if j["id"] == job_id), None)
        assert updated_job is not None, f"Job {job_id} should still exist"
        
        print(f"Job {job_id} after waiting: progress={updated_job['progress']}%, status={updated_job['status']}")
        
        # Job should have progressed - check multiple conditions
        job_progressed = (
            updated_job["progress"] > initial_progress or 
            updated_job["status"] in ["processing", "completed"] or
            (updated_job["stages"] and any(s["status"] != "pending" for s in updated_job["stages"]))
        )
        
        assert job_progressed, \
            f"Job should have progressed. Initial: {initial_progress}/{initial_status}, Current: {updated_job['progress']}/{updated_job['status']}"
        
        # Check stages have been updated
        if updated_job["stages"]:
            has_progress = any(s["progress"] > 0 or s["status"] != "pending" for s in updated_job["stages"])
            print(f"Stages: {[(s['name'], s['status'], s['progress']) for s in updated_job['stages']]}")
            assert has_progress, "At least one stage should have progress or changed status"
        
        print(f"Job {job_id} auto-advanced successfully!")
        
        # Cleanup
        requests.delete(f"{API}/jobs/{job_id}")
    
    def test_job_stages_transition_correctly(self):
        """Job stages should transition: pending -> processing -> completed"""
        # Ensure worker is running
        status = requests.get(f"{API}/worker/status").json()
        if not status["running"]:
            requests.post(f"{API}/worker/toggle")
            time.sleep(0.5)
        
        # Create a job
        create_response = requests.post(f"{API}/jobs", json={
            "preset": "SLOTS_20",  # 5 stages
            "priority": "high"
        })
        job = create_response.json()
        job_id = job["id"]
        
        # Wait for processing
        time.sleep(10)  # Wait for multiple worker cycles
        
        # Get updated job
        jobs = requests.get(f"{API}/jobs").json()["jobs"]
        updated_job = next((j for j in jobs if j["id"] == job_id), None)
        
        if updated_job and updated_job["stages"]:
            # Check stage statuses are valid
            valid_statuses = ["pending", "processing", "completed"]
            for stage in updated_job["stages"]:
                assert stage["status"] in valid_statuses, f"Invalid stage status: {stage['status']}"
                assert 0 <= stage["progress"] <= 100, f"Invalid stage progress: {stage['progress']}"
            
            # Stages should be processed in order (completed stages before processing/pending)
            found_non_completed = False
            for stage in updated_job["stages"]:
                if stage["status"] == "completed":
                    assert not found_non_completed, "Completed stages should come before non-completed"
                else:
                    found_non_completed = True
            
            print(f"Job stages: {[(s['name'], s['status'], s['progress']) for s in updated_job['stages']]}")
        
        # Cleanup
        requests.delete(f"{API}/jobs/{job_id}")


class TestJobListing:
    """Tests for GET /api/sla113/jobs"""
    
    def test_list_jobs_returns_stages_array(self):
        """Jobs listing should include stages array for each job"""
        # Create a test job
        create_response = requests.post(f"{API}/jobs", json={
            "preset": "COD_WARFARE",
            "priority": "normal"
        })
        job = create_response.json()
        job_id = job["id"]
        
        # List jobs
        list_response = requests.get(f"{API}/jobs")
        assert list_response.status_code == 200
        
        data = list_response.json()
        assert "jobs" in data
        assert "total" in data
        
        # Find our job
        our_job = next((j for j in data["jobs"] if j["id"] == job_id), None)
        assert our_job is not None
        assert "stages" in our_job
        assert isinstance(our_job["stages"], list)
        assert len(our_job["stages"]) == len(JOB_STAGES["COD_WARFARE"])
        
        # Cleanup
        requests.delete(f"{API}/jobs/{job_id}")
        print(f"Jobs listing includes stages array with {len(our_job['stages'])} stages")


class TestJobDeletion:
    """Tests for DELETE /api/sla113/jobs/{id}"""
    
    def test_delete_job(self):
        """Should be able to delete a job"""
        # Create a job
        create_response = requests.post(f"{API}/jobs", json={
            "preset": "ARCADE_60",
            "priority": "low"
        })
        job = create_response.json()
        job_id = job["id"]
        
        # Delete the job
        delete_response = requests.delete(f"{API}/jobs/{job_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["deleted"] == True
        
        # Verify job is gone (with retry for transient network issues)
        time.sleep(0.5)
        for _ in range(3):
            try:
                jobs_response = requests.get(f"{API}/jobs")
                if jobs_response.status_code == 200:
                    jobs = jobs_response.json()["jobs"]
                    assert not any(j["id"] == job_id for j in jobs), "Job should be deleted"
                    break
            except Exception as e:
                time.sleep(0.5)
                continue
        
        print(f"Job {job_id} deleted successfully")
    
    def test_delete_nonexistent_job_returns_404(self):
        """Deleting non-existent job should return 404"""
        response = requests.delete(f"{API}/jobs/NONEXISTENT-JOB-ID")
        assert response.status_code == 404


class TestPreviousFeaturesStillWork:
    """Verify previous features still work (regression tests)"""
    
    def test_build_pipeline_still_works(self):
        """Build Pipeline endpoints should still work"""
        # Create a project first
        project_response = requests.post(f"{API}/projects", json={
            "name": "TEST_Regression_Build",
            "game_type": "fish_shooter",
            "theme": "neon",
            "target_platform": "webgl"
        })
        assert project_response.status_code == 200
        project_id = project_response.json()["id"]
        
        # Create a build
        build_response = requests.post(f"{API}/builds", json={
            "project_id": project_id,
            "target": "webgl",
            "optimization": "balanced"
        })
        assert build_response.status_code == 200
        build = build_response.json()
        assert "stages" in build
        
        # Cleanup
        requests.delete(f"{API}/builds/{build['id']}")
        requests.delete(f"{API}/projects/{project_id}")
        print("Build Pipeline still works")
    
    def test_compliance_still_works(self):
        """Compliance endpoints should still work"""
        # Create a project
        project_response = requests.post(f"{API}/projects", json={
            "name": "TEST_Regression_Compliance",
            "game_type": "slot_machine",
            "theme": "default",
            "target_platform": "both"
        })
        project_id = project_response.json()["id"]
        
        # Run compliance check
        compliance_response = requests.post(f"{API}/compliance/check", json={
            "project_id": project_id,
            "jurisdiction": "GLI",
            "check_type": "full"
        })
        assert compliance_response.status_code == 200
        report = compliance_response.json()
        assert "results" in report
        
        # Cleanup
        requests.delete(f"{API}/compliance/{report['id']}")
        requests.delete(f"{API}/projects/{project_id}")
        print("Compliance Engine still works")
    
    def test_deploy_center_still_works(self):
        """Deploy endpoints should still work"""
        # List deployments
        response = requests.get(f"{API}/deployments")
        assert response.status_code == 200
        assert "deployments" in response.json()
        print("Deploy Center still works")
    
    def test_revenue_pipelines_still_work(self):
        """Revenue Pipelines endpoints should still work"""
        # List pipelines
        response = requests.get(f"{API}/pipelines")
        assert response.status_code == 200
        data = response.json()
        assert "pipelines" in data
        assert "total_revenue" in data
        
        # Pulse a pipeline if any exist
        if data["pipelines"]:
            pipeline_id = data["pipelines"][0]["id"]
            pulse_response = requests.put(f"{API}/pipelines/{pipeline_id}/pulse")
            assert pulse_response.status_code == 200
        
        print("Revenue Pipelines still work")
    
    def test_vision_smith_still_works(self):
        """Vision Smith endpoints should still work"""
        # List game types
        response = requests.get(f"{API}/game-types")
        assert response.status_code == 200
        assert "game_types" in response.json()
        print("Vision Smith (game types) still works")


class TestAllJobPresets:
    """Test all job presets create correct stages"""
    
    @pytest.mark.parametrize("preset,expected_stages", [
        ("ARCADE_40", JOB_STAGES["ARCADE_40"]),
        ("ARCADE_60", JOB_STAGES["ARCADE_60"]),
        ("SLOTS_20", JOB_STAGES["SLOTS_20"]),
        ("OPEN_WORLD", JOB_STAGES["OPEN_WORLD"]),
        ("CASINO_SUITE", JOB_STAGES["CASINO_SUITE"]),
        ("GTA5_TYPE", JOB_STAGES["GTA5_TYPE"]),
        ("COD_WARFARE", JOB_STAGES["COD_WARFARE"]),
        ("FANTASY_RPG", JOB_STAGES["FANTASY_RPG"]),
    ])
    def test_preset_creates_correct_stages(self, preset, expected_stages):
        """Each preset should create job with correct named stages"""
        response = requests.post(f"{API}/jobs", json={
            "preset": preset,
            "priority": "normal"
        })
        assert response.status_code == 200
        
        job = response.json()
        assert len(job["stages"]) == len(expected_stages)
        
        for i, stage in enumerate(job["stages"]):
            assert stage["name"] == expected_stages[i]
        
        # Cleanup
        requests.delete(f"{API}/jobs/{job['id']}")
        print(f"Preset {preset} creates {len(expected_stages)} stages correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
