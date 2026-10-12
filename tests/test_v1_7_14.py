import os
import py_compile

import pytest


def test_v1_7_14_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_v1_7_14_source_scan():
    """Source scan: disabled tertiary question buttons present, zero xlink baseline CSS, menu_book icon present, analytics & description untouched."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Disabled tertiary question buttons present (xlink_q_login / disabled=True)
    assert "xlink_q_login" in content
    assert "xlink_q_signup" in content
    assert "disabled=True" in content

    # 2. _XLINK_CSS present with :has() rule
    assert "_XLINK_CSS" in content
    assert (
        'div[data-testid="stHorizontalBlock"]:has(button[data-testid="stBaseButton-tertiary"])'
        in content
    )

    # 3. menu_book icon present in third card, analytics and description untouched
    assert ":material_menu_book:" in content
    assert ":material_analytics:" in content
    assert ":material_description:" in content
    assert ":material_journal:" not in content
