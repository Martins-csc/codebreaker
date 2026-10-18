import os
import py_compile

import pytest


def test_v1_9_3_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    ai_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(ai_path, doraise=True)


def test_v1_9_3_source_scan():
    """Source scan: _nav_to_auth present and used in landing CTAs and auth switch lines."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "_nav_to_auth" in content
    assert 'key="cta_login"' in content
    assert 'key="cta_signup"' in content
    assert "on_click=_nav_to_auth" in content
    assert "_auth_switch_line" in content
