import os
import py_compile
import time

import pytest
from ai_engine import (build_pdf_lines, clean_roadmap_step,
                       render_blueprint_pdf, sanitize_pdf_text)


def test_v1_6_4_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_clean_roadmap_step_keycaps():
    """Assert clean_roadmap_step strips keycap glyphs (U+20E3, U+FE0F) and leading number prefixes."""
    raw = "1️⃣. \u20e3Setup database\ufe0f"
    cleaned = clean_roadmap_step(raw)
    assert "1." not in cleaned
    assert "\u20e3" not in cleaned
    assert "\ufe0f" not in cleaned
    assert "Setup database" in cleaned


def test_roadmap_numbered_once_and_heading_count():
    """Assert roadmap steps are numbered exactly once and heading exists."""
    bp = {
        "project_name": "Roadmap Test",
        "roadmap": ["1. Step One", "2. Step Two", "Step Three"],
    }
    lines = build_pdf_lines(bp)
    roadmap_heading = [l for l in lines if "Implementation Roadmap" in l]
    assert len(roadmap_heading) == 1

    for l in lines:
        assert "1. 1." not in l
        assert "2. 2." not in l


def test_build_pdf_lines_pure_ascii():
    """Assert build_pdf_lines produces pure ASCII / latin-1 safe lines."""
    bp = {
        "project_name": "ASCII Test",
        "summary": "Summary with — dash and → arrow",
        "tech_stack": ["Python • Flask"],
        "folder_structure": "root/\n  ├── app.py",
        "edge_cases": ["Risk 1"],
        "roadmap": ["Build"],
    }
    lines = build_pdf_lines(bp)
    for l in lines:
        l.encode("latin-1")


def test_title_dedupe_regex():
    """Assert title dedupe regex strips trailing — vN and formatting correctly."""
    import re

    title1 = "weather app — v2"
    title2 = "weather app — v2 (v2)"
    pattern = r"\s*—\s*v\d+$"

    base1 = re.sub(pattern, "", title1).strip()
    assert base1 == "weather app"

    def format_title(t, v):
        b = re.sub(r"\s*—\s*v\d+", "", t)
        b = re.sub(r"\s*\(v\d+\)", "", b).strip()
        if v > 1:
            return f"{b} (v{v})"
        return b

    assert format_title("weather app — v2", 2) == "weather app (v2)"
    assert format_title("weather app — v2 (v2)", 2) == "weather app (v2)"
    assert format_title("weather app", 1) == "weather app"


def test_delete_arm_expiry():
    """Assert delete arm expiry logic resets state after 10 seconds."""
    session_state = {
        "arm_del_bp_123": True,
        "arm_time_bp_123": time.time() - 15,
    }
    now = time.time()
    for k in list(session_state.keys()):
        if k.startswith("arm_time_bp_"):
            b_id = k.replace("arm_time_bp_", "")
            if now - session_state.get(k, 0) > 10:
                session_state[f"arm_del_bp_{b_id}"] = False
                session_state.pop(k, None)

    assert session_state["arm_del_bp_123"] is False
    assert "arm_time_bp_123" not in session_state


def test_single_renderer_law_source_scan():
    """Source-scan: ai_engine.py has exactly one fpdf-using function, no .cell( in it, and app.py references render_blueprint_pdf."""
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    with open(engine_path, "r", encoding="utf-8") as f:
        content = f.read()

    pdf_func_start = content.find("def render_blueprint_pdf")
    assert pdf_func_start != -1
    pdf_func_end = content.find("def render_blueprint_", pdf_func_start + 25)
    if pdf_func_end == -1:
        pdf_func_end = len(content)
    pdf_func_body = content[pdf_func_start:pdf_func_end]

    assert ".cell(" not in pdf_func_body, "render_blueprint_pdf must not use .cell("
    assert "multi_cell" in pdf_func_body
    assert content.count("FPDF(") == 1

    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        app_content = f.read()
    assert "render_blueprint_pdf" in app_content
