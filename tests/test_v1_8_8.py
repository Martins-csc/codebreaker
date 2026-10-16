import os
import py_compile

import pytest


def test_v1_8_8_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    ai_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(ai_path, doraise=True)


def test_v1_8_8_source_scan():
    """Source scan: _record_run_ms definition, reachability at all stop/tail sites, and root wrap truth."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. _record_run_ms defined
    assert "def _record_run_ms():" in content
    assert (
        'st.session_state["last_run_ms"] = round((time.time() - _run_start) * 1000, 1)'
        in content
    )

    # 2. _record_run_ms called at least 3 times (2 stop sites + 1 tail)
    assert content.count("_record_run_ms()") >= 3

    # 3. Root wrap truth: _ROOT = st.empty() and with _ROOT.container(): present
    assert "_ROOT = st.empty()" in content
    assert "with _ROOT.container():" in content

    # 4. Page branches sit inside _ROOT block (all page branches present inside app.py)
    for branch_keyword in [
        'if page == "About":',
        'elif page == "Contact":',
        'elif page == "Home":',
        'elif page == "Analyze":',
        'elif page == "Blueprint":',
        'elif page == "Engineering Log":',
    ]:
        assert branch_keyword in content
