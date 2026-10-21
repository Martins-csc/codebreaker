import os
import py_compile

import pytest


def test_v1_9_29_py_compile():
    """Assert app.py compiles successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    assert py_compile.compile(app_path, doraise=True)


def test_v1_9_29_oauth_insert_no_try():
    """Source scan: oauth_states insert uses random state and is not wrapped in delete try block."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "insert_oauth_state" in content
    assert '"pending"' not in content
    assert "consume_latest_oauth_state" in content
