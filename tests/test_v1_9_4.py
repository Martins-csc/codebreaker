import os
import py_compile

import pytest


def test_v1_9_4_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    ai_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(ai_path, doraise=True)


def test_v1_9_4_source_scan():
    """Source scan: zero 'Signed out successfully', pre-warm calls relocated to Dashboard via needs_prewarm."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Signed out successfully" not in content
    assert "Logged out successfully!" in content
    assert "needs_prewarm" in content
    assert content.count("needs_prewarm") >= 4
    assert 'if st.session_state.get("needs_prewarm"):' in content
