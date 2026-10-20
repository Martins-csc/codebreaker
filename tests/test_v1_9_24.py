import os
import py_compile

import pytest


def test_v1_9_24_py_compile():
    """Assert app.py compiles successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    assert py_compile.compile(app_path, doraise=True)


def test_v1_9_24_session_state_oauth():
    """Source scan: app.py uses st.session_state["pending_oauth_state"] for OAuth state persistence."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert 'st.session_state["pending_oauth_state"] = state' in content
    assert 'state = st.session_state.get("pending_oauth_state")' in content
    assert 'st.session_state.pop("pending_oauth_state", None)' in content
    assert 'st.error("Login session expired or invalid.")' in content
