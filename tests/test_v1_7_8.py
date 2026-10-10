import os
import py_compile

import pytest


def test_v1_7_8_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_v1_7_8_source_scan():
    """Source scan: config.toml has primaryColor and toolbarMode, app.py has _ROOT = st.empty() and with _ROOT.container():, inner columns [0.72, 0.28], alignment CSS."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        app_content = f.read()

    # 1. Root container repaint pattern present
    assert "_ROOT = st.empty()" in app_content
    assert "with _ROOT.container():" in app_content

    # 2. Cross-link inner columns [0.7, 0.3] present
    assert "[0.7, 0.3]" in app_content

    # 3. Alignment CSS present
    assert "p" in app_content
    assert "margin: 0;" in app_content
    assert "line-height: inherit;" in app_content

    # 4. config.toml contains primaryColor "#1a73e8" and toolbarMode minimal
    config_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../.streamlit/config.toml")
    )
    assert os.path.exists(config_path)
    with open(config_path, "r", encoding="utf-8") as f:
        config_content = f.read()
    assert 'primaryColor = "#1a73e8"' in config_content
    assert 'toolbarMode = "minimal"' in config_content
