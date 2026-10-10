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
    """Source scan: library Confirm shares log's red mechanism, anchor cross-links, centering columns, reload block and rebind loop."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Library Confirm shares log's red mechanism (expander mechanism)
    assert 'div[data-testid="stExpander"]' in content
    assert "background-color: #d33" in content

    # 2. In-place cross-link tertiary buttons present
    assert "auth_switch_to_signup" in content
    assert "auth_switch_to_login" in content

    # 3. Centering columns present: st.columns([0.3, 0.4, 0.3])
    assert (
        "st.columns([0.3, 0.4, 0.3])" in content
        or "st.columns([0.3,0.4,0.3])" in content
    )

    # 4. Reload block present with rebind loop
    assert "_importlib.reload(ai_engine)" in content
    assert "_AE_MT = _os.path.getmtime(ai_engine.__file__)" in content
    assert 'st.session_state.get("_ae_mt") != _AE_MT' in content
    assert "for _n in (" in content
    assert "globals()[_n] = getattr(ai_engine, _n)" in content
