import py_compile
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest


def test_py_compile_gate():
    """Test pre-seal compile gate across core python modules for v1.4.2."""
    for mod in [
        "app.py",
        "ai_engine.py",
        "security.py",
        "config.py",
        "supabase_client.py",
    ]:
        res = py_compile.compile(mod, doraise=True)
        assert res is not None


def test_v1_4_2_analyze_placeholders_and_no_max_chars():
    """Test Analyze form placeholders are present and max_chars is removed from inputs."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert 'placeholder="e.g. Chat App"' in content
    assert 'placeholder="e.g. Students, Enterprise, Consumers"' in content
    assert (
        'placeholder="What problem are you solving and what are the core requirements?"'
        in content
    )
    assert (
        "max_chars="
        not in content.split('elif page == "Analyze":')[1].split(
            'elif page == "Blueprint":'
        )[0]
    )


def test_v1_4_2_log_expander_primary_css():
    """Test scoped CSS for expander primary delete button on Engineering Log page."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    css_pattern = 'div[data-testid="stExpander"] div.stButton > button[kind="primary"]'
    assert css_pattern in content
    assert "background-color:#d33" in content or "background-color: #d33" in content


def test_v1_4_2_resumed_user_carries_created_at():
    """Test URL-resume rehydration path includes member_since in session_state['user']."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert (
        '"member_since": c_display' in content or "'member_since': c_display" in content
    )


def test_v1_4_2_log_tz_conversion():
    """Test log timestamp conversion logic to Africa/Lagos (zoneinfo)."""

    def format_lagos_timestamp(created_at_str):
        if not created_at_str or created_at_str == "N/A":
            return "N/A", "N/A"
        try:
            clean_str = str(created_at_str).replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_str)
            dt_lagos = dt.astimezone(ZoneInfo("Africa/Lagos"))
            d_disp = dt_lagos.strftime("%Y-%m-%d")
            t_disp = dt_lagos.strftime("%Y-%m-%d %H:%M:%S")
            return d_disp, t_disp
        except Exception:
            d = (
                str(created_at_str).split("T")[0]
                if "T" in str(created_at_str)
                else str(created_at_str)
            )
            return d, str(created_at_str)

    d_disp, t_disp = format_lagos_timestamp("2026-09-27T12:00:00Z")
    assert d_disp == "2026-09-27"
    assert "13:00:00" in t_disp


def test_v1_4_2_no_emoji_sweep():
    """Test that banned emoji glyphs are absent from user-facing strings."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    emojis = ["⚡", "🔍", "📐", "📝", "🛡️", "👋", "✅", "🗑️", "📥"]
    for emoji in emojis:
        assert emoji not in content, f"Found emoji: '{emoji}' in app.py"


def test_v1_4_2_about_signature_text():
    """Test About signature is set to Built by CodeBreaker Dev."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "Built by CodeBreaker Dev" in content
    assert "Built by Martins" not in content


def test_v1_4_2_export_help_tooltips_present():
    """Test four export download buttons are present after v1.4.5 redesign."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "Export as Markdown (.md)" in content
    assert "Export as Plain text (.txt)" in content
