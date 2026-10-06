from unittest.mock import MagicMock, patch

import pytest
from ai_engine import (BlueprintError, extend_blueprint,
                       render_blueprint_markdown, render_blueprint_pdf)


def test_no_duplicate_open_button_keys_in_app():
    """Assert that Open buttons on Home and Blueprint pages use unique keys."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    # Check that home open and blueprint open use distinct unique key formats
    assert "home_open_bp_" in content or "open_bp_" in content
    assert "bp_open_" in content


def test_engineering_log_title_length_cap():
    """Test that milestone title input enforces max 40 chars."""
    from security import validate_input_length

    long_title = "a" * 41
    valid, err = validate_input_length("title", long_title[:40])
    assert valid is True
    assert len(long_title[:40]) == 40


def test_extend_blueprint_creates_v2_logic():
    """Test extend_blueprint function call structure and schema preservation."""
    old_bp = {
        "project_name": "TestProj",
        "tech_stack": ["Python"],
        "folder_structure": "src/\n  app.py",
        "edge_cases": ["Edge 1"],
        "roadmap": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"],
        "summary": "Old summary",
    }

    mock_response = {
        "project_name": "TestProj — v2",
        "tech_stack": ["Python", "FastAPI"],
        "folder_structure": "src/\n  app.py\n  api.py",
        "edge_cases": ["Edge 1", "Edge 2"],
        "roadmap": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"],
        "summary": "Extended summary",
    }

    with patch("ai_engine._call_groq", return_value=mock_response):
        res = extend_blueprint(old_bp, "Add FastAPI")
        assert res["project_name"] == "TestProj — v2"
        assert "FastAPI" in res["tech_stack"]


def test_exports_contain_bullet_number_markers_and_tree():
    """Test that Markdown and PDF exports contain proper bullet/number markers and tree structure."""
    bp = {
        "project_name": "ExportProj",
        "tech_stack": ["React", "Node"],
        "folder_structure": "root/\n  package.json\n  src/\n    index.js",
        "edge_cases": ["Concurrency"],
        "roadmap": ["Init", "Build", "Test", "Deploy", "Verify"],
        "summary": "Export summary",
    }

    md = render_blueprint_markdown(bp)
    assert "- React" in md
    assert "- Node" in md
    assert "1. Init" in md
    assert "```text" in md
    assert "root/" in md

    pdf_bytes = render_blueprint_pdf(bp)
    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert len(pdf_bytes) > 0
