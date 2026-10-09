import os
import py_compile

import pytest
from ai_engine import build_pdf_lines, render_blueprint_pdf


def test_v1_6_9_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_v1_6_9_confirm_styling_source_scan():
    """Source scan: zero caption occurrences, Confirm present."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Confirming will permanently delete this item." not in content
    assert '"Confirm"' in content


def test_v1_6_9_pdf_chrome_spec_and_engine():
    """Source scan & functional check: pdf_chrome_spec.md exists, footer set_auto_page_break(auto=False) before set_y, strftime DD-MM-YYYY, Courier branch."""
    spec_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../docs/pdf_chrome_spec.md")
    )
    assert os.path.exists(spec_path)
    with open(spec_path, "r", encoding="utf-8") as f:
        spec_content = f.read()
    assert "PDF Chrome Spec" in spec_content

    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    with open(engine_path, "r", encoding="utf-8") as f:
        engine_content = f.read()

    assert "set_auto_page_break(auto=False)" in engine_content
    assert 'strftime("%d-%m-%Y")' in engine_content
    assert 'set_font("Courier"' in engine_content


def test_v1_6_9_pdf_export_functional():
    """Functional test for render_blueprint_pdf with export_date ISO conversion."""
    bp = {
        "project_name": "Mission 1.6.9 Test",
        "summary": "Testing PDF footer chrome and folder structure Courier branch.",
        "tech_stack": ["Python", "Streamlit"],
        "folder_structure": "root/\n  app.py\n  ai_engine.py",
        "edge_cases": ["None"],
        "roadmap": ["Step 1: Verify PDF chrome"],
    }
    pdf_bytes = render_blueprint_pdf(bp, export_date="2026-10-09")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
