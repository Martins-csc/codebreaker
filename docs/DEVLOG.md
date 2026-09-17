# CodeBreaker Development Log

## Entry 014: First Outage Postmortem & Compile Gate Hotfix (v1.0.5)
- **Date**: 2026-09-17
- **Author**: Engineering Team / Builder, Reviewer & Orchestrator Agents
- **Milestone**: v1.0.5 Hotfix & Pre-Seal Compile Gate

### Outage Postmortem & Root Cause Analysis
1. **Cause**: A broken `try:` block indentation in `app.py` (`client = get_client()` unindented relative to `try:`) was shipped via an automated commit, resulting in a production-down `IndentationError` when launching the Streamlit app.
2. **Why Tests Missed It**: The existing unit test suite (`tests/`) tests individual modules (`security.py`, `config.py`, `supabase_client.py`, `ai_engine.py`) and component logic, but no test file imports `app.py` directly (as `app.py` is the top-level Streamlit entrypoint containing UI event loops and script execution code).
3. **Fix**: 
   - **Hotfix**: Restored correct `try/except` indentation and structure in `app.py` (~lines 212-280) preserving all intended signup error handling and 30-second cooldown logic.
   - **Pre-Seal Compile Gate**: Instituted a mandatory pre-seal compile check (`python -m py_compile app.py`) across all delivery pipelines to catch syntax and indentation errors before code sealing.
4. **Verification**: `python -m py_compile app.py` executed successfully with zero output, and all 38 pytest unit tests passed successfully.

## Entry 013: Abuse Guards Family — Defense in Depth & Batching Rule (v1.0.4)
- **Date**: 2026-09-17
- **Author**: Engineering Team / Builder, Tester & Reviewer Agents
- **Milestone**: v1.0.4 Abuse Guards Family

### Design Notes & Architectural Decisions
1. **Defense in Depth Strategy**: Implemented a multi-layered security approach for abuse prevention:
   - **Layer 1 (Platform)**: Supabase platform-layer rate limits and authentication security.
   - **Layer 2 (Application Handlers & UI)**: Strict input length caps (email ≤254, password ≤128, display name ≤80, problem/idea ≤2000, log fields ≤5000) enforced both on UI input components (`max_chars`) and in server-side handlers returning sanitized generic error messages.
   - **Layer 3 (Password Policy)**: Minimum 8 characters with at least one letter and one number, live `st.caption` hints, and sanitized rejection messages (preventing rule leakage).
   - **Layer 4 (UX Cooldown)**: 30-second signup cooldown managed via `st.session_state` timestamps after any failed signup attempt, with explicit code comments noting server-side rate limits remain Supabase's responsibility.
2. **Category Batching Rule Applied**: Applied the category batching rule to the security domain, batching password validation, input caps, and signup cooldown together into a cohesive **Abuse Guards Family** rather than scattering safeguards across random commits.
3. **Security Audit & Test Coverage**: Verified zero user-enumeration vectors in error messages, identical limits in UI and handlers, and zero secrets in code. Added comprehensive unit tests in `tests/test_security.py` covering weak-password table rejection, handler input caps with mocked Supabase, cooldown session state logic, empty email/password checks, email format validation, and 7-character password rejection. All 38 unit tests passing successfully.

## Entry 012: First-Run Guidance, Onboarding Tour & The Category Batching Rule (v1.0.3)
- **Date**: 2026-09-17
- **Author**: Engineering Team / Builder, Tester & Reviewer Agents
- **Milestone**: v1.0.3 First-Run Guidance Family & About Page

### The Category Batching Rule (Credited to Founder)
- **Definition**: Group related capabilities by output category or functional domain rather than scattering them across disparate releases. Batching by category ensures cohesive user experience, unified documentation, and thorough domain-specific verification.
- **Case Study (v0.4.1 / v1.0.2 PDF Split)**: 
  - In v0.4.1, the export format category was established by batching Markdown (.md), Plain Text (.txt), and HTML (.html) exports together. 
  - When PDF export was requested in v1.0.2, rather than scattering document rendering features across random releases, it was naturally batched into the existing export category family using pure-python `fpdf2`.
  - Similarly, v1.0.3 establishes the **First-Run Guidance Family** by batching the dismissible onboarding tour and comprehensive About page together, rather than building them in isolated silos.

### Design Notes & Architectural Decisions
1. **Onboarding Tour**: A dismissible 3-step walkthrough (Analyze, Blueprint, Engineering Log) displayed on first login of a session via `st.expander` and managed via `st.session_state["tour_dismissed"]`. It displays once per session and never blocks the authentication gate.
2. **About Page**: A dedicated navigation item (`About`) outlining the mission statement ("Plan before you code"), classroom lecturer usage (`Assignment Grade = System Blueprint + Engineering Log`), the two auth doors (Email/Password + GitHub OAuth), the four export formats, public repository link, and version footer (`v1.0.3`).
3. **Security & Zero-Network Testing**: All tests run with zero network calls and zero secret dependencies. Tour state flags are isolated in session state.
4. **Test Coverage**: Added dedicated unit tests in `tests/test_onboarding_and_about.py` covering tour rendering once per session, click-to-dismiss persistence, and About page content validation. All 32 unit tests passing successfully.

