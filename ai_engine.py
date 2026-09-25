import datetime
import json
import os
import re

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

    errors = []

    # Attempt Groq
    try:
        return _call_groq(SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        err_msg = str(e)
        for secret in [
            get_config("GROQ_API_KEY"),
            get_config("GEMINI_API_KEY"),
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
            get_config("GROQ_API_KEY"),
            get_config("GEMINI_API_KEY"),
        ]:
            if secret:
                err_msg = err_msg.replace(secret, "[REDACTED]")
        errors.append(f"Gemini failed: {err_msg}")

    raise BlueprintError(f"All AI providers failed. Details: {'; '.join(errors)}")


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


def render_blueprint_markdown(blueprint: dict, export_date: str = None) -> str:
    """
    Render blueprint dict into clean Markdown format:
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

    project_name = blueprint.get("project_name")
    if project_name is None or str(project_name).lower() == "none":
        project_name = "Untitled Project"

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
    lines.append(f"# {project_name}")
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

    lines.append("## Implementation Roadmap")
    valid_roadmap = (
        [r for r in roadmap if r is not None and str(r).lower() != "none"]
        if isinstance(roadmap, list)
        else []
    )
    if valid_roadmap:
        for i, step in enumerate(valid_roadmap, 1):
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

    project_name = blueprint.get("project_name")
    if project_name is None or str(project_name).lower() == "none":
        project_name = "Untitled Project"

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
    lines.append(f"PROJECT: {project_name}")
    lines.append("=" * len(f"PROJECT: {project_name}"))
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
    lines.append(str(folder_structure))
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

    lines.append("IMPLEMENTATION ROADMAP")
    lines.append("-" * 22)
    valid_roadmap = (
        [r for r in roadmap if r is not None and str(r).lower() != "none"]
        if isinstance(roadmap, list)
        else []
    )
    if valid_roadmap:
        for i, step in enumerate(valid_roadmap, 1):
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


class CodeBreakerPDF(FPDF):
    def __init__(self, export_date: str):
        super().__init__()
        self.export_date = export_date

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(
            0,
            10,
            f"Generated by CodeBreaker Workspace + {self.export_date}",
            align="C",
        )


def render_blueprint_pdf(blueprint: dict, export_date: str = None) -> bytes:
    """
    Render blueprint dict into a professional PDF document as bytes:
    - title header (project name + tagline)
    - summary
    - tech stack bullets
    - folder tree in a monospace block
    - edge cases & risks
    - numbered roadmap
    - footer 'Generated by CodeBreaker v1.0.2 + date'
    In-memory generation only (zero temp files on disk).
    Ensures None values never leak as 'None'.
    """
    if not isinstance(blueprint, dict):
        blueprint = {}

    if not export_date:
        export_date = datetime.date.today().isoformat()

    project_name = blueprint.get("project_name")
    if project_name is None or str(project_name).lower() == "none":
        project_name = "Untitled Project"

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

    pdf = CodeBreakerPDF(export_date)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    printable_w = pdf.w - pdf.l_margin - pdf.r_margin

    # Title header: project name + tagline
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(17, 17, 17)
    pdf.cell(
        printable_w, 10, str(project_name), new_x="LMARGIN", new_y="NEXT", align="L"
    )

    pdf.set_font("helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(
        printable_w,
        5,
        "CodeBreaker System Architecture Blueprint",
        new_x="LMARGIN",
        new_y="NEXT",
        align="L",
    )
    pdf.ln(4)

    def add_section_heading(title):
        pdf.set_font("helvetica", "B", 13)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(printable_w, 8, title, new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)

    # Summary
    add_section_heading("Summary")
    pdf.multi_cell(printable_w, 5.5, str(summary))
    pdf.ln(3)

    # Tech Stack
    add_section_heading("Tech Stack")
    valid_tech = (
        [t for t in tech_stack if t is not None and str(t).lower() != "none"]
        if isinstance(tech_stack, list)
        else []
    )
    if valid_tech:
        for tech in valid_tech:
            pdf.cell(printable_w, 5.5, f"- {tech}", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(printable_w, 5.5, "- Not specified", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Folder Structure (monospace block)
    add_section_heading("Folder Structure")
    pdf.set_font("Courier", size=9)
    pdf.set_fill_color(246, 248, 250)
    tree_text = str(folder_structure)
    pdf.multi_cell(printable_w, 4.5, tree_text, fill=True)
    pdf.set_font("helvetica", "", 10)
    pdf.ln(3)

    # Edge Cases & Risks
    add_section_heading("Edge Cases & Risks")
    valid_edges = (
        [e for e in edge_cases if e is not None and str(e).lower() != "none"]
        if isinstance(edge_cases, list)
        else []
    )
    if valid_edges:
        for edge in valid_edges:
            pdf.multi_cell(printable_w, 5.5, f"- {edge}")
    else:
        pdf.cell(printable_w, 5.5, "- Not specified", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Implementation Roadmap
    add_section_heading("Implementation Roadmap")
    valid_roadmap = (
        [r for r in roadmap if r is not None and str(r).lower() != "none"]
        if isinstance(roadmap, list)
        else []
    )
    if valid_roadmap:
        for i, step in enumerate(valid_roadmap, 1):
            pdf.multi_cell(printable_w, 5.5, f"{i}. {step}")
    else:
        pdf.cell(printable_w, 5.5, "1. Not specified", new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())
