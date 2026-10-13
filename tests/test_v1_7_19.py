import os
import py_compile

import pytest


def test_v1_7_19_py_compile():
    """Assert app.py compiles successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    assert py_compile.compile(app_path, doraise=True)


def test_v1_7_19_source_scan():
    """Source scan: horizontal_alignment="right" and horizontal_alignment="left" present, zero justify-content rules, disabled tertiary question buttons present."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Native container alignment attributes present
    assert 'horizontal_alignment="right"' in content
    assert 'horizontal_alignment="left"' in content

    # 2. Zero justify-content rules remain in CSS
    assert "justify-content" not in content

    # 3. Disabled tertiary question buttons present on both views
    assert "xlink_q_login" in content
    assert "xlink_q_signup" in content
    assert "disabled=True" in content
