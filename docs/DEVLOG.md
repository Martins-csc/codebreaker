# CodeBreaker Development Log

## Entry 007: Deployment Readiness & Unified Config Loader (v0.5.0)
- **Date**: 2026-09-15
- **Author**: Engineering Team / Builder, Tester & Reviewer Agents
- **Milestone**: v0.5.0 Deployment Readiness

### Design Notes & Architectural Decisions
1. **Secrets Live in Cloud Dashboard Only**: All sensitive credentials (`GROQ_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`) are strictly excluded from version control and configured exclusively via Streamlit Community Cloud's Secret Management dashboard (`st.secrets`).
2. **Unified Config Loader & Fallback Order**: Implemented a robust config loader (`config.py`) following a strict resolution order:
   - Priority 1: `os.environ` (local development via `.env` or CI environments).
   - Priority 2: `st.secrets` (Streamlit Cloud runtime environment).
   - Priority 3: Optional default value or `ConfigError` raised for required configurations.
   - Guarded safely against missing Streamlit runtime environments or uninitialized secrets files.
3. **Repo Visibility & Security Rationale**: CodeBreaker repository is designed as a secure, public-ready open-source codebase. By strictly relying on public anon keys (`SUPABASE_ANON_KEY`), secure OAuth mediation, and PostgreSQL Row Level Security (RLS), the codebase contains zero hardcoded secrets and can be safely open-sourced without credential exposure.
4. **Pre-Deploy Audit & Test Suite**: Verified complete requirements (`streamlit`, `requests`, `supabase`, `markdown`, `pytest`), full test suite pass rate (21 tests green), and absence of risky regex patterns (`gsk_`, `eyJ`, `password=`).

## Entry 001: Initial Scaffold, Quota Interruption & Resume-by-Audit
- **Date**: 2026-09-13
- **Author**: Engineering Team / Orchestrator Agent
- **Milestone**: v0.1 Bootstrap & Resumption

### Summary of Events
1. **Initial Scaffold**: Created the core Streamlit application skeleton (`app.py`), project dependencies (`requirements.txt`), project configuration (`.gitignore`, `.env.example`), and documentation (`README.md`, `CHANGELOG.md`).
2. **Quota Interruption**: Development workflow was temporarily paused due to API quota constraints on upstream language models.
3. **Resume-by-Audit**: Upon resumption, executed a strict audit of existing project artifacts (`app.py`, `requirements.txt`, `README.md`, `CHANGELOG.md`) to verify state before proceeding. Established the principle that unexpected interruptions must always be recovered via non-destructive state auditing rather than blind overwriting.
4. **Documentation Completion**: Completed missing governance and architecture tracking docs (`docs/ROADMAP.md` and `docs/DEVLOG.md`).

## Entry 002: Roadmap Drift & Correction
- **Date:** 2026-09-13
- **Milestone:** v0.1 Governance
- **Event:** The orchestrator auto-generated a roadmap (AST parser, dependency graphs, collaboration) that diverged from the approved product plan and omitted deployment entirely.
- **Decision:** Approved shipping spine restored; the agent's ideas were demoted to a labeled v1.x backlog instead of being deleted.
- **Lesson:** When a document must match a decision, paste the exact content into the brief. Generated governance docs must never drift unreviewed.

## Entry 003: AI Engine & Blueprint Architecture (v0.2.0)
- **Date**: 2026-09-13
- **Author**: Engineering Team / Builder & Tester Agents
- **Milestone**: v0.2.0 AI Engine Integration

