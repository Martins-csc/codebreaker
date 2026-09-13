import os
from unittest.mock import MagicMock, patch

import pytest

from ai_engine import BlueprintError, _parse_json_response, generate_blueprint

VALID_BLUEPRINT_DATA = {
    "project_name": "Test Project",
    "tech_stack": ["Python", "Streamlit"],
    "folder_structure": "app.py\nrequirements.txt",
    "edge_cases": ["Network timeout", "Invalid input"],
    "roadmap": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"],
    "summary": "A test summary.",
}


def test_parse_plain_json():
    import json

    raw = json.dumps(VALID_BLUEPRINT_DATA)
    res = _parse_json_response(raw)
    assert res["project_name"] == "Test Project"
    assert res["tech_stack"] == ["Python", "Streamlit"]


def test_parse_fenced_json():
    import json

    raw = "```json\n" + json.dumps(VALID_BLUEPRINT_DATA) + "\n```"
    res = _parse_json_response(raw)
    assert res["project_name"] == "Test Project"


def test_parse_json_buried_in_prose():
    import json

    raw = (
        "Here is your requested system blueprint:\n```json\n"
        + json.dumps(VALID_BLUEPRINT_DATA)
        + "\n```\nHope this helps!"
    )
    res = _parse_json_response(raw)
    assert res["project_name"] == "Test Project"
    assert len(res["roadmap"]) == 5


def test_parse_invalid_json():
    with pytest.raises(BlueprintError):
        _parse_json_response("Not a json string at all")


def test_parse_missing_keys():
    import json

    incomplete = {"project_name": "Incomplete"}
    raw = json.dumps(incomplete)
    with pytest.raises(BlueprintError, match="Missing required blueprint key"):
        _parse_json_response(raw)


def test_parse_invalid_types():
    import json

    invalid_type_data = VALID_BLUEPRINT_DATA.copy()
    invalid_type_data["tech_stack"] = "not-a-list"
    raw = json.dumps(invalid_type_data)
    with pytest.raises(BlueprintError, match="Invalid type for tech_stack"):
        _parse_json_response(raw)


@patch.dict(os.environ, {}, clear=True)
def test_generate_blueprint_no_keys_raises_error():
    """Ensure zero network calls and BlueprintError when no API keys are present."""
    analysis = {"project_name": "No Key Test", "problem": "Test"}
    with pytest.raises(BlueprintError, match="All AI providers failed"):
        generate_blueprint(analysis)


@patch("ai_engine.requests.post")
@patch.dict(
    os.environ,
    {"GROQ_API_KEY": "fake_groq_key", "GEMINI_API_KEY": "fake_gemini_key"},
    clear=True,
)
def test_fallback_triggering(mock_post):
    import json

    # Groq tries 2 models, both fail. Then Gemini succeeds.
    success_resp = MagicMock()
    success_resp.status_code = 200
    success_resp.json.return_value = {
        "candidates": [
            {"content": {"parts": [{"text": json.dumps(VALID_BLUEPRINT_DATA)}]}}
        ]
    }

    mock_post.side_effect = [
        Exception("Groq model 1 error"),
        Exception("Groq model 2 error"),
        success_resp,
    ]

    analysis = {"project_name": "Fallback Test", "problem": "Test"}
    res = generate_blueprint(analysis)
    assert res["project_name"] == "Test Project"
    assert mock_post.call_count == 3
