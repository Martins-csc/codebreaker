import os
import py_compile

import pytest


def test_v1_8_4_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    ai_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(ai_path, doraise=True)


def test_v1_8_4_source_scan():
    """Source scan: root-wrap enclosure, ghost probe fields, and sb_calls tracking."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Root container wrapping check
    assert "_ROOT = st.empty()" in content
    assert "with _ROOT.container():" in content

    # 2. Ghost probe telemetry fields in Persistence Debug
    assert "Token Present" in content
    assert "Auth Verified Age" in content
    assert "Last Completed Run" in content
    assert "Supabase Calls" in content

    # 3. Supabase call tracking helper
    assert "_track_client" in content
    assert "sb_calls" in content
    assert "last_run_ms" in content