### Design Notes & Architectural Decisions
1. **Requests-Only Wrapper**: Implemented `ai_engine.py` using strictly `requests` without heavy SDK dependencies, maintaining a lightweight footprint and fast startup times.
2. **JSON-Forcing Prompt & Robust Parser**: Enforced strict JSON output via system instructions and built a robust multi-stage parser that handles plain JSON, markdown code fences (` ```json `), and prose-wrapped responses, followed by strict schema validation.
3. **Groq-to-Gemini Fallback Chain**: Designed a resilient provider chain that attempts Groq chat completions first (`llama-3.3-70b-versatile` with `openai/gpt-oss-120b` fallback) and automatically fails over to Gemini REST (`gemini-2.0-flash`) when keys are missing or provider errors occur.
4. **Security & Safety Guardrails**: Hardcoded 10-second timeouts on all network calls, custom `BlueprintError` exceptions with secret sanitization (redacting any active API keys), and strict `.env` git-ignore rules.

## Entry 004: Supabase Auth, Row Level Security & Engineering Log (v0.3.0)
- **Date**: 2026-09-14
- **Author**: Engineering Team / Builder & Tester Agents
- **Milestone**: v0.3.0 Accounts & Data Storage

### Design Notes & Architectural Decisions
1. **Anon Key & RLS**: All Supabase client interactions use the public `SUPABASE_ANON_KEY` combined with active user sessions. Data isolation and multi-tenant security rely entirely on Row Level Security (RLS) policies (`auth.uid() = user_id`) on the `engineering_log` table.
2. **Service Role Ban**: The privileged `service_role` key is strictly banned across all application and test code to prevent credential leakage and enforce the principle of least privilege.
3. **Session Management**: Session state (`access_token`, `refresh_token`, `user`) is securely managed inside Streamlit's `st.session_state` and synchronized with the Supabase client via `client.auth.set_session(...)`.
4. **Error Sanitization**: Authentication exceptions (such as invalid credentials or duplicate emails) are caught and presented as clean, sanitized `st.error` notifications without leaking internal exception strings or environment secrets.
5. **Email Confirmation**: Assumed email confirmation is disabled in Supabase development project settings for immediate account activation upon sign-up.

## Entry 004 Addendum: The Two-Layer Lesson
- **Date:** 2026-09-14
- **Event:** First live login hit 42501 on engineering_log despite perfect RLS policies.
- **Cause:** Table-level GRANTs for the authenticated role were missing; RLS governs rows, GRANTs govern roles.
- **Fix:** GRANT select/insert/update/delete on engineering_log and select/update on profiles TO authenticated.

## Entry 005: GitHub OAuth Second Door & PKCE Flow (v0.3.1)
- **Date**: 2026-09-14
- **Author**: Engineering Team / Builder, Tester & Reviewer Agents
- **Milestone**: v0.3.1 GitHub OAuth Integration

### Design Notes & Architectural Decisions
1. **Supabase Mediation**: OAuth secret never appears in code; Supabase mediates the handshake so the app never touches the OAuth secret.
2. **PKCE Code Exchange**: PKCE authorization code arrives via query params on page load and is exchanged immediately via `client.auth.exchange_code_for_session(code)`.
3. **Redirect URL Integrity**: `redirect_to` is dynamically built from the app's own URL (`st.context.url` with fallback).
4. **Session Consistency**: Session storage and synchronization (`client.auth.set_session`) are identical to the email authentication flow.
5. **Zero-Network Unit Testing**: Tested with mocked client methods and simulated query params, verifying clean query-param cleanup.

## Entry 006: Export & Habit Design (v0.4.0)
- **Date**: 2026-09-14
- **Author**: Engineering Team / Builder, Tester & Reviewer Agents
- **Milestone**: v0.4.0 Export & Habit

### Design Notes & Architectural Decisions
1. **Client-Side Export**: Used `st.download_button` over server filesystem writes to avoid cluttering local disk storage and ensure zero filesystem side-effects in cloud/serverless deployments.
2. **Sanitized Filenames**: Implemented rigorous filename sanitization (`sanitize_filename`) stripping path separators (`/`, `\`), null bytes, directory traversal patterns (`../`), and special characters to prevent path traversal vulnerabilities.
3. **Markdown Architecture**: Structured blueprint export with clear Markdown sections (title, summary, tech stack bullets, fenced folder tree, edge cases, numbered roadmap, and dynamic footer) with robust safeguards ensuring `None` values never leak as literal `"None"`.
4. **Engineering Log Habit & RLS Deletion**: Polished Engineering Log entries with styled expanders, timestamp date badges, and a delete button per entry executing client-side ownership verification (`user_id` match) in addition to Supabase RLS policies.
5. **UI Cleanup**: Replaced literal `<br>` artifact on the Login page with proper Markdown spacing.

## Entry 006 Addendum: Export for Real Humans (v0.4.1)
- **Date**: 2026-09-15
- **Author**: Engineering Team / Builder, Tester & Reviewer Agents
- **Milestone**: v0.4.1 Export Formats for Real Humans

### Export Rationale
1. **Markdown (.md)**: Tailored for repositories (`README.md`), serving as the project's instant front page on GitHub and Git platforms.
2. **HTML (.html)**: Self-contained, cleanly styled web page featuring rendered headings and footer, optimized for human reading on mobile devices and browsers ("Open with Chrome/Safari").
3. **Plain Text (.txt)**: Universal fallback format ensuring compatibility with any text editor or AI coding assistant spec without formatting barriers.
4. **Origin Story**: Born from the founder's own Android "Open with" confusion when attempting to view architecture specs on mobile.
5. **Security & Sanitization**: Reused rigorous `sanitize_filename` across all three export formats with zero secret leakage.