## Entry 011: PDF Export & Pure-Python Portability (v1.0.2)
- **Date**: 2026-09-17
- **Author**: Engineering Team / Builder, Tester & Reviewer Agents
- **Milestone**: v1.0.2 PDF Export

### Design Notes & Architectural Decisions
1. **Pure-Python Portability**: Selected `fpdf2` as the PDF generation library because it is 100% pure Python, pip-installs cleanly on both Termux and Streamlit Community Cloud, and requires zero native binaries (such as wkhtmltopdf or pango).
2. **In-Memory Generation**: All PDF documents are generated in-memory (`BytesIO` / `pdf.output()`) with zero temp files written to disk, ensuring high performance and zero filesystem clutter in serverless cloud environments.
3. **Completing the Export Story**: Fulfills the multi-format export vision: Markdown (.md) for repositories, HTML (.html) for browsers, Plain text (.txt) for editors, and PDF (.pdf) for human readers and offline printing.
4. **Security & Safety Guardrails**: Reused robust filename sanitization (`sanitize_filename`), ensured `None` values never leak as `"None"`, and verified zero secrets are present in PDF metadata or content.
5. **Test Coverage**: Added comprehensive unit tests in `tests/test_ai_engine.py` verifying PDF format (`b"%PDF"`), minimum size (>1KB), safety, and zero network usage. All 28 tests passing successfully.

## Entry 010: Admin Pulse & Owner-Only Visibility (v1.0.1)
- **Date**: 2026-09-16
- **Author**: Engineering Team / Builder, Tester & Reviewer Agents
- **Milestone**: v1.0.1 Admin Pulse

### Design Notes & Architectural Decisions
1. **Owner-Only Visibility**: Implemented `ADMIN_EMAIL` configuration checking in `config.py` (supporting `os.environ` and `st.secrets` fallback) to restrict administrative metrics visibility exclusively to the site owner.
2. **Efficient Counting**: Leveraged Supabase `select("id", count="exact")` queries to fetch exact counts of registered users (`profiles` table) and engineering log entries without downloading unnecessary row payloads.
3. **Environment Configuration**: Added `ADMIN_EMAIL` entry to `.env.example` and local `.env` file without exposing or printing secrets.
4. **Test Coverage**: Added dedicated unit tests (`tests/test_admin_pulse.py`) ensuring owners see counts and non-admins see nothing, with zero network calls and all tests passing successfully.

## Entry 009: Email Confirmation & Production Safety (v1.0.0)
- **Date**: 2026-09-15
- **Author**: Engineering Team / Builder, Tester & Reviewer Agents
- **Milestone**: v1.0.0 Email Confirmation

### Design Notes & Architectural Decisions
1. **Separation of Concerns**: Supabase handles email delivery and token generation during `auth.sign_up`, whereas CodeBreaker manages UX state transitions, blocking login gates for unconfirmed users (`confirmed_at is None` or empty identities), and displaying clear guidance (`st.info("Check your email to confirm your account")`).
2. **Resend Confirmation Workflow**: Added "Resend confirmation email" button on the Login page, invoking `supabase.auth.resend({"type": "signup", "email": email})`. Code comments note server-side rate limits and future client-side debounce considerations.
3. **Security & Error Sanitization**: Audited email templates and error handling to ensure zero secrets are exposed and no sensitive user data leaks in exception messages.
4. **Test Coverage**: Verified robust unit test suite (`tests/test_auth_confirmation.py`) with zero network calls and all 24 tests passing successfully.

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

## Entry 008: Launch Day
- **Date:** 2026-09-15
- **Event:** CodeBreaker deployed to Streamlit Community Cloud: https://martins-codebreaker.streamlit.app
- **Decisions:** repo stays public (Cloud free tier reads public repos only; zero secrets in repo, audited twice); owner-only toolbar vs public view clarified (dev controls invisible to visitors); analytics anonymize viewers by default.
- **Mechanics:** git push = deploy via GitHub webhook; secrets live only in Cloud dashboard (st.secrets) and local .env; config.py loads os.environ first, st.secrets as fallback.
- **Lesson:** platform constraints (OAuth scopes) decide repo visibility, not preference — evidence over assumption.

## Entry 008: Launch Day
- **Date:** 2026-09-15
- **Event:** CodeBreaker deployed to Streamlit Community Cloud: https://martins-codebreaker.streamlit.app
- **Decisions:** repo stays public (Cloud free tier reads public repos only; zero secrets in repo, audited twice); owner-only toolbar vs public view clarified (dev controls invisible to visitors); analytics anonymize viewers by default.
- **Mechanics:** git push = deploy via GitHub webhook; secrets live only in Cloud dashboard (st.secrets) and local .env; config.py loads os.environ first, st.secrets as fallback.
- **Lesson:** platform constraints (OAuth scopes) decide repo visibility, not preference — evidence over assumption.
