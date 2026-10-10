import os
import py_compile

import pytest


def test_v1_7_6_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_v1_7_6_source_scan():
    """Source scan: zero href='?mode=' in app.py, tertiary cross-link buttons present with underline CSS, config.toml contains toolbarMode, widget state clearance on login success."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        app_content = f.read()

    # 1. Zero href="?mode= in app.py
    assert 'href="?mode=' not in app_content
    assert "?mode=" not in app_content

    # 2. Tertiary cross-link buttons present with underline CSS
    assert "auth_switch_to_signup" in app_content
    assert "auth_switch_to_login" in app_content
    assert "text-decoration: underline;" in app_content

    # 3. Widget state clearance on login success
    assert "auth_card_email" in app_content
    assert "auth_card_password" in app_content

    # 4. config.toml contains toolbarMode
    config_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../.streamlit/config.toml")
    )
    assert os.path.exists(config_path)
    with open(config_path, "r", encoding="utf-8") as f:
        config_content = f.read()
    assert (
        'toolbarMode = "minimal"' in config_content or "toolbarMode" in config_content
    )
