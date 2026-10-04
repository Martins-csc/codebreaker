import py_compile
from unittest.mock import MagicMock, patch

import pytest


def test_py_compile_gate():
    """Test pre-seal compile gate across core python modules for v1.5.0."""
    for mod in [
        "app.py",
        "ai_engine.py",
        "security.py",
        "config.py",
        "supabase_client.py",
    ]:
        res = py_compile.compile(mod, doraise=True)
        assert res is not None


def test_v1_5_0_persistent_blueprint_library_code():
    """Assert codebase implements persistent blueprint library requirements for v1.5.0."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Analyze auto-save inserts into public.blueprints and stores active_blueprint_id
    assert 'client.table("blueprints").insert(' in content
    assert '"active_blueprint_id"' in content

    # 2. Home library list queries public.blueprints, renders Open button with redirect
    assert 'client.table("blueprints")' in content
    assert "Saved Blueprints" in content
    assert '"Open"' in content
    assert 'st.query_params["pg"] = "Blueprint"' in content

    # 3. Blueprint page loads from DB using active_blueprint_id
    assert 'active_bp_id = st.session_state.get("active_blueprint_id")' in content
    assert "Open a blueprint from your library or generate a new one." in content


def test_v1_5_2_requirements():
    """Assert codebase implements v1.5.2 blueprint refresh-restore and save visibility requirements."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Blueprint default load queries most recent row when active_blueprint_id missing
    assert 'order("created_at", desc=True)' in content
    assert ".limit(1)" in content

    # 2. Save failure wraps auto-save in try/except with st.warning
    assert "Blueprint generated but could not be saved to your library:" in content

    # 3. Home list queries public.blueprints on every render
    assert 'client.table("blueprints")' in content
