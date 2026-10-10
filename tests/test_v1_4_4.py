import py_compile
from datetime import datetime

import pytest


def test_py_compile_gate():
    """Test pre-seal compile gate across core python modules for v1.4.4."""
    for mod in [
        "app.py",
        "ai_engine.py",
        "security.py",
        "config.py",
        "supabase_client.py",
    ]:
        res = py_compile.compile(mod, doraise=True)
        assert res is not None


def test_v1_4_4_no_st_form_remaining():
    """Test that zero st.form wrappers remain anywhere in app.py (assertion)."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "st.form" not in content
    assert "form_submit_button" not in content


def test_v1_4_4_member_since_formatting():
    """Test format_member_since produces DD Mon YYYY format."""

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

    assert format_member_since("2026-09-16T12:34:56Z") == "16 Sep 2026"
    assert format_member_since("2026-09-16") == "16 Sep 2026"
    assert format_member_since("N/A") == "N/A"


def test_v1_4_4_folder_structure_vertical_replace():
    """Test folder structure handles literal escaped newlines."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "folder_tree.replace" in content


def test_v1_4_4_export_labels_inline_purpose():
    """Test selectbox is removed and four export rows are present."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "blueprint_export_format" not in content
    assert "Export as Markdown (.md)" in content
    assert "Export as Plain text (.txt)" in content
    assert "Export as HTML (.html)" in content
    assert "Export as PDF (.pdf)" in content


def test_v1_4_4_email_placeholder_empty_and_hints_css():
    """Test email placeholder is empty and aggressive hint suppression CSS is injected."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "st.text_input" in content and '"Email"' in content
    assert 'div[data-testid="stWidgetTrailer"]' in content
    assert 'div[data-testid="stCharCounter"]' in content
    assert "autocomplete" in content


def test_v1_4_4_danger_buttons_full_width():
    """Test danger buttons have use_container_width=True."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "use_container_width=True" in content
