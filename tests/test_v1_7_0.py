import os
import py_compile

import pytest
from ai_engine import build_pdf_lines, render_blueprint_pdf


def test_v1_7_0_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_v1_7_0_requirements_source_scan():
    """Source scan: zero caption occurrences, fmt_date used, cross links present, initial_sidebar_state, Log Out."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        app_content = f.read()

    # 1. Zero occurrences of delete warning caption
    assert "Confirming will permanently delete this item." not in app_content

    # 2. fmt_date helper present and used
    assert "def fmt_date(" in app_content
    assert "fmt_date(" in app_content

    # 3. Both cross-link buttons present
    assert "auth_switch_to_signup" in app_content
    assert "auth_switch_to_login" in app_content

    # 4. initial_sidebar_state="collapsed" present
    assert 'initial_sidebar_state="collapsed"' in app_content

    # 5. Log Out button present in app
    assert '"Log Out"' in app_content

    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    with open(engine_path, "r", encoding="utf-8") as f:
        engine_content = f.read()

    # 6. strftime("%d-%m-%Y") present in ai_engine
    assert 'strftime("%d-%m-%Y")' in engine_content


def test_v1_7_0_pdf_export_functional():
    """Functional test for render_blueprint_pdf."""
    bp = {
        "project_name": "Mission 1.7.0 Test",
        "summary": "Testing DD-MM-YYYY display law and confirmation unification.",
        "tech_stack": ["Python", "Streamlit"],
        "folder_structure": "root/\n  app.py\n  ai_engine.py",
        "edge_cases": ["None"],
        "roadmap": ["Step 1: Verify requirements"],
    }
    pdf_bytes = render_blueprint_pdf(bp, export_date="2026-10-09")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
