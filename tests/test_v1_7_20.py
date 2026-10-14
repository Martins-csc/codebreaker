import os
import py_compile

import pytest


def test_v1_7_20_py_compile():
    """Assert app.py compiles successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    assert py_compile.compile(app_path, doraise=True)


def test_v1_7_20_source_scan():
    """Source scan: _render_home_changelog defined and called in Home branch."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "def _render_home_changelog():" in content
    assert "_render_home_changelog()" in content
    # Check that it's called in Home branch (between page == "Home" and page == "Analyze")
    home_idx = content.find('elif page == "Home":')
    analyze_idx = content.find('elif page == "Analyze":')
    changelog_call_idx = content.find("_render_home_changelog()", home_idx)
    assert home_idx != -1
    assert analyze_idx != -1
    assert changelog_call_idx != -1
    assert home_idx < changelog_call_idx < analyze_idx
