# CodeBreaker Development Log

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
