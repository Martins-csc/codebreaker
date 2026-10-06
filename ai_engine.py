import datetime
import json
import os
import re
import textwrap

import markdown
import requests
from config import get_config
from fpdf import FPDF


class BlueprintError(Exception):
    """Custom exception for blueprint generation failures without exposing secrets."""

    pass


SYSTEM_PROMPT = """You are an expert AI system architect and software engineer.
You must output STRICT JSON only, with no markdown commentary outside the JSON if possible, or wrapped in json code fences.
The JSON object must contain exactly these top-level keys with specified types:
1. "project_name": string
2. "project_description": string
3. "target_audience": string
4. "tech_stack": list of strings
5. "folder_structure": string representing a text tree of folders and files
6. "edge_cases": list of strings
7. "roadmap": list of step strings (Implementation Roadmap step count follows complexity: simple 3-4, medium 5-7, complex 8-10; never default to 5)
8. "summary": string
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
    api_key = get_config("GROQ_API_KEY")
    if not api_key:
        raise BlueprintError("GROQ_API_KEY not found in environment or secrets.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    groq_model = get_config("GROQ_MODEL", "openai/gpt-oss-120b")
    models_to_try = [groq_model]
    for m in ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"]:
        if m not in models_to_try:
            models_to_try.append(m)
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
    api_key = get_config("GEMINI_API_KEY")
    if not api_key:
        raise BlueprintError("GEMINI_API_KEY not found in environment or secrets.")

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


def _call_ai(system_prompt: str, user_prompt: str) -> dict:
    errors = []
    try:
        return _call_groq(system_prompt, user_prompt)
    except Exception as e:
        err_msg = str(e)
        for secret in [get_config("GROQ_API_KEY"), get_config("GEMINI_API_KEY")]:
            if secret:
                err_msg = err_msg.replace(secret, "[REDACTED]")
        errors.append(f"Groq (Groq API/Models) failed: {err_msg}")

    try:
        return _call_gemini(system_prompt, user_prompt)
    except Exception as e:
        err_msg = str(e)
        for secret in [get_config("GROQ_API_KEY"), get_config("GEMINI_API_KEY")]:
            if secret:
                err_msg = err_msg.replace(secret, "[REDACTED]")
        errors.append(f"Gemini (Google Generative AI) failed: {err_msg}")

    raise BlueprintError(
        f"All AI providers failed (Groq, Gemini). Details: {'; '.join(errors)}"
    )


def generate_blueprint(analysis: dict) -> dict:
    """
    Generate a system blueprint from project analysis dict.
    Tries Groq (configurable via GROQ_MODEL config, default openai/gpt-oss-120b),
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

    res = _call_ai(SYSTEM_PROMPT, user_prompt)

    res["project_name"] = res.get("project_name") or analysis.get(
        "project_name", "Untitled Project"
    )
    res["project_description"] = (
        res.get("project_description")
        or analysis.get("problem", "")
        or analysis.get("project_description", "")
    )
    res["target_audience"] = res.get("target_audience") or analysis.get(
        "target_audience", ""
    )
    return res


def extend_blueprint(old_json: dict, new_requirements: str, notes: str = "") -> dict:
    """
    Extend an existing blueprint with new requirements and notes context, preserving confirmed content.
    """
    if not isinstance(old_json, dict):
        raise BlueprintError("Old blueprint must be a dictionary.")

    change_context = f"New Requirements / Changes: {new_requirements}"
    if notes:
        change_context += f"\nOptional Notes: {notes}"

    system_prompt = (
        SYSTEM_PROMPT
        + "\nYou are extending an existing system architecture blueprint. You must preserve confirmed content from the existing blueprint while intelligently integrating the new requirements, features, or bug fixes provided in the change context. Output the complete updated blueprint in strict JSON matching the required schema, preserving project_name, project_description, and target_audience."
    )

    user_prompt = f"""
Existing Blueprint JSON:
{json.dumps(old_json, indent=2)}

Change Context:
{change_context}

Please generate the updated, extended system architecture blueprint incorporating these changes while retaining core structure, project context, and verified decisions.
"""

    res = _call_ai(system_prompt, user_prompt)

    res["project_description"] = res.get("project_description") or old_json.get(
        "project_description", ""
    )
    res["target_audience"] = res.get("target_audience") or old_json.get(
        "target_audience", ""
    )
    res["project_name"] = res.get("project_name") or old_json.get(
        "project_name", "Untitled Project"
    )
    return res


