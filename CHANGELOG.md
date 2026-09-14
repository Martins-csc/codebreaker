# Changelog

All notable changes to the CodeBreaker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-09-14

### Added
- Supabase authentication integration (`supabase_client.py`) with environment-only configuration and lazy singleton client.
- Complete Streamlit auth gate (signup with email, password, and display name; login; sidebar sign-out).
- Session gate protecting all application modules (Home, Analyze, Blueprint, Engineering Log) when unauthenticated (`st.warning` + `st.stop()`).
- Engineering Log page with form submission (progress, bugs, learnings) and current-user entry listing ordered newest-first, relying on Row Level Security (RLS).
- Unit tests (`tests/test_supabase_client.py`) and live smoke test script (`scripts/smoke_supabase.py`).

## [0.2.1] - 2026-09-13

### Added
- Empty root `conftest.py` for robust test module discovery.
- Configurable `GROQ_MODEL` environment variable support in `ai_engine.py` (defaulting to `openai/gpt-oss-120b` as the primary Groq attempt).
- `GROQ_MODEL` configuration line in `.env.example`.

## [0.2.0] - 2026-09-13

### Added
- AI Engine wrapper (`ai_engine.py`) using `requests` with 10-second timeouts, custom `BlueprintError`, and robust JSON parsing (fenced code block extraction, brace block detection).
- Groq (`llama-3.3-70b-versatile` / `openai/gpt-oss-120b`) integration with automatic fallback to Gemini REST (`gemini-2.0-flash`).
- Streamlit UI wiring for Analyze page form (project name, problem, target audience, skill level) and Blueprint page tabs (`Tech Stack`, `Folder Structure`, `Edge Cases`, `Roadmap`, `Summary`).
- Unit tests (`tests/test_ai_engine.py`) covering parser helper, schema validation, and fallback handling with zero network calls.
- Live smoke test script (`scripts/smoke_groq.py`) for verifying Groq API connectivity and response structure.

## [0.1.0] - 2026-09-13

### Added
- Initial release of CodeBreaker UI framework using Streamlit.
- Home page with application title and tagline.
- Sidebar navigation placeholders for `Analyze`, `Blueprint`, and `Engineering Log` pages.
- Project baseline documentation: `README.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, and `docs/DEVLOG.md`.
- Basic configuration with `.env.example` and `.gitignore`.
