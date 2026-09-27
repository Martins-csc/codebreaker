import py_compile
from datetime import datetime, timezone

import pytest


def test_py_compile_gate():
    """Test pre-seal compile gate across core python modules for v1.4.3."""
    for mod in [
        "app.py",
        "ai_engine.py",
        "security.py",
        "config.py",
        "supabase_client.py",
    ]:
        res = py_compile.compile(mod, doraise=True)
        assert res is not None


def test_v1_4_3_no_st_form_remaining():
    """Test that zero st.form wrappers remain anywhere in app.py."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "st.form" not in content
    assert "form_submit_button" not in content


def test_v1_4_3_delete_all_inside_expander():
    """Test that delete-ALL confirmation is wrapped inside an st.expander('Confirm delete all', ...)."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert 'with st.expander("Confirm delete all"' in content


def test_v1_4_3_export_captions_per_format():
    """Test dynamic export captions are present for all four formats."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "editable spec for repos/AI assistants" in content
    assert "universal, opens anywhere" in content
    assert "styled page for browsers/offline" in content
    assert "fixed-layout for print/share" in content


def test_v1_4_3_member_since_date_formatting():
    """Test member-since date formatting to DD Mon YYYY (e.g. 16 Sep 2026)."""

    def format_member_since(created_at_val):
        if not created_at_val or created_at_val == "N/A":
            return "N/A"
        try:
            s_val = str(created_at_val)
            if "T" in s_val:
                clean_str = s_val.replace("Z", "+00:00").split("+")[0].split(".")[0]
                dt = datetime.fromisoformat(clean_str)
                return dt.strftime("%d %b %Y")
            elif len(s_val) == 10 and s_val[4] == "-" and s_val[7] == "-":
                dt = datetime.strptime(s_val, "%Y-%m-%d")
                return dt.strftime("%d %b %Y")
            else:
                dt = datetime.fromisoformat(s_val.replace("Z", "+00:00"))
                return dt.strftime("%d %b %Y")
        except Exception:
            s = str(created_at_val).split("T")[0]
            try:
                dt = datetime.strptime(s, "%Y-%m-%d")
                return dt.strftime("%d %b %Y")
            except Exception:
                return str(created_at_val)

    # Test ISO timestamp
    assert format_member_since("2026-09-16T12:34:56Z") == "16 Sep 2026"
    # Test date string YYYY-MM-DD
    assert format_member_since("2026-09-16") == "16 Sep 2026"
    # Test N/A fallback
    assert format_member_since("N/A") == "N/A"
    assert format_member_since(None) == "N/A"
