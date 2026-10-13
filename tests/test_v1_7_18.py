import os
import py_compile

import pytest


def test_v1_7_18_py_compile():
    """Assert app.py compiles successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    assert py_compile.compile(app_path, doraise=True)


def test_v1_7_18_source_scan():
    """Source scan: zero <a href inside auth-switch code, disabled tertiary question buttons present, four CSS rules present verbatim."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Zero <a href inside auth-switch code
    assert "<a href" not in content

    # 2. Disabled tertiary question buttons present on both views
    assert "xlink_q_login" in content
    assert "xlink_q_signup" in content
    assert "disabled=True" in content

    # 3. CSS rules present
    assert (
        'div[data-testid="stHorizontalBlock"]:has(button[data-testid="stBaseButton-tertiary"]) { column-gap: 6px; align-items: center; }'
        in content
    )
    assert (
        'button[data-testid="stBaseButton-tertiary"] { min-height: 0; padding: 0; white-space: nowrap; }'
        in content
    )
    assert 'button[data-testid="stBaseButton-tertiary"][disabled]' in content
    assert 'button[data-testid="stBaseButton-tertiary"]:not([disabled])' in content
