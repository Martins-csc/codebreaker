import json
import os
import re

import requests


class BlueprintError(Exception):
    """Custom exception for blueprint generation failures without exposing secrets."""

    pass


SYSTEM_PROMPT = """You are an expert AI system architect and software engineer.
You must output STRICT JSON only, with no markdown commentary outside the JSON if possible, or wrapped in json code fences.
The JSON object must contain exactly these top-level keys with specified types:
1. "project_name": string
2. "tech_stack": list of strings
3. "folder_structure": string representing a text tree of folders and files
4. "edge_cases": list of strings
5. "roadmap": list of exactly 5 step strings
6. "summary": string
"""


def _parse_json_response(content: str) -> dict:
    """Robustly parse JSON response by stripping fences, finding first {} block, and validating schema."""
    if not isinstance(content, str):
        raise BlueprintError("AI response content is not a string.")

    cleaned = content.strip()

    # 1. Try stripping markdown code fences
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if fence_match:
        cleaned = fence_match.group(1).strip()

    # 2. Extract first {...} block
    brace_match = re.search(r"(\{[\s\S]*\})", cleaned)
    if brace_match:
        cleaned = brace_match.group(1).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise BlueprintError(f"Failed to parse JSON response from AI engine: {e}")

    if not isinstance(data, dict):
        raise BlueprintError("Parsed AI response is not a JSON object.")

    # Schema validation
    required_keys = [
        "project_name",
        "tech_stack",
        "folder_structure",
        "edge_cases",
        "roadmap",
        "summary",
    ]
    for key in required_keys:
        if key not in data:
            raise BlueprintError(f"Missing required blueprint key: {key}")

    if not isinstance(data["project_name"], str):
        raise BlueprintError("Invalid type for project_name: expected string.")
    if not isinstance(data["tech_stack"], list):
        raise BlueprintError("Invalid type for tech_stack: expected list.")
    if not isinstance(data["folder_structure"], str):
        raise BlueprintError("Invalid type for folder_structure: expected string.")
    if not isinstance(data["edge_cases"], list):
        raise BlueprintError("Invalid type for edge_cases: expected list.")
    if not isinstance(data["roadmap"], list):
        raise BlueprintError("Invalid type for roadmap: expected list.")
    if not isinstance(data["summary"], str):
        raise BlueprintError("Invalid type for summary: expected string.")

    return data


def _call_groq(system_prompt: str, user_prompt: str) -> dict:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise BlueprintError("GROQ_API_KEY not found in environment.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    models_to_try = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b"]
    last_err = None

    for model in models_to_try:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            resp_data = response.json()
            content = resp_data["choices"][0]["message"]["content"]
            return _parse_json_response(content)
        except Exception as e:
            last_err = e
            continue

    raise BlueprintError(f"Groq API call failed across models: {last_err}")


def _call_gemini(system_prompt: str, user_prompt: str) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise BlueprintError("GEMINI_API_KEY not found in environment.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    combined_prompt = f"{system_prompt}\n\nProject Analysis Request:\n{user_prompt}"
    payload = {
        "contents": [{"parts": [{"text": combined_prompt}]}],
        "generationConfig": {"temperature": 0.2},
    }

    response = requests.post(url, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    resp_data = response.json()
    content = resp_data["candidates"][0]["content"]["parts"][0]["text"]
    return _parse_json_response(content)


def generate_blueprint(analysis: dict) -> dict:
    """
    Generate a system blueprint from project analysis dict.
    Tries Groq (llama-3.3-70b-versatile, falling back to openai/gpt-oss-120b),
    then falls back to Gemini (gemini-2.0-flash).
    Timeout set to 10 seconds. Raises BlueprintError on failure without leaking secrets.
    """
    if not isinstance(analysis, dict):
        raise BlueprintError("Analysis input must be a dictionary.")

    user_prompt = f"""
Analyze the following project requirements and build a comprehensive system architecture blueprint:
- Project Name: {analysis.get('project_name', 'Untitled')}
- Problem Statement: {analysis.get('problem', '')}
- Target Audience: {analysis.get('target_audience', '')}
- Skill Level: {analysis.get('skill_level', 'Intermediate')}
"""

    errors = []

    # Attempt Groq
    try:
        return _call_groq(SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        err_msg = str(e)
        for secret in [
            os.environ.get("GROQ_API_KEY"),
            os.environ.get("GEMINI_API_KEY"),
        ]:
            if secret:
                err_msg = err_msg.replace(secret, "[REDACTED]")
        errors.append(f"Groq failed: {err_msg}")

    # Attempt Gemini fallback
    try:
        return _call_gemini(SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        err_msg = str(e)
        for secret in [
            os.environ.get("GROQ_API_KEY"),
            os.environ.get("GEMINI_API_KEY"),
        ]:
            if secret:
                err_msg = err_msg.replace(secret, "[REDACTED]")
        errors.append(f"Gemini failed: {err_msg}")

    raise BlueprintError(f"All AI providers failed. Details: {'; '.join(errors)}")
