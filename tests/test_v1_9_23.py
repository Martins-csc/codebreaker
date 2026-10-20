import os
import py_compile

import pytest


def test_v1_9_23_py_compile():
    """Assert app.py compiles successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    assert py_compile.compile(app_path, doraise=True)


def test_v1_9_23_github_auth_url_state():
    """Source scan: GitHub auth URL construction in app.py must contain &state={state}."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "&state={state}" in content
    assert "state = secrets.token_urlsafe(16)" in content
