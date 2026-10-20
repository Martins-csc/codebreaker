import os
import py_compile

import pytest


def test_v1_9_24_py_compile():
    """Assert app.py compiles successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    assert py_compile.compile(app_path, doraise=True)


def test_v1_9_24_query_params_state():
    """Source scan: app.py handles OAuth flow."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "client.rpc" in content
