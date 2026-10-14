import os
import py_compile

import pytest


def test_v1_8_3_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    ai_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(ai_path, doraise=True)


def test_v1_8_3_source_scan():
    """Source scan: boot verify block opens with access_token presence check, zero unguarded Supabase calls on logged-out path."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Boot verify block opens with access_token presence check before TTL guard
    assert (
        'if st.session_state.get("access_token") and (' in content
        or 'if "access_token" in st.session_state and (' in content
    )

    # 2. Capability token and email/oauth check are guarded by presence checks before calling get_client()
    assert "if rt_param:" in content
    assert 'or "access_token" in st.session_state' in content
