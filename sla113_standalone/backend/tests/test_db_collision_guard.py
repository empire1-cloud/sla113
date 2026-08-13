"""Tests for the DB_NAME collision guard.

Verifies that the standalone refuses to connect to known monolith
database names unless COLLISION_BYPASS is set.
"""
import os
import pytest
from app.core.database import _guard_collision, PROTECTED_DB_NAMES


def test_protected_names_known():
    assert "sla113" in PROTECTED_DB_NAMES
    assert "sla113_db" in PROTECTED_DB_NAMES


def test_standalone_default_is_safe():
    assert "sla113_standalone" not in PROTECTED_DB_NAMES


def test_guard_raises_on_sla113():
    with pytest.raises(RuntimeError, match="SAFETY GUARD TRIGGERED"):
        _guard_collision("sla113")


def test_guard_raises_on_sla113_db():
    with pytest.raises(RuntimeError, match="SAFETY GUARD TRIGGERED"):
        _guard_collision("sla113_db")


def test_guard_passes_on_standalone_default():
    # Should not raise for the standalone's default DB name
    _guard_collision("sla113_standalone")


def test_guard_passes_on_custom_name():
    _guard_collision("my_custom_game_db")


def test_guard_bypasses_with_env(monkeypatch):
    monkeypatch.setenv("COLLISION_BYPASS", "true")
    # Should not raise even for protected names
    _guard_collision("sla113")
    _guard_collision("sla113_db")


def test_guard_still_raises_with_false_bypass(monkeypatch):
    monkeypatch.setenv("COLLISION_BYPASS", "false")
    with pytest.raises(RuntimeError, match="SAFETY GUARD TRIGGERED"):
        _guard_collision("sla113")
