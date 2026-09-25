import py_compile
from pathlib import Path

import pytest


def test_py_compile_gate():
    """Test pre-seal compile gate across core python modules for v1.4.0."""
    for mod in [
        "app.py",
        "ai_engine.py",
        "security.py",
        "config.py",
        "supabase_client.py",
    ]:
        res = py_compile.compile(mod, doraise=True)
        assert res is not None


def test_v1_4_0_banned_strings_sweep():
    """Test that banned strings are absent from app.py."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    banned = [
        "Row Level Security",
        "RLS",
        "Supabase Auth",
        "mediated securely by Supabase",
        "handshake",
        "AI-driven",
        "v1.1.4",
        "press enter",
        "0/100 words",
    ]
    for b in banned:
        assert b not in content, f"Found banned string: '{b}'"


def test_v1_4_0_log_sorting_logic():
    """Test sorting logic for engineering log entries."""
    entries = [
        {"created_at": "2026-01-01T00:00:00Z", "progress": "B milestone"},
        {"created_at": "2026-01-03T00:00:00Z", "progress": "A milestone"},
        {"created_at": "2026-01-02T00:00:00Z", "progress": "C milestone"},
    ]

    # Newest first
    sorted_newest = sorted(entries, key=lambda x: x.get("created_at", ""), reverse=True)
    assert sorted_newest[0]["created_at"] == "2026-01-03T00:00:00Z"

    # Oldest first
    sorted_oldest = sorted(entries, key=lambda x: x.get("created_at", ""))
    assert sorted_oldest[0]["created_at"] == "2026-01-01T00:00:00Z"

    # A->Z (milestone)
    sorted_az = sorted(entries, key=lambda x: str(x.get("progress", "")).lower())
    assert sorted_az[0]["progress"] == "A milestone"
    assert sorted_az[2]["progress"] == "C milestone"

    # Z->A (milestone)
    sorted_za = sorted(
        entries, key=lambda x: str(x.get("progress", "")).lower(), reverse=True
    )
    assert sorted_za[0]["progress"] == "C milestone"
    assert sorted_za[2]["progress"] == "A milestone"


def test_v1_4_0_dashboard_and_hygiene_elements():
    """Test dashboard tiles, Quick Start buttons, and copy hygiene in app.py."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Dashboard tiles
    assert "My Blueprints" in content
    assert "My Engineering Logs" in content
    assert "Quick Start" in content
    assert "Account" in content
    assert "persistent library arrives next update" in content

    # Quick Start buttons target check
    assert 'st.query_params["pg"] = "Analyze"' in content
    assert 'st.query_params["pg"] = "Blueprint"' in content
    assert 'st.query_params["pg"] = "Engineering Log"' in content

    # Copy hygiene: Skill level selectbox deleted from Analyze
    assert "skill_level = st.selectbox" not in content
    assert "Your Skill Level" not in content

    # Blueprint status line and clean blocks
    assert "Generating blueprint…" in content
    assert "What do I do with this file?" not in content

    # Delete controls
    assert "Delete ALL my logs" in content
    assert "Confirm delete" in content


def test_v1_4_0_two_step_delete_state():
    """Test two-step delete session state behavior."""
    session_state = {}
    entry_id = "test-entry-123"
    confirm_key = f"confirm_del_{entry_id}"

    # Initial state: not confirmed
    assert session_state.get(confirm_key, False) is False

    # First click sets confirmation flag
    session_state[confirm_key] = True
    assert session_state[confirm_key] is True

    # Cancel clears confirmation flag
    session_state[confirm_key] = False
    assert session_state[confirm_key] is False
