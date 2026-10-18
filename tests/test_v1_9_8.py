import os
import py_compile

import pytest


def test_v1_9_8_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    ai_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(ai_path, doraise=True)


def test_v1_9_8_source_scan():
    """Source scan: zero untagged _track_client() calls remaining in app.py."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    untagged_count = 0
    for line in lines:
        if "_track_client()" in line or "_track_client ( )" in line:
            untagged_count += 1
    assert (
        untagged_count == 0
    ), f"Found {untagged_count} untagged _track_client() call sites."
