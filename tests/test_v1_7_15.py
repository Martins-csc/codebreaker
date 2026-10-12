import os
import py_compile

import pytest


def test_v1_7_15_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_v1_7_15_source_scan():
    """Source scan: _XLINK_CSS injected before _ROOT / auth code, contains [disabled] black override and :not([disabled]) blue rule."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. _XLINK_CSS present
    assert "_XLINK_CSS = " in content
    assert "st.markdown(_XLINK_CSS, unsafe_allow_html=True)" in content

    # 2. _XLINK_CSS appears before _ROOT (first-paint CSS law)
    xlink_pos = content.find("_XLINK_CSS")
    root_pos = content.find("_ROOT = st.empty()")
    set_page_pos = content.find("st.set_page_config")
    assert set_page_pos < xlink_pos < root_pos

    # 3. CSS rules present
    assert 'button[data-testid="stBaseButton-tertiary"][disabled]' in content
    assert "color: #111111;" in content
    assert 'button[data-testid="stBaseButton-tertiary"]:not([disabled])' in content
    assert "color: #1a73e8;" in content
