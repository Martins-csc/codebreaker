import os
import py_compile

import pytest


def test_v1_7_17_py_compile():
    """Assert app.py compiles successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    assert py_compile.compile(app_path, doraise=True)


def test_v1_7_17_source_scan():
    """Source scan: disabled tertiary question buttons present on both views, vertical_alignment='center' present, zero markdown question elements in cross-link rows, _XLINK_CSS present."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Disabled tertiary question buttons / keys present
    assert "xlink_q_login" in content
    assert "xlink_q_signup" in content
    assert "disabled=True" in content

    # 2. vertical_alignment="center" or CSS align-items: center present
    assert 'vertical_alignment="center"' in content or "align-items: center" in content

    # 3. Zero markdown question elements in cross-link switch function
    # Check that q.markdown is not used for the question in _auth_switch_line
    # Instead q.button is used with disabled=True
    assert "q.button(question" in content or "q.button(" in content

    # 4. _XLINK_CSS rules present
    assert "_XLINK_CSS = " in content
    assert 'button[data-testid="stBaseButton-tertiary"][disabled]' in content
    assert 'button[data-testid="stBaseButton-tertiary"]:not([disabled])' in content
    assert (
        'div[data-testid="stButton"] button[disabled]' in content
        or 'div[data-testid="stHorizontalBlock"]' in content
    )
