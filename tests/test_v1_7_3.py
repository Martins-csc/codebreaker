import os
import py_compile

import pytest


def test_v1_7_3_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_v1_7_3_source_scan():
    """Source scan: provider-diversity rule in prompts, zero 'Back to All Blueprints', '← Blueprint Library' present, exactly one set_page_config with collapsed sidebar."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )

    with open(app_path, "r", encoding="utf-8") as f:
        app_content = f.read()

    with open(engine_path, "r", encoding="utf-8") as f:
        engine_content = f.read()

    # 1. Provider-diversity rule present in ai_engine.py (SYSTEM_PROMPT covers generation and extend)
    rule_text = (
        "When the project requires an LLM/AI API or any third-party API, "
        "weigh alternatives (OpenAI, Google Gemini, Anthropic Claude, open-source models via Groq/Ollama) "
        "against the user's stated constraints (cost, privacy, offline use, latency); "
        "select the best-fit provider, reflect it in the tech stack, and justify the choice in one sentence inside the summary; "
        "never default to OpenAI GPT-4o without explicit justification."
    )
    assert rule_text in engine_content

    # 2. Zero "Back to All Blueprints" strings in app.py / codebase
    assert "Back to All Blueprints" not in app_content

    # 3. "← Blueprint Library" button label present in app.py
    assert "← Blueprint Library" in app_content

    # 4. Exactly one set_page_config call with initial_sidebar_state="collapsed"
    assert app_content.count("st.set_page_config(") == 1
    assert 'initial_sidebar_state="collapsed"' in app_content
