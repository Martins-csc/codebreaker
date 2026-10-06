import os
import py_compile

import pytest


def test_v1_6_3_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_v1_6_3_nav_radio_source_scan():
    """Assert no st.session_state["nav_radio"] = appears after the radio creation line in app.py."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    radio_line_idx = -1
    for idx, line in enumerate(lines):
        if 'key="nav_radio"' in line:
            radio_line_idx = idx
            break

    assert radio_line_idx != -1, "nav_radio widget instantiation key not found"

    # Scan all lines AFTER radio instantiation for assignments to session_state["nav_radio"] or session_state['nav_radio']
    for idx in range(radio_line_idx + 1, len(lines)):
        line = lines[idx]
        assert (
            'session_state["nav_radio"]' not in line
        ), f"Found post-instantiation nav_radio assignment on line {idx+1}: {line}"
        assert (
            "session_state['nav_radio']" not in line
        ), f"Found post-instantiation nav_radio assignment on line {idx+1}: {line}"

    # Assert nav_pending pattern is applied at top before radio creation
    nav_pending_idx = content.find("nav_pending")
    assert nav_pending_idx != -1, "nav_pending pattern not found in app.py"
    assert nav_pending_idx < content.find(
        'key="nav_radio"'
    ), "nav_pending logic must appear before radio widget creation"


def test_v1_6_3_ai_key_presence_diagnostic():
    """Assert Persistence Debug lists provider keys (GROQ_API_KEY, GEMINI_API_KEY) with PRESENT or MISSING (names and presence only)."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "GROQ_API_KEY" in content
    assert "GEMINI_API_KEY" in content
    assert "PRESENT" in content
    assert "MISSING" in content
