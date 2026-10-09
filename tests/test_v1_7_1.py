import os
import py_compile

import pytest


def test_v1_7_1_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_v1_7_1_source_scan():
    """Source scan: library Confirm shares log's red mechanism, tertiary switch buttons, centering columns, CSS, reload block and rebind loop."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Library Confirm shares log's red mechanism (container CSS matching expander mechanism)
    assert 'div[data-testid="stContainer"]' in content
    assert 'div[data-testid="stExpander"]' in content
    assert "background-color: #d33" in content

    # 2. Tertiary switch buttons with type="tertiary", use_container_width=True, existing keys
    assert "Don't have an account? Sign up" in content
    assert "Already have an account? Log in" in content
    assert 'type="tertiary"' in content
    assert "use_container_width=True" in content
    assert 'key="auth_switch_to_signup"' in content
    assert 'key="auth_switch_to_login"' in content

    # 3. Centering columns present: st.columns([0.25, 0.5, 0.25])
    assert (
        "st.columns([0.25, 0.5, 0.25])" in content
        or "st.columns([0.25,0.5,0.25])" in content
        or "st.columns([0.25, 0.5, 0.25])" in content
    )

    # 4. CSS for tertiary button present
    assert 'div[data-testid="stButton"] button[kind="tertiary"]' in content
    assert "color: #1a73e8" in content

    # 5. Reload block present with rebind loop
    assert "_importlib.reload(ai_engine)" in content
    assert "_AE_MT = _os.path.getmtime(ai_engine.__file__)" in content
    assert 'st.session_state.get("_ae_mt") != _AE_MT' in content
    assert "for _n in (" in content
    assert "globals()[_n] = getattr(ai_engine, _n)" in content
