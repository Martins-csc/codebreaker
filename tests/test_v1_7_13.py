import os
import py_compile

import pytest


def test_v1_7_13_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_v1_7_13_source_scan():
    """Source scan: _XLINK_CSS injected with unsafe_allow_html=True, zero case-insensitive JOURNAL string literals outside icon shortcode."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. _XLINK_CSS and unsafe_allow_html=True present
    assert "_XLINK_CSS" in content
    assert "st.markdown(_XLINK_CSS, unsafe_allow_html=True)" in content

    # 2. Zero case-insensitive "JOURNAL" string literals outside `:material_journal:`
    lines = content.splitlines()
    for line in lines:
        if "journal" in line.lower():
            # Must be the material icon shortcode line
            assert ":material_journal:" in line or "material_journal" in line
            assert "JOURNAL" not in line
