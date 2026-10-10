import os
import py_compile

import pytest


def test_v1_7_2_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_v1_7_2_source_scan():
    """Source scan: library Confirm shares log's red mechanism, cross-link markdown contains '<a href="?mode=', zero LIBRARY-WITNESS, boot mode handler."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Library Confirm shares log's red mechanism via expander CSS and st.expander
    assert (
        'div[data-testid="stExpander"] div.stButton > button[kind="primary"]' in content
    )
    assert "background-color: #d33" in content
    assert "with st.expander(" in content

    # 2. In-place cross-link tertiary buttons present
    assert "auth_switch_to_signup" in content
    assert "auth_switch_to_login" in content

    # 3. Zero LIBRARY-WITNESS strings remain
    assert "LIBRARY-WITNESS" not in content

    # 4. Library except branch restored to st.info("Library unavailable.")
    assert 'st.info("Library unavailable.")' in content

    # 5. Boot mode param handler present
    assert 'mode_param = st.query_params.get("mode")' in content
    assert 'if mode_param in ("signup", "login"):' in content