def _unicode_to_ascii_tree(tree_str: str) -> str:
    if not isinstance(tree_str, str):
        return str(tree_str)
    return (
        tree_str.replace("└──", "+--")
        .replace("├──", "|--")
        .replace("│", "|")
        .replace("─", "-")
    )


def _wrap_text(text: str, width: int = 90) -> str:
    if not isinstance(text, str):
        text = str(text)
    paragraphs = text.split("\n")
    wrapped_paragraphs = []
    for p in paragraphs:
        if not p.strip():
            wrapped_paragraphs.append("")
        else:
            wrapped_lines = textwrap.wrap(p, width=width)
            wrapped_paragraphs.extend(wrapped_lines)
    return "\n".join(wrapped_paragraphs)


def sanitize_filename(project_name: str) -> str:
    """Sanitize project name into a safe filename, stripping path separators and odd characters."""
    if not isinstance(project_name, str) or not project_name.strip():
        return "codebreaker_blueprint.md"
    # Remove path separators, risky characters, and non-alphanumeric chars
    cleaned = re.sub(r'[\\/*?:"<>|]', "", project_name)
    cleaned = re.sub(r"[^a-zA-Z0-9_\-\s]", "", cleaned)
    cleaned = re.sub(r"\s+", "_", cleaned).strip("_")
    if not cleaned:
        return "codebreaker_blueprint.md"
    return f"{cleaned.lower()}_blueprint.md"


def _get_project_context(blueprint: dict):
    if not isinstance(blueprint, dict):
        blueprint = {}
    name = blueprint.get("project_name")
    if not name or str(name).lower() == "none":
        name = "Untitled Project"
    desc = blueprint.get("project_description")
    if not desc or str(desc).lower() == "none" or not str(desc).strip():
        desc = "N/A"
    aud = blueprint.get("target_audience")
    if not aud or str(aud).lower() == "none" or not str(aud).strip():
        aud = "N/A"
    return name, desc, aud


def sanitize_pdf_text(s):
    m = {
        "\u251c": "|",
        "\u2514": "+",
        "\u2500": "-",
        "\u2502": "|",
        "\u2011": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2022": "-",
        "\u2192": "->",
        "\u00a0": " ",
        "\u20e3": "",
        "\ufe0f": "",
    }
    return "".join(m.get(ch, "-" if ord(ch) > 255 else ch) for ch in str(s))


def _clean_item(item):
    import re as _re

    return _re.sub(r"^\d+\s*[\.\)]\s*", "", sanitize_pdf_text(item).strip())


def clean_roadmap_step(step) -> str:
    if step is None or str(step).lower() == "none":
        return "N/A"
    step_str = str(step).strip()
    step_str = re.sub(r"[\u20e3\ufe0f]", "", step_str)
    step_str = re.sub(r"^(\d+[\.\)]\s*|-\s*)", "", step_str).strip()
    return step_str


def build_pdf_lines(bp):
    ctx = bp.get("context") or {}
    L = [
        "# " + (bp.get("project_name") or "Blueprint"),
        "CodeBreaker System Architecture Blueprint",
        "",
        "## Project Context",
        "Name: " + sanitize_pdf_text(bp.get("project_name") or "N/A"),
        "Description: "
        + sanitize_pdf_text(
            ctx.get("description") or bp.get("project_description") or "N/A"
        ),
        "Target Audience: "
        + sanitize_pdf_text(
            ctx.get("target_audience") or bp.get("target_audience") or "N/A"
        ),
        "",
        "## Summary",
        sanitize_pdf_text(bp.get("summary") or "N/A"),
        "",
        "## Tech Stack",
    ]
    L += ["- " + sanitize_pdf_text(t) for t in (bp.get("tech_stack") or [])]
    L += ["", "## Folder Structure"]
    L += [
        sanitize_pdf_text(ln)
        for ln in str(bp.get("folder_structure") or "").splitlines()
    ]
    L += ["", "## Edge Cases & Risks"]
    L += ["- " + _clean_item(e) for e in (bp.get("edge_cases") or [])]
    L += ["", "## Implementation Roadmap"]
    L += [f"{i}. " + _clean_item(r) for i, r in enumerate(bp.get("roadmap") or [], 1)]
    L += ["", "Generated by CodeBreaker Workspace"]
    return L


