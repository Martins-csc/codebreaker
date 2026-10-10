import os
import py_compile

import pytest


def test_v1_7_9_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_v1_7_9_source_scan():
    """Source scan: :has() CSS present, right-aligned question column, _ROOT pattern present, [0.75, 0.25] split with gap='small'."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. :has() CSS block present verbatim
    assert (
        'div[data-testid="stHorizontalBlock"]:has(button[kind="tertiary"])' in content
    )

    # 2. Question column right-aligned
    assert "text-align: right;" in content or "text-align: right" in content

    # 3. _ROOT pattern present
    assert "_ROOT = st.empty()" in content
    assert "with _ROOT.container():" in content

    # 4. [0.75, 0.25] split with gap="small"
    assert (
        "st.columns([0.75, 0.25]" in content
        or 'st.columns([0.75, 0.25], gap="small")' in content
    )
    assert 'gap="small"' in content
