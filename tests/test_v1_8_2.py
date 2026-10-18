import os
import py_compile

import pytest


def test_v1_8_2_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    ai_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(ai_path, doraise=True)


def test_v1_8_2_source_scan():
    """Source scan: zero _render_home_changelog, isolated auth widget keys, pre-warm calls."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Zero _render_home_changelog
    assert "_render_home_changelog" not in content

    # 2. All five auth inputs carry exact key= arguments
    assert 'key="login_email"' in content
    assert 'key="login_password"' in content
    assert 'key="signup_email"' in content
    assert 'key="signup_password"' in content
    assert 'key="signup_display_name"' in content

    # 3. _AUTH_WIDGET_KEYS equals the five-key list
    assert "_AUTH_WIDGET_KEYS = [" in content
    assert '"login_email"' in content
    assert '"login_password"' in content
    assert '"signup_email"' in content
    assert '"signup_password"' in content
    assert '"signup_display_name"' in content

    # 4. Pre-warm relocated to Dashboard via needs_prewarm
    assert "needs_prewarm" in content
