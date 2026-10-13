import os
import py_compile

import pytest


def test_v1_7_16_py_compile():
    """Assert app.py compiles successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    assert py_compile.compile(app_path, doraise=True)


def test_v1_7_16_source_scan():
    """Source scan: question markdown contains text-align:right, link button carries use_container_width=False, disabled-black CSS rule present."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Question markdown contains text-align:right or disabled tertiary button
    assert "text-align:right" in content or "disabled=True" in content

    # 2. Link button carries use_container_width=False
    assert "use_container_width=False" in content

    # 3. Inner columns present
    assert (
        'st.columns([0.72, 0.28], gap="small")' in content
        or "st.columns([0.72, 0.28]" in content
        or "st.columns([0.62, 0.38]" in content
    )

    # 4. Disabled-black CSS rule present
    assert 'button[data-testid="stBaseButton-tertiary"][disabled]' in content
    assert "color: #111111;" in content
