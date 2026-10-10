import os
import py_compile

import pytest


def test_v1_7_10_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_v1_7_10_source_scan():
    """Source scan: stBaseButton-tertiary selectors present and no button[kind="tertiary"], auth isolation clear function called, module-card class present, zero JOURNAL strings."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. CSS contains stBaseButton-tertiary and zero button[kind="tertiary"]
    assert 'button[data-testid="stBaseButton-tertiary"]' in content
    assert 'button[kind="tertiary"]' not in content

    # 2. Auth form isolation clear function present and called in transitions
    assert "def clear_auth_form_state()" in content
    assert "clear_auth_form_state()" in content
    assert content.count("clear_auth_form_state()") >= 5

    # 3. Module cards share one min-height class (.module-card)
    assert ".module-card" in content
    assert "min-height: 210px;" in content or "min-height:210px;" in content

    # 4. Zero "JOURNAL" heading strings
    assert "JOURNAL" not in content
    assert "journal" in content  # icon material/journal is fine