def render_blueprint_pdf(bp):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_font("Helvetica", "", 10)
    for line in build_pdf_lines(bp):
        if any(ord(c) > 255 for c in line):
            raise ValueError("non-ascii reached pdf renderer: " + line[:40])
        if line.startswith("# "):
            pdf.set_font("Helvetica", "B", 15)
            pdf.multi_cell(0, 9, line[2:])
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "", 10)
        elif line.startswith("## "):
            pdf.set_font("Helvetica", "B", 12)
            pdf.multi_cell(0, 7, line[3:])
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "", 10)
        else:
            pdf.multi_cell(0, 5.5, line if line.strip() else " ")
            pdf.set_x(pdf.l_margin)
    return bytes(pdf.output())


def render_blueprint_markdown(blueprint: dict, export_date: str = None) -> str:
    """
    Render blueprint dict into clean Markdown format:
    - project context
    - title
    - summary
    - tech stack bullets
    - folder tree inside a code fence
    - edge cases
    - numbered roadmap
    - footer 'Generated by CodeBreaker v0.4 + date'
    Ensures None values never leak as 'None'.
    """
    if not isinstance(blueprint, dict):
        blueprint = {}

    if not export_date:
        export_date = datetime.date.today().isoformat()

    p_name, p_desc, p_aud = _get_project_context(blueprint)
    summary = blueprint.get("summary")
    if summary is None or str(summary).lower() == "none":
        summary = "No summary provided."

    tech_stack = blueprint.get("tech_stack")
    if tech_stack is None or str(tech_stack).lower() == "none":
        tech_stack = []

    folder_structure = blueprint.get("folder_structure")
    if folder_structure is None or str(folder_structure).lower() == "none":
        folder_structure = "No folder structure provided."

    edge_cases = blueprint.get("edge_cases")
    if edge_cases is None or str(edge_cases).lower() == "none":
        edge_cases = []

    roadmap = blueprint.get("roadmap")
    if roadmap is None or str(roadmap).lower() == "none":
        roadmap = []

    lines = []
    lines.append("# Project Context")
    lines.append(f"- **Name**: {p_name}")
    lines.append(f"- **Description**: {p_desc}")
    lines.append(f"- **Target Audience**: {p_aud}")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append(f"# {p_name}")
    lines.append("")
    lines.append("## Summary")
    lines.append(str(summary))
    lines.append("")

    lines.append("## Tech Stack")
    valid_tech = (
        [t for t in tech_stack if t is not None and str(t).lower() != "none"]
        if isinstance(tech_stack, list)
        else []
    )
    if valid_tech:
        for tech in valid_tech:
            lines.append(f"- {tech}")
    else:
        lines.append("- Not specified")
    lines.append("")

    lines.append("## Folder Structure")
    lines.append("```text")
    lines.append(str(folder_structure))
    lines.append("```")
    lines.append("")

    lines.append("## Edge Cases & Risks")
    valid_edges = (
        [e for e in edge_cases if e is not None and str(e).lower() != "none"]
        if isinstance(edge_cases, list)
        else []
    )
    if valid_edges:
        for edge in valid_edges:
            lines.append(f"- {edge}")
    else:
        lines.append("- Not specified")
    lines.append("")

    valid_roadmap = (
        [r for r in roadmap if r is not None and str(r).lower() != "none"]
        if isinstance(roadmap, list)
        else []
    )
    cleaned_roadmap = [clean_roadmap_step(s) for s in valid_roadmap]
    lines.append(f"## Implementation Roadmap ({len(cleaned_roadmap)} Steps)")

    if cleaned_roadmap:
        for i, step in enumerate(cleaned_roadmap, 1):
            lines.append(f"{i}. {step}")
    else:
        lines.append("1. Not specified")
    lines.append("")

    lines.append("---")
    lines.append(f"Generated by CodeBreaker v0.4 + {export_date}")

    return "\n".join(lines)


