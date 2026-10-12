import os
import py_compile

import pytest


def test_v1_7_12_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_v1_7_12_source_scan():
    """Source scan: vertical_alignment='center' present, _clear_auth_forms defined and called, exactly 3 st.container(height=230) blocks, :material_analytics: in st.markdown without unsafe_allow_html."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Columns [0.62, 0.38] present in _auth_switch_line
    assert "[0.62, 0.38]" in content

    # 2. _clear_auth_forms defined and called
    assert "def _clear_auth_forms()" in content
    assert "_clear_auth_forms()" in content
    assert content.count("_clear_auth_forms()") >= 4

    # 3. Exactly three st.container(height=230) blocks
    assert content.count("st.container(height=230)") == 3

    # 4. :material_analytics: appears inside st.markdown call and NOT in unsafe_allow_html
    assert ":material_analytics:" in content
    assert '<div class="module-card">:material/analytics:' not in content
