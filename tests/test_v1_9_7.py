import os
import py_compile

import pytest


def test_v1_9_7_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    ai_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(ai_path, doraise=True)


def test_v1_9_7_source_scan():
    """Source scan: descending sort for recent milestones, loud invalidation, show_spinner=False, and st.spinner wrappers."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Recent milestones descending sort
    log_sec_start = content.find("My Engineering Logs")
    log_snippet = (
        content[log_sec_start : log_sec_start + 1500]
        if log_sec_start != -1
        else content
    )
    assert "sorted(" in log_snippet
    assert "reverse=True" in log_snippet
    assert "log_rows[:3]" not in log_snippet

    # 2. Loud invalidation (no try/except pass in _invalidate_caches)
    inv_start = content.find("def _invalidate_caches()")
    inv_def = content[inv_start : inv_start + 250] if inv_start != -1 else content
    assert "try:" not in inv_def
    assert "except Exception:" not in inv_def

    # 3. show_spinner=False on cache_data decorators
    assert "@st.cache_data(ttl=30, show_spinner=False)" in content

    # 4. st.spinner wrappers at render sites
    assert 'with st.spinner("Loading..."):' in content
    assert 'with st.spinner("Loading blueprints..."):' in content
    assert 'with st.spinner("Loading logs..."):' in content
