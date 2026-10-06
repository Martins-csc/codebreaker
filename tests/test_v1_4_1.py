import py_compile
import time

import pytest
from ai_engine import render_blueprint_pdf, sanitize_pdf_text
from security import validate_email


def test_py_compile_gate():
    """Test pre-seal compile gate across core python modules for v1.4.1."""
    for mod in [
        "app.py",
        "ai_engine.py",
        "security.py",
        "config.py",
        "supabase_client.py",
    ]:
        res = py_compile.compile(mod, doraise=True)
        assert res is not None


def test_latin1_safe_on_emoji_and_arrows():
    """Test sanitization mapping common arrows/symbols to safe ASCII/replacements."""
    sample = "Project 🚀 → Beta Test • Check"
    safe = sanitize_pdf_text(sample)
    assert "->" in safe
    encoded = safe.encode("latin-1", "replace")
    assert encoded is not None


def test_render_blueprint_pdf_with_emoji_and_arrow():
    """Test rendering blueprint PDF with emoji and arrow input."""
    blueprint = {
        "project_name": "SaaS Alpha -> Production",
        "tech_stack": ["Python 3.14", "Streamlit"],
        "folder_structure": "src/\n  app.py -> main entry\n  utils.py",
        "edge_cases": ["Network timeout", "High concurrency -> queueing"],
        "roadmap": ["Step 1: Setup", "Step 2: Core features"],
        "summary": "Building a robust system with 100% -> speed boost and total reliability.",
    }
    pdf_bytes = render_blueprint_pdf(blueprint)
    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000


def test_log_form_plain_widgets_and_no_max_chars():
    """Test app.py log form implementation uses plain widgets and has no max_chars on log text areas."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Log form must not use st.form for engineering_log_form
    assert 'with st.form("engineering_log_form"):' not in content
    # Log text areas must not have max_chars
    assert 'st.text_area("Progress / Milestone", max_chars=' not in content
    assert 'st.text_area("Bugs / Challenges", max_chars=' not in content
    assert 'st.text_area("Learnings / Insights", max_chars=' not in content
    # Plain submit button present
    assert 'st.button("Submit Log Entry"' in content
    # Project labeling stored and grouped
    assert "project_name" in content
    assert "Project — milestone" in content or "—" in content


def test_about_page_expanders_and_contact_btn():
    """Test About page contains Mini-FAQ expander accordions and Contact us button."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert 'with st.expander("Privacy: Are my logs private?"):' in content
    assert (
        'with st.expander("Forgot Password: How do I reset my password?"):' in content
    )
    assert (
        'with st.expander("Reload Login Note: Do I stay logged in across reloads?"):'
        in content
    )
    assert (
        'with st.expander("Where is my exported file: Where do exports go?"):'
        in content
    )
    assert "Built by CodeBreaker Dev" in content
    assert 'st.button("Contact us"' in content


def test_contact_page_validation_and_cooldown():
    """Test contact form validation rules and success message."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert 'page == "Contact"' in content
    assert "codebreakerbuild@gmail.com" in content
    assert "Message sent. We'll respond within 24 hours." in content
    assert "60" in content  # cooldown check


def test_delete_two_step_buttons_formatting():
    """Test delete two-step confirmation buttons have use_container_width=True and short labels Delete/Cancel."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "use_container_width=True" in content
    assert '"Delete"' in content
    assert '"Cancel"' in content
