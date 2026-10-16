import os
import py_compile

import pytest


def test_v1_8_9_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    ai_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(ai_path, doraise=True)


def test_v1_8_9_source_scan():
    """Source scan: zero importlib reload calls or _AE_MT in app.py."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "importlib" not in content
    assert "reload(" not in content
    assert "_AE_MT" not in content
    assert "ai_engine" in content
