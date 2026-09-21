"""SLA113 Genesis Engine — deterministic math, pipeline artifacts, and API contract.

Runs in-process with no database, no network, and no LLM key.
"""
import io
import json
import zipfile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from routers.sla113_genesis import router
from sla113.genesis.logic import verify_math
from sla113.genesis.models import GameSpec
from sla113.genesis.pipeline import GenesisPipeline, job_dir


@pytest.fixture(autouse=True)
def _workdir(tmp_path, monkeypatch):
    monkeypatch.setenv("SLA113_GENESIS_WORKDIR", str(tmp_path))


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router, prefix="/api")
    return TestClient(app)


# ── math ──

def test_default_model_is_exactly_96_5_percent_and_verified():
    v = verify_math(GameSpec(seed=113))
    assert v["theoretical_rtp"] == pytest.approx(0.965, abs=1e-12)
    assert v["verification_status"] == "verified"
    assert v["regulatory_certification"] is False


def test_math_is_reproducible():
    spec = GameSpec(seed=113, shots_per_round=2000)
    assert verify_math(spec) == verify_math(spec)


def test_unseeded_math_is_still_reproducible():
    spec = GameSpec(shots_per_round=2000)
    assert verify_math(spec) == verify_math(spec)


def test_target_mismatch_is_flagged_not_hidden():
    v = verify_math(GameSpec(target_rtp=0.50, seed=113, shots_per_round=1000))
    assert v["target_matches_model"] is False
    assert v["verification_status"] == "review_required"


def test_custom_weights_change_the_rtp():
    spec = GameSpec(paytable={"a": 0.5, "b": 2.0}, hit_weights={"a": 3, "b": 1}, target_rtp=0.875, seed=1)
    v = verify_math(spec)
    assert v["probabilities"] == {"a": 0.75, "b": 0.25}
    assert v["theoretical_rtp"] == pytest.approx(0.875)
    assert v["verification_status"] == "verified"


def test_simulation_agrees_with_theory():
    v = verify_math(GameSpec(seed=7, shots_per_round=200_000))
    assert v["simulation_within_tolerance"] is True
    assert abs(v["simulated_rtp"] - v["theoretical_rtp"]) < 0.02


# ── spec validation ──

@pytest.mark.parametrize("kwargs", [
    {"paytable": {}},
    {"paytable": {"small": -1.0}},
    {"paytable": {"mystery": 1.0}},  # no canonical weight and no hit_weights
    {"paytable": {"a": 1.0}, "hit_weights": {"b": 1.0}},
    {"paytable": {"a": 1.0}, "hit_weights": {"a": 0.0}},
])
def test_bad_specs_are_rejected(kwargs):
    with pytest.raises(ValidationError):
        GameSpec(**kwargs)


# ── pipeline ──

def test_pipeline_produces_every_artifact():
    result = GenesisPipeline().run(GameSpec(name="Test Genesis", seed=113, shots_per_round=1000))
    root = job_dir(result["job_id"])
    assert result["status"] == "complete"
    assert result["stages_completed"][-1] == "DESCRIBED"
    for rel in ["web/index.html", "web/manifest.json", "verification.json", "deployment.json", result["build"]["web_zip"]]:
        assert (root / rel).is_file(), rel
    deploy = json.loads((root / "deployment.json").read_text())
    assert deploy["deployed"] is False


def test_playable_build_carries_the_verified_math():
    spec = GameSpec(paytable={"a": 0.5, "b": 2.0}, hit_weights={"a": 3, "b": 1}, target_rtp=0.875, seed=1)
    result = GenesisPipeline().run(spec)
    page = (job_dir(result["job_id"]) / "web" / "index.html").read_text()
    runtime = json.loads(page.split("window.GENESIS=", 1)[1].split(";</script>", 1)[0])
    assert runtime["paytable"] == {"a": 0.5, "b": 2.0}
    assert runtime["probabilities"] == {"a": 0.75, "b": 0.25}
    assert result["manifest"]["composer"]["uses_verified_math"] is True


def test_zip_is_self_contained():
    result = GenesisPipeline().run(GameSpec(seed=113, shots_per_round=1000))
    names = set(zipfile.ZipFile(job_dir(result["job_id"]) / result["build"]["web_zip"]).namelist())
    assert "web/index.html" in names and "verification.json" in names
    assert any(n.startswith("web/assets/") and n.endswith(".svg") for n in names)
    assert any(n.startswith("web/audio/") and n.endswith(".wav") for n in names)


def test_game_name_cannot_inject_markup():
    result = GenesisPipeline().run(GameSpec(name="</script><script>alert(1)</script>", seed=1, shots_per_round=100))
    page = (job_dir(result["job_id"]) / "web" / "index.html").read_text()
    assert "</script><script>alert(1)" not in page


# ── API ──

def test_api_status(client):
    body = client.get("/api/sla113/genesis/status").json()
    assert body["math"] == "deterministic" and body["llm_calls"] is False


def test_api_generate_then_download(client):
    r = client.post("/api/sla113/genesis/generate", json={"spec": {"name": "API Game", "seed": 113, "shots_per_round": 1000}})
    assert r.status_code == 200, r.text
    body = r.json()
    assert "workspace" not in body  # server paths are not exposed
    d = client.get(f"/api/sla113/genesis/jobs/{body['job_id']}/download")
    assert d.status_code == 200
    assert "web/index.html" in zipfile.ZipFile(io.BytesIO(d.content)).namelist()


def test_api_rejects_bad_spec(client):
    assert client.post("/api/sla113/genesis/verify", json={"paytable": {"small": -1}}).status_code == 422


@pytest.mark.parametrize("job_id", ["../etc", "genesis_" + "0" * 32, "nope"])
def test_api_download_refuses_unknown_or_malformed_jobs(client, job_id):
    assert client.get(f"/api/sla113/genesis/jobs/{job_id}/download").status_code == 404
