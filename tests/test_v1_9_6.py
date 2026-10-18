import os
import py_compile

import pytest


def test_v1_9_6_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    ai_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(ai_path, doraise=True)


def test_v1_9_6_source_scan():
    """Source scan: .clear() in log submission, st.spinner wrapping fetch calls in Blueprint Library and Engineering Log views."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify cache clear call in log submission handler
    assert "_cached_fetch_logs.clear()" in content

    # Verify st.spinner wraps fetch calls in Blueprint Library and Engineering Log views
    assert 'with st.spinner("Loading blueprints..."):' in content
    assert '_cached_fetch_blueprints(user["id"])' in content

    assert 'with st.spinner("Loading logs..."):' in content
    assert '_cached_fetch_logs(user["id"])' in content
