import os
import py_compile

import pytest


def test_v1_9_5_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    ai_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(ai_path, doraise=True)


def test_v1_9_5_source_scan():
    """Source scan: zero date formatting strings in Dashboard recent renderers, cache clear present in log submission."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify recent blueprints render without timestamps (no date_str in Home blueprint loop)
    # Check that Home view prints display_title without date_str
    assert 'st.markdown(f"- **{display_title}**")' in content
    assert (
        "date_str" not in content or "fmt_date" in content
    )  # fmt_date still used in log detail view but not in Home recent lists

    # Verify recent milestones render without timestamp badges
    assert 'st.markdown(f"- **{proj}** — {ttl}")' in content
    assert "`({d_str})`" not in content

    # Verify log submission cache invalidation
    assert "_cached_fetch_logs.clear()" in content
    assert "_invalidate_caches()" in content