def render_blueprint_text(blueprint: dict, export_date: str = None) -> str:
    """
    Render blueprint dict into clean Plain Text format containing all sections
    and footer 'Generated by CodeBreaker v0.4.1'.
    """
    if not isinstance(blueprint, dict):
        blueprint = {}

    if not export_date:
        export_date = datetime.date.today().isoformat()

    p_name, p_desc, p_aud = _get_project_context(blueprint)
    summary = blueprint.get("summary")
    if summary is None or str(summary).lower() == "none":
        summary = "No summary provided."

    tech_stack = blueprint.get("tech_stack")
    if tech_stack is None or str(tech_stack).lower() == "none":
        tech_stack = []

    folder_structure = blueprint.get("folder_structure")
    if folder_structure is None or str(folder_structure).lower() == "none":
        folder_structure = "No folder structure provided."

    edge_cases = blueprint.get("edge_cases")
    if edge_cases is None or str(edge_cases).lower() == "none":
        edge_cases = []

    roadmap = blueprint.get("roadmap")
    if roadmap is None or str(roadmap).lower() == "none":
        roadmap = []

    lines = []
    lines.append("PROJECT CONTEXT")
    lines.append("-" * 15)
    lines.append(f"Name: {p_name}")
    lines.append(f"Description: {p_desc}")
    lines.append(f"Target Audience: {p_aud}")
    lines.append("")
    lines.append("=" * 40)
    lines.append("")

    lines.append(f"PROJECT: {p_name}")
    lines.append("=" * len(f"PROJECT: {p_name}"))
    lines.append("")
    lines.append("SUMMARY")
    lines.append("-" * 7)
    lines.append(str(summary))
    lines.append("")

    lines.append("TECH STACK")
    lines.append("-" * 10)
    valid_tech = (
        [t for t in tech_stack if t is not None and str(t).lower() != "none"]
        if isinstance(tech_stack, list)
        else []
    )
    if valid_tech:
        for tech in valid_tech:
            lines.append(f"- {tech}")
    else:
        lines.append("- Not specified")
    lines.append("")

    lines.append("FOLDER STRUCTURE")
    lines.append("-" * 16)
    lines.append(_unicode_to_ascii_tree(str(folder_structure)))
    lines.append("")

    lines.append("EDGE CASES & RISKS")
    lines.append("-" * 18)
    valid_edges = (
        [e for e in edge_cases if e is not None and str(e).lower() != "none"]
        if isinstance(edge_cases, list)
        else []
    )
    if valid_edges:
        for edge in valid_edges:
            lines.append(f"- {edge}")
    else:
        lines.append("- Not specified")
    lines.append("")

    valid_roadmap = (
        [r for r in roadmap if r is not None and str(r).lower() != "none"]
        if isinstance(roadmap, list)
        else []
    )
    cleaned_roadmap = [clean_roadmap_step(s) for s in valid_roadmap]
    heading_text = f"IMPLEMENTATION ROADMAP ({len(cleaned_roadmap)} Steps)"
    lines.append(heading_text)
    lines.append("-" * len(heading_text))

    if cleaned_roadmap:
        for i, step in enumerate(cleaned_roadmap, 1):
            lines.append(f"{i}. {step}")
    else:
        lines.append("1. Not specified")
    lines.append("")

    lines.append("-" * 40)
    lines.append(f"Generated by CodeBreaker v0.4.1 + {export_date}")

    return "\n".join(lines)


def render_blueprint_html(blueprint: dict, export_date: str = None) -> str:
    """
    Render blueprint dict into a self-contained styled HTML page using the markdown package:
    - includes title
    - includes 'Generated by CodeBreaker' footer
    - valid HTML wrapper and rendered headings.
    """
    if not export_date:
        export_date = datetime.date.today().isoformat()

    project_name = (
        blueprint.get("project_name") if isinstance(blueprint, dict) else None
    )
    if project_name is None or str(project_name).lower() == "none":
        project_name = "Untitled Project"

    md_content = render_blueprint_markdown(blueprint, export_date=export_date)
    html_body = markdown.markdown(md_content, extensions=["fenced_code", "tables"])

    html_page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - CodeBreaker System Blueprint</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background: #fdfdfd;
        }}
        h1, h2, h3 {{
            color: #111;
            border-bottom: 1px solid #eaeaea;
            padding-bottom: 0.3em;
        }}
        pre, code {{
            background: #f6f8fa;
            border-radius: 6px;
            padding: 0.2em 0.4em;
            font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 85%;
        }}
        pre {{
            padding: 1rem;
            overflow: auto;
        }}
        pre code {{
            background: transparent;
            padding: 0;
        }}
        ul, ol {{
            padding-left: 2rem;
        }}
        footer {{
            margin-top: 3rem;
            border-top: 1px solid #eaeaea;
            padding-top: 1rem;
            font-size: 0.9rem;
            color: #666;
            text-align: center;
        }}
    </style>
</head>
<body>
    {html_body}
    <footer>
        Generated by CodeBreaker Workspace + {export_date}
    </footer>
</body>
</html>
"""
    return html_page


def _latin1_safe(text) -> str:
    return sanitize_pdf_text(text)
