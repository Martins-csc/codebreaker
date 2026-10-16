import os
import py_compile

import pytest


def test_v1_8_6_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    ai_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(ai_path, doraise=True)


def test_v1_8_6_source_scan():
    """Source scan: end-of-run recording lines, tag completeness, and probe display."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. End-of-run recording lines are present at script end
    assert (
        'st.session_state["last_run_ms"] = round((time.time() - _run_start) * 1000, 1)'
        in content
    )
    assert (
        'st.session_state["last_sb_calls"] = st.session_state.get("sb_calls", 0)'
        in content
    )
    assert (
        'st.session_state["last_sb_tags"] = list(st.session_state.get("sb_tags", []))'
        in content
    )

    # 2. Probe displays last_run_ms, last_sb_calls, last_sb_tags
    assert "Last Completed Run (ms)" in content
    assert "Last Completed Run Supabase Calls" in content
    assert "Last Completed Run Supabase Tags" in content

    # 3. Tag completeness: zero raw get_client outside _track_client definition
    # Count occurrences of get_client() across app.py
    lines = content.splitlines()
    get_client_calls = 0
    for line in lines:
        if (
            "get_client()" in line
            and "def _track_client" not in line
            and "def get_client" not in line
            and "from supabase_client" not in line
            and "return get_client()" not in line
        ):
            get_client_calls += 1
    assert (
        get_client_calls == 0
    ), f"Found {get_client_calls} raw get_client() call sites outside definition"
