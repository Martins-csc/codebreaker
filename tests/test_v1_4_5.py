import py_compile
import smtplib
from unittest.mock import MagicMock, patch

import pytest


def test_py_compile_gate():
    """Test pre-seal compile gate across core python modules for v1.4.5."""
    for mod in [
        "app.py",
        "ai_engine.py",
        "security.py",
        "config.py",
        "supabase_client.py",
    ]:
        res = py_compile.compile(mod, doraise=True)
        assert res is not None


def test_v1_4_5_export_redesign_four_rows():
    """Test four export rows with button + info popover/expander and selectbox removed."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "blueprint_export_format" not in content
    assert "Export as Markdown (.md)" in content
    assert "Export as Plain text (.txt)" in content
    assert "Export as HTML (.html)" in content
    assert "Export as PDF (.pdf)" in content
    assert "st.popover" in content
    assert "st.expander" in content
    assert "editable spec for repos & AI assistants" in content
    assert "universal, opens anywhere" in content
    assert "styled page for browser/offline" in content
    assert "fixed-layout for print & share" in content


def test_v1_4_5_contact_form_requirements():
    """Test contact form requirements: SMTP config check, SMTP_SSL/SMTP, SMTPException handling, and clearing fields on success."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "SMTP_HOST" in content
    assert "SMTP_PORT" in content
    assert "SMTP_USER" in content
    assert "SMTP_PASSWORD" in content
    assert "Contact form unavailable — email service not configured" in content
    assert "smtplib.SMTP_SSL" in content
    assert "starttls()" in content
    assert "smtplib.SMTPException" in content
    assert "Email send failed:" in content
    assert "contact_name_input" in content
    assert "contact_email_input" in content
    assert "contact_message_input" in content
    assert "Contact email sent to" in content
