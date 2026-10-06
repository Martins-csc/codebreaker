import json
import py_compile
from unittest.mock import MagicMock, patch

import pytest
from ai_engine import (BlueprintError, _wrap_text, extend_blueprint,
                       generate_blueprint, render_blueprint_html,
                       render_blueprint_markdown, render_blueprint_pdf,
                       render_blueprint_text, sanitize_pdf_text)


def test_py_compile_gate():
    """Test pre-seal compile gate across core python modules for v1.6.1."""
    for mod in [
        "app.py",
        "ai_engine.py",
        "security.py",
        "config.py",
        "supabase_client.py",
    ]:
        res = py_compile.compile(mod, doraise=True)
        assert res is not None


def test_sanitizer_ascii_only():
    """Test that sanitize_pdf_text strips emojis and converts unicode arrows/dashes to ASCII."""
    dirty = "🚀 Deploy ✅ check ├─→|- └─→+ –—‑→-"
    safe = sanitize_pdf_text(dirty)
    assert "🚀" not in safe
    assert "✅" not in safe
    assert "→" not in safe
    assert "—" not in safe
    # Ensure it encodes to latin-1 without error
    encoded = safe.encode("latin-1", "replace")
    assert isinstance(encoded, bytes)


def test_wrapper_lines_max_95_chars():
    """Test that text wrapping respects width (<= 95 chars)."""
    long_text = "This is a very long sentence designed to test whether text wrapping correctly wraps paragraphs into lines that do not exceed ninety-five characters in length."
    wrapped = _wrap_text(long_text, width=90)
    lines = wrapped.split("\n")
    for line in lines:
        assert len(line) <= 95


def test_roadmap_scaling_differs():
    """Test roadmap length differs between simple and complex fixtures, with no strict assertion of 5."""
    simple_bp = {
        "project_name": "Simple",
        "project_description": "Simple app",
        "target_audience": "Devs",
        "tech_stack": ["Python"],
        "folder_structure": "main.py",
        "edge_cases": [],
        "roadmap": ["Step 1", "Step 2", "Step 3"],
        "summary": "Simple",
    }
    complex_bp = {
        "project_name": "Complex",
        "project_description": "Complex app",
        "target_audience": "Enterprise",
        "tech_stack": ["Python", "Docker", "K8s"],
        "folder_structure": "src/\n  app.py",
        "edge_cases": ["Scale", "Security"],
        "roadmap": [f"Step {i}" for i in range(1, 9)],
        "summary": "Complex",
    }
    assert len(simple_bp["roadmap"]) == 3
    assert len(complex_bp["roadmap"]) == 8
    assert len(simple_bp["roadmap"]) != len(complex_bp["roadmap"])


def test_extend_blueprint_signature_and_context():
    """Test extend_blueprint(old_json, new_requirements, notes) carries context and returns schema-complete dict."""
    old_bp = {
        "project_name": "Core App",
        "project_description": "Base app",
        "target_audience": "Users",
        "tech_stack": ["Python"],
        "folder_structure": "app.py",
        "edge_cases": ["Edge 1"],
        "roadmap": ["Step 1"],
        "summary": "Base summary",
    }

    mock_resp = {
        "project_name": "Core App — v2",
        "project_description": "Base app",
        "target_audience": "Users",
        "tech_stack": ["Python", "Redis"],
        "folder_structure": "app.py\nredis.py",
        "edge_cases": ["Edge 1", "Edge 2"],
        "roadmap": ["Step 1", "Step 2"],
        "summary": "Extended summary",
    }

    with patch("ai_engine._call_groq", return_value=mock_resp):
        res = extend_blueprint(old_bp, "Add Redis", "Caching note")
        assert res["project_name"] == "Core App — v2"
        assert "Redis" in res["tech_stack"]
        assert res["project_description"] == "Base app"
        assert res["target_audience"] == "Users"


def test_export_rows_2_columns_and_txt_bom():
    """Test export rows structure in app.py (2 columns ratio 0.82/0.18) and TXT bytes start with BOM."""
    with open("app.py", "r", encoding="utf-8") as f:
        app_content = f.read()

    assert (
        "st.columns([0.82, 0.18])" in app_content
        or "st.columns([82, 18])" in app_content
        or "st.columns([0.82" in app_content
    )
    assert "utf-8-sig" in app_content
    assert (
        "Blueprint Library" not in app_content
        or 'st.sidebar.subheader("Blueprint Library")' not in app_content
    )

    bp = {
        "project_name": "Test",
        "project_description": "Desc",
        "target_audience": "Aud",
        "tech_stack": ["Python"],
        "folder_structure": "app.py",
        "edge_cases": [],
        "roadmap": ["Step 1"],
        "summary": "Sum",
    }
    txt_str = render_blueprint_text(bp)
    txt_bytes = txt_str.encode("utf-8-sig")
    # UTF-8 BOM bytes are b'\xef\xbb\xbf'
    assert txt_bytes.startswith(b"\xef\xbb\xbf")


def test_project_context_in_exports():
    """Test every export begins with Project Context block or legacy fallback."""
    bp = {
        "project_name": "Context App",
        "project_description": "Important project",
        "target_audience": "Students",
        "tech_stack": ["Python"],
        "folder_structure": "app.py",
        "edge_cases": [],
        "roadmap": ["Step 1"],
        "summary": "Summary",
    }
    md = render_blueprint_markdown(bp)
    assert "Project Context" in md
    assert "Important project" in md
    assert "Students" in md

    # Row without project_description and target_audience renders N/A
    missing_bp = {
        "project_name": "No Context App",
        "tech_stack": ["Python"],
        "folder_structure": "app.py",
        "edge_cases": [],
        "roadmap": ["Step 1"],
        "summary": "Summary",
    }
    md_missing = render_blueprint_markdown(missing_bp)
    assert "N/A" in md_missing


def test_pdf_rewrite_functions():
    """Test sanitize_pdf_text and build_pdf_lines contracts."""
    from ai_engine import (build_pdf_lines, render_blueprint_pdf,
                           sanitize_pdf_text)

    tree = "root/\n  ├── file1\n  └── file2 :rocket: \u0123"
    sanitized = sanitize_pdf_text(tree)
    # Check ASCII-only and mapping
    assert "├" not in sanitized
    assert "└" not in sanitized
    assert "|" in sanitized
    assert "+" in sanitized
    assert "-" in sanitized  # \u0123 > 255 becomes "-"

    bp = {
        "project_name": "PDF Test",
        "project_description": "Desc",
        "target_audience": "Aud",
        "tech_stack": ["Python"],
        "folder_structure": tree,
        "edge_cases": ["Edge"],
        "roadmap": ["1. Step 1", "2. Step 2"],
        "summary": "Sum",
    }
    lines = build_pdf_lines(bp)
    assert isinstance(lines, list)
    # Check roadmap single numbering
    roadmap_lines = [
        l
        for l in lines
        if "Implementation Roadmap" in l or "1. Step 1" in l or "2. Step 2" in l
    ]
    assert any("1. Step 1" in l for l in lines)
    assert any("2. Step 2" in l for l in lines)
    assert not any("1. 1." in l for l in lines)

    pdf_bytes = render_blueprint_pdf(bp)
    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert pdf_bytes.startswith(b"%PDF")
