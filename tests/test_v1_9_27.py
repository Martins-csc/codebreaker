import os
import py_compile

import pytest


def test_v1_9_27_py_compile():
    """Assert app.py compiles successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    assert py_compile.compile(app_path, doraise=True)


def test_v1_9_27_latest_row_consumption():
    """Source scan: callback uses consume_latest_oauth_state and insert uses random state without pending."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert 'client.rpc("consume_latest_oauth_state").execute()' in content
    assert "state = secrets.token_urlsafe(16)" in content
    assert "insert_oauth_state" in content
    assert "consume_oauth_state" not in content
