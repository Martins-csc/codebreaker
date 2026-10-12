import os
import py_compile

import pytest


def test_v1_7_13_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_v1_7_13_source_scan():
    """Source scan: zero xlink baseline CSS, menu_book icon present."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. _XLINK_CSS present
    assert "_XLINK_CSS" in content

    # 2. menu_book icon present
    assert ":material_menu_book:" in content
