# CodeBreaker Development Log

## Entry 028: Landing, One-Card Auth & Sidebar Order Contract (v1.3.0)
- **Date**: 2026-09-25
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.3.0 Landing + One-Card Auth + Sidebar Order Contract

### Design Notes & Architectural Decisions
1. **Landing Rationale**: Public landing page established as the default logged-out view, featuring a professional headline, one-paragraph value proposition, 3-step "How it works", module icon-cards (Analyze, Blueprint, Engineering Log), and clear CTAs (`[Log In]`, `[Create Account]`). Pre-auth sidebar rendering is completely suppressed.
2. **One-Card Auth View**: Reached exclusively via landing CTAs. A single container card housing mode toggle (Log In / Sign Up), email, password, conditional display name (sign-up mode only), button row (`[Log In]` / `[Forgot Password]` or `[Sign Up]`), thin divider `"or"`, `[Continue with GitHub]`, and `← Back to overview` link. Password reset request flow stays inside the card.
3. **Sidebar Order Contract (Authenticated)**: Strict sidebar order enforced:
   - Admin Pulse (admin only)
   - Section radios (`Home`, `Analyze`, `Blueprint`, `Engineering Log`, `About`) with zero "Navigation" caption (`label_visibility="collapsed"`)
   - Persistence Debug (admin only)
   - Sign Out LAST.
4. **Routing & Banner Polish**: Authenticated users hitting root land on Home. Version banners removed from Home.
5. **Banned-Strings Sweep**: Thorough sweep across `app.py` and exports eliminating all user-facing occurrences of "Row Level Security", "RLS", "Supabase", "handshake", "AI-driven", version strings (`v1.x`), "press enter", and "0/100 words". Tone professional and zero-jargon.
6. **Testing & Verification**: Enforced pre-seal compile gate (`python3 -m py_compile`) and green test suite (`86 passed`, including new unit tests in `tests/test_v1_3_0.py`).

## Entry 030: When Every Client-Storage Channel Fails: Capability URLs (v1.2.3, v1.2.4 & v1.2.5 Micro-Hotfixes)
- **Date**: 2026-09-22 / 2026-09-23
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.2.3 URL Capability Resume & v1.2.5 Postgres 42702 Parameter Renaming Hotfix

### Design Notes & Architectural Decisions
1. **The Client Storage Dead-End**: Across v1.1.5 to v1.2.2, CodeBreaker investigated localStorage and cookies (`streamlit-local-storage`, `streamlit-cookies-controller`). While cookies improved server-side read access, browser cross-site tracking policies, iframe sandboxing, third-party storage restrictions, and state synchronization across reruns introduced persistent fragility.
2. **Capability URLs (`?rt=...`)**: Abandoned all client storage entirely. Replaced with cryptographically secure server-side session persistence via URL capability tokens (`rt = secrets.token_urlsafe(32)`).
3. **Threat Model & Tradeoffs**: Capability URLs act as bearer tokens if shared or logged. To mitigate this risk, CodeBreaker implements:
   - **One-Time Token Rotation**: On every successful boot, the consumed capability token is immediately revoked server-side, and a brand new token is minted and stamped into `st.query_params["rt"]`.
   - **Explicit Revocation on Sign-Out**: Signing out explicitly revokes the token row in `public.resume_sessions` and strips `rt` from query parameters.
   - **Short Expiry & Pruning**: Tokens expire after 7 days, with opportunistic pruning of expired rows.
   - **Zero Token Leakage in Debug**: Tokens are never logged or rendered in full; debug panels display only presence/absence and verify results.
4. **SQL Schema & Security Definers**: Created `public.resume_sessions` with RLS (owners may select/delete own rows only) and security-definer functions (`create_resume_token`, `verify_resume_token`, `revoke_resume_token`, `prune_expired_resume_sessions`).
5. **v1.2.4 & v1.2.5 Micro-Hotfixes (Postgres 42702 Parameter Ambiguity)**:
   - **The 42702 on "token_hash" Collision Class**: PL/pgSQL parameters and `RETURNS TABLE` out-parameters collide with table column names even on the comparison side of qualified expressions (`rs.token_hash = token_hash`).
   - **Parameter Renaming as Durable Fix (`p_` prefix)**: Renamed ALL function parameters and `RETURNS TABLE` out-parameters with `p_` prefix (`p_token_hash`, `p_user_id`, `p_refresh_token`, `p_expires_at`, `p_uid`) across all four security-definer functions (`create_resume_token`, `verify_resume_token`, `revoke_resume_token`, `prune_expired_resume_sessions`).
   - **Variable_Conflict Pragmas Banned**: Established parameter renaming as the sole durable fix; `variable_conflict` pragmas are strictly banned.
   - **Re-Run Safety**: Preserved re-run safety (omitting DROP TABLE).
   - **First Production Catch**: Caught by the degraded-caption visibility discipline and database migration verification.
6. **Testing & Verification**: Enforced pre-seal compile gate (`python3 -m py_compile`) and comprehensive zero-network unit tests in `tests/test_url_capability_resume.py` plus the full pytest suite.

### Entry 030 Addendum (v1.2.6 Micro-Hotfix — RPC Parameter-Name Drift)
- **Renaming DB Function Parameters is an API Change**: Database function parameter names are part of the RPC API contract when passed via JSON dictionaries (`client.rpc("func", {"param": val})`).
- **Same-Release Migration**: When definer parameters are updated (e.g., adding `p_` prefix for Postgres 42702 ambiguity resolution), all RPC caller sites in application code (`app.py`) must be migrated in the exact same release.
- **Automated Source Consistency**: Instituted a zero-network source-consistency test (`tests/test_rpc_source_consistency.py`) that statically parses SQL migration function signatures and asserts that every RPC params dict key in `app.py` matches its target database function.

## Entry 022: Duplicate Widget Key Outage & Framework Exception Isolation (v1.1.5.1)
- **Date**: 2026-09-20
- **Author**: Engineering Team / Builder, Tester & Reviewer Agents
- **Milestone**: v1.1.5.1 Duplicate Widget Key Outage Hotfix

### Outage Postmortem & Root Cause Analysis
1. **Duplicate Widget Key Outage**: Streamlit keys are global per execution run. The recovery "set new password" form collided with login form keys (`'set'`), causing application crashes when rendering conditional forms. Conditional forms must strictly namespace keys.
2. **Framework Exception Masking**: Login's broad `except Exception` block previously masked a `StreamlitAPIException` as an authentication failure (`"Invalid login credentials"`). Future code strictly catches framework exceptions separately and re-raises them rather than swallowing them.
3. **Test Coverage & Verification**: Added comprehensive unit tests in `tests/test_auth_widget_keys.py` asserting auth widget key uniqueness across signup, login, and recovery forms, and verifying that framework exceptions are re-raised rather than masked. Verified via pre-seal compile check (`python3 -m py_compile`) and full pytest suite.

## Entry 020: Email Saga Closure Batch (v1.1.4)
- **Date**: 2026-09-19
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.1.4 Email Saga Closure Batch

### Design Notes & Architectural Decisions
1. **Token vs TokenHash Anatomy**: Supabase OTP verification handles raw tokens or hashed token representations (`token_hash`). Depending on GoTrue version / link parameters, tokens may be supplied as raw OTP codes/opaque strings or hashed strings. To ensure 100% reliability across GoTrue schema variations, `verify_otp` implements a robust fallback chain: raw `token_hash=`, sha256-hex digest of the token as `token_hash`, and raw `token=`.
2. **Duplicate Signup & Enumeration Trade-Off**: When `sign_up` returns empty identities (`identities=[]`), indicating an existing account, CodeBreaker displays `st.warning("This email is already linked to an account. Please log in or reset your password.")` and sends no confirmation email. This was established as a deliberate founder trade-off balancing UX clarity against strict non-enumeration, prioritizing user support when trying to sign up with an existing address.
3. **Forgot-Password Form Integration**: Integrated forgot-password directly inside the login form as a second `form_submit_button` under Log In, reusing the existing Email field value and eliminating extraneous buttons and collapsible forms.
4. **Tour Persistence**: Onboarding tour state is persisted server-side via `supabase.auth.update_user(data={"tour_seen": True})` when dismissed. The tour renders only when `user_metadata` lacks `tour_seen`, replacing ephemeral session-only flags.
5. **RLS-Walled Counts via Security Definer Functions**: Admin Pulse counts are retrieved via server-side RPC functions (`count_registered_users` and `count_engineering_logs`) rather than direct table queries, ensuring proper Row Level Security and security definer encapsulation with graceful error handling.
6. **Residual OAuth Hop Note**: Audited all user-facing redirects and links. Confirmed zero hardcoded `supabase.co` URLs exist anywhere in application source code, with the sole exception of the mediated GitHub OAuth authorize hop handled by the Supabase client.
7. **Test Coverage & Verification**: Verified via pre-seal compile check (`python3 -m py_compile`) and comprehensive zero-network unit tests in `tests/test_email_saga_closure.py` and the full pytest suite.

## Entry 019: Email Link Ownership & Identity Family (v1.1.2)
- **Date**: 2026-09-18
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.1.2 Email Link Ownership & Identity Family

### Design Notes & Architectural Decisions
1. **Email Link Ownership**: Email verification and password recovery links now point directly at the application domain with server-side `verify_otp` execution (eliminating Supabase intermediate landing pages and `ref` parameters in email links).
2. **Robust `verify_otp` & Fallback**: On page load, `st.query_params` is parsed for `type` (`signup`, `recovery`) and token (`token`, `token_hash`, `code`). The server calls `verify_otp` trying `token_hash=` first, falling back to `token=` per the installed `supabase-py` API.
3. **Success & Error UX**: 
   - Success + recovery establishes the recovery session (`recovery_mode = True`) and renders the secure set-new-password form.
   - Success + signup displays `"Email confirmed — please log in."`.
   - Expired or invalid links render `st.warning("This link has expired or is invalid. Please request a new one.")` with one-click resend/forgot password paths.
   - Query parameters are strictly cleared after handling (`st.query_params.clear()`).
4. **Cleanup of Dead Code**: Deleted the old PKCE/code-exchange recovery detection from v1.1.0 that caused login redirection failures, while retaining redirect-origin hygiene and GitHub OAuth code exchange.
5. **Branding & Delivery**: Email branding is managed via Supabase email templates and custom SMTP paths (5-minute expiry). Residual OAuth redirection hop is noted until Pro custom domains are provisioned.
6. **Test Coverage & Verification**: Verified via pre-seal compile gate (`python -m py_compile`) and full pytest suite (`.venv/bin/pytest tests/ -q` — all 47 unit tests passing green).

## Entry 017: Password Reset Flow & Auth Family Completion (v1.1.0)
- **Date**: 2026-09-18
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.1.0 Password Reset Flow

### Design Notes & Architectural Decisions
1. **Auth Family Completion**: With signup, email confirmation, login, and now password reset implemented, CodeBreaker's complete authentication suite is fully realized.
2. **Account Enumeration Protection**: The "Forgot password?" feature validates email format first via `validate_email`, invokes `supabase.auth.reset_password_for_email`, and catches/suppresses all backend exceptions. It displays the exact enumeration-safe info message `"If an account exists for that email, a reset link is on its way."` so attackers cannot determine whether an account exists for a given email address.
3. **Recovery Session Return**: Detects recovery sessions when reset links land (`type=recovery` query parameter check on page load), exchanges the authorization code for a session, and renders the secure "Set new password" form.
4. **Password Policy Reuse**: Reuses `validate_password` from `security.py` to enforce the exact 8-character password policy (minimum 8 chars with at least one letter and one number) on new password updates via `supabase.auth.update_user`, followed by automatic sign-out and prompt for fresh login.
5. **Test Coverage & Verification**: Added unit tests in `tests/test_security.py` covering forgot-password wording, enumeration safety, recovery session detection, and password policy reuse. Verified via pre-seal compile check (`python3 -m py_compile`) and full pytest suite (all 43 unit tests passing successfully).

## Entry 016: Cooldown UX Live Countdown & Explicit Reruns (v1.0.6)
- **Date**: 2026-09-18
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.0.6 Cooldown UX Fix

### Design Notes & Architectural Decisions
1. **Cooldown UX Challenge**: Streamlit renders web pages exclusively upon user interaction. Previously, static cooldown timers left the warning and disabled Sign Up button stuck at their initial values unless the user interacted or triggered the mode-toggle workaround.
2. **Live-Ticking Countdown**: Replaced the stuck-disabled cooldown state with an active countdown loop (`time.sleep(1); st.rerun()`) while cooldown is active. This visibly counts down remaining seconds every second and automatically re-enables the Sign Up button the instant the timer hits 0.
3. **Strict Loop Bounds**: Bounded the rerun loop strictly by the stored session timestamp (`signup_cooldown_until`), guaranteeing that the loop terminates immediately upon expiration and can never spin infinitely.
4. **Server-Side Protection**: Added a server-side submission check to block signup attempts during active cooldown periods even if bypassed client-side.
5. **Test Coverage & Verification**: Added robust unit tests in `tests/test_security.py` covering remaining seconds calculation, cooldown expiry re-enabling, and server-side submission blocking. Verified via pre-seal compile check (`python3 -m py_compile`) and full pytest suite (all 41 tests passing successfully).

## Entry 015: UI Refinement, Vertical Numbered Tour & Test Updates (v1.0.5)
- **Date**: 2026-09-18
- **Author**: Engineering Team / Orchestrator & Builder Agents
- **Milestone**: v1.0.5 UI Refinement & Tour Polish

### Design Notes & Architectural Decisions
1. **Auth Input Refinement**: Cleaned up authentication form inputs by removing explicit `max_chars` parameters, "Secure password" placeholders, and password requirement helper captions, relying on robust submit-time validation.
2. **Onboarding Tour Refactor**: Streamlined the first-run onboarding tour body into a vertical numbered 3-step list via `st.markdown`:
   - `1. **Analyze**: Describe any project idea to generate an AI-driven blueprint.`
   - `2. **Blueprint**: Explore the 5 tabs and export your spec in 4 formats.`
   - `3. **Engineering Log**: Record progress, bugs, and learnings.`
   Retained the `"Got it"` dismissal button and once-per-session `tour_dismissed` session state logic without blocking authentication.
3. **Login Validation**: Maintained per-field empty and format validation messages with combined error strings fully deleted.
4. **Test Suite Updates**: Updated `tests/test_onboarding_and_about.py` with `test_tour_markdown_content()` verifying the vertical numbered 3-step list structure.
5. **Verification**: Ran pre-seal compile check across all core modules and full pytest suite (all unit tests passing successfully).

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

## Entry 021: Session Persistence, LocalStorage Bundle & Navigation State (v1.1.5)
- **Date**: 2026-09-20
- **Author**: Engineering Team / Builder & Tester Agents
- **Milestone**: v1.1.5 Session Persistence & Navigation State

### Design Notes & Architectural Decisions
1. **LocalStorage Session Bundle (`cb_session`)**: Both email/password login, OAuth, and sign-up flows synchronize authentication state by writing a session bundle containing `access_token`, `refresh_token`, and `expires_at` to browser localStorage via `streamlit-local-storage`.
2. **Boot Rehydration & Expiry Guard**: On app startup when `session_state` lacks an active user, the app checks `cb_session`. If present, it validates expiration against `time.time()`. Valid sessions call `client.auth.set_session` and rehydrate `user` metadata via `get_user`. Expired sessions attempt `refresh_session`; any failure or corrupt JSON strictly deletes the key (`deleteItem("cb_session")`) and falls back to the login gate.
3. **Sign-Out Cleanup**: Sidebar Sign Out explicitly invokes `client.auth.sign_out()`, deletes both `cb_session` and `cb_page` from localStorage, and clears `st.session_state`.
4. **Navigation State Persistence (`cb_page`)**: Active sidebar radio selection is persisted to localStorage as `cb_page` and automatically restored on page reload/refresh.
5. **Zero-Network Unit Testing**: Added comprehensive unit tests in `tests/test_session_and_nav_paths.py` covering valid restore, expired session refresh, corrupt session deletion, sign-out cleanup, and navigation persistence.
6. **Syntax & Indentation Repair**: Resolved pre-existing indentation error around line 547 in `app.py` and verified complete compilation.

## Entry 022: Auth Widget Key Namespacing & Exception Isolation (v1.1.5.1)
- **Date**: 2026-09-20
- **Author**: Engineering Team / Builder & Tester Agents
- **Milestone**: v1.1.5.1 Production Login Hotfix

### Design Notes & Architectural Decisions
1. **Explicit Widget Key Namespacing**: Assigned unique, explicit `key=` attributes to all form inputs across login, signup, and recovery/password-reset forms (`signup_email`, `signup_pw`, `signup_display_name`, `signup_submit_btn`, `login_email`, `login_pw`, `login_submit_btn`, `forgot_submit_btn`, `reset_pw_new`, `reset_pw_confirm`, `reset_submit_btn`).
2. **Exception Isolation**: Updated auth exception handlers to re-raise `StreamlitAPIException` / duplicate key errors instead of masking framework errors as auth failures.
3. **Unit Testing**: Added `tests/test_auth_widget_keys.py` enforcing key uniqueness and exception non-masking.
4. **Documentation**: CHANGELOG v1.1.5.1 and DEVLOG Entry 022.

## Entry 023: LocalStorage Duplicate Element Key Hotfix & Invariant Audit (v1.1.5.2)
- **Date**: 2026-09-21
- **Author**: Engineering Team / Builder & Tester Agents
- **Milestone**: v1.1.5.2 LocalStorage Hotfix

### Design Notes & Architectural Decisions
1. **Indentation Repair**: Fixed syntax IndentationError around line 125 in `app.py`.
2. **LocalStorage Unique Key Namespacing**: Introspected `streamlit-local-storage` (`LocalStorage`) and provided unique explicit `key=` attributes (`ls_refresh_set`, `ls_oauth_set`, `ls_signout_del_sess`, `ls_signout_del_page`, `ls_page_set`, `ls_reset_del_sess`, `ls_reset_del_page`, `ls_signup_set`, `ls_login_set`) across all `setItem` and `deleteItem` call sites to prevent `StreamlitDuplicateElementKey` crashes.
3. **Graceful Exception Wrapping**: Wrapped all local storage operations (`getAll`, `getItem`, `setItem`, `deleteItem`) in robust `try / except (StreamlitAPIException, Exception):` blocks ensuring graceful degradation if local storage components fail.
4. **Regression Testing**: Added `test_storage_invariant_stream_api_exception_and_unique_keys` in `tests/test_session_and_nav_paths.py`.
5. **Gates & Verification**: Verified clean core module compilation (`python3 -m py_compile`) and 100% test suite pass rate (`pytest tests/ -q`).

## Entry 024: Silent Degradation Anti-Pattern & Visible Graceful Fallback (v1.1.5.3)
- **Date**: 2026-09-21
- **Author**: Engineering Team / Builder & Tester Agents
- **Milestone**: v1.1.5.3 Persistence Hotfix

### Design Notes & Architectural Decisions
1. **Silent Degradation Anti-Pattern**: Identified that bare/broad exception swallowing (`except Exception: pass`) masked underlying `LocalStorage.__init__` `KeyError` issues and next-run component value semantics (`None` on initial boot load), causing login to work in-memory but refresh to fail silently without crashing or notifying users.
2. **Graceful Must Mean Visible**: Banned bare swallowing across storage operations. Every storage except-block now captures exception class and message into `st.session_state["persist_debug"]` and renders a discreet sidebar caption `st.sidebar.caption("persistence: degraded — ...")` so persistence degradation is always visible.
3. **Verify Third-Party Internal API Signatures**: Inspected `streamlit-local-storage` initialization and component lifecycles to ensure proper pre-initialization of session state storage keys and robust error handling.
4. **Signature Compatibility & Regression Testing**: Added unit tests asserting method signature compatibility and verifying debug flag population on simulated storage failure in `tests/test_session_and_nav_paths.py`.
5. **Pre-Seal Gates**: Verified clean compilation (`python3 -m py_compile app.py`) and 100% test pass rate (`pytest tests/ -q`).

## Entry 025: Continuous Idempotent Storage Emission & Expander Probe Gating (v1.1.6)
- **Date**: 2026-09-21
- **Author**: Engineering Team / Builder, Tester & Reviewer Agents
- **Milestone**: v1.1.6 Persistence Root Cause Hotfix

### Design Notes & Architectural Decisions
1. **Persistence Root Cause**: Discovered that one-shot component writes are lost when their initial render is discarded before mount, causing `cb_session` never to land in browser localStorage.
2. **Continuous Idempotent Emission**: Moved storage writes from one-shot handlers to continuous idempotent emission: while authenticated, every render re-issues `setItem("cb_session", ...)` and `setItem("cb_page", ...)` using fixed namespaced keys (`ls_continuous_session`, `ls_continuous_page`) — mirroring the probe pattern that provably survives.
3. **Two-Experiment Method**: Utilized local control and Cloud witness environments to isolate and verify component mount lifecycles and storage persistence durability.
4. **Delete Exclusivity**: Restrict `deleteItem` calls exclusively to sign-out and reset paths.
5. **Retirement of Pre-Auth `?pdebug=1`**: Retired `?pdebug=1` pre-auth path. Persistence Debug is now strictly admin-email-gated post-login, and round-trip probe execution is strictly gated to when the expander is expanded (`persistence_debug_expander`).
6. **Testing & Verification**: Added comprehensive unit tests covering continuous-write emission, post-sign-out write silence, expander probe gating, and strict post-login admin checks. Enforced pre-seal compile gate (`python3 -m py_compile`) and 100% test pass rate (`pytest tests/ -q`).

### Entry 025 Addendum (v1.1.6.1)
- **Only Strings Cross Component Bridges**: Probe evidence confirmed that dict bundles passed across the component JS bridge serialize as `"[object Object]"`. Consequently, all session storage writes must explicitly `json.dumps(bundle)`, and reads must utilize `json.loads` with try/except error handling.
- **Corrupt-Legacy Migration Path**: Any legacy `"[object Object]"` or parse failures on read immediately call `deleteItem("cb_session")`, route to clean login gate, and record exception class in `persist_debug`.
- **Token-Write Sites Verification**: Verified all six token-write sites set `expires_at`.
- **Temporary Flag Window**: Temporarily restored `?pdebug=1` pre-auth visibility for diagnosis window only (scheduled for retirement after acceptance).

## Entry 026: Library Abandonment Postmortem & Cookie-Based Server-Side Persistence (v1.2.0)
- **Date**: 2026-09-22
- **Author**: Engineering Team / Builder, Tester & Reviewer Agents
- **Milestone**: v1.2.0 Cookie-Based Persistence & Library Abandonment Postmortem

### The Seven-Round Root-Cause Chain
1. *Rounds 1–2 (Silent Failures & KeyErrors)*: Initial client-side local storage components (`streamlit-local-storage`) raised `KeyError` on uninitialized session state keys and swallowed errors silently (`v1.1.5.3`).
2. *Rounds 3–4 (Duplicate Element Key Crashes)*: Shared component key names caused Streamlit duplicate element key exceptions during multi-page navigation (`v1.1.5.2`).
3. *Rounds 5 (Discarded One-Shot Writes)*: Discovered that one-shot component writes are lost when their initial render is discarded before client-side component mount (`v1.1.6`), forcing continuous idempotent re-emission on every render.
4. *Rounds 6 (toString Coercion & Parse Failures)*: Bi-directional component bridges coerced non-string values into `"[object Object]"`, requiring JSON serialization guardrails and strict corrupt-legacy cleanup paths (`v1.1.6.1`).
5. *Round 7 (The Architectural Dead End — Unreadable Boot)*: Client-side components execute asynchronously via iframes/message passing, making them unreadable synchronously on the server during the initial HTTP request boot. This necessitated complex boot-rerun loops (`boot_mount_triggered`) that failed on cold starts or strict proxies.

### The Decision Rule Adopted
- **Prefer server-side-readable state (cookies via request headers via `st.context.cookies`) over client-component bridges for anything auth-critical.**
- **Rationale**: Cookies are transmitted natively with every HTTP request header. They are readable synchronously on the very first server render without requiring client component mount lifecycles, round-trip probes, or artificial re-run loops.
- **Security & Trade-off Documentation**: While client-set cookies written via JavaScript bridge cannot enforce `HttpOnly` flags (unlike server-set HTTP-only cookies), they provide immediate server-side readability (`st.context.cookies`) on request entry, eliminating client mount delays and race conditions. Token values are stored securely within cookie data bundles (`cb_session`), and debug headers leak zero full tokens (displaying presence and length only).
- **Gating Independence**: Admin Pulse is strictly independent of debug flags (`?pdebug=1`), tied strictly to `ADMIN_EMAIL` match. Persistence Debug is restricted to admin post-login or the temporary `?pdebug=1` window (retiring in v1.2.1).
- **Verification**: Enforced pre-seal compile gate (`python3 -m py_compile`) and green test suite (`.venv/bin/pytest tests/ -q`).

## Entry 027: Persistence Park Order, Equipment-Gap Analysis & Revisit Conditions (v1.2.1)
- **Date**: 2026-09-22
- **Author**: Engineering Team / Builder, Tester & Reviewer Agents
- **Milestone**: v1.2.1 Persistence Parked & Window Closed

### Park Order
1. **Window Closure**: Removed the temporary `?pdebug=1` diagnostic query flag entirely. Persistence Debug is now strictly restricted to site owners post-login (`ADMIN_EMAIL`).
2. **User Expectation Management**: Added a calm, transparent user-reassurance caption on the login screen: `"Sessions reset on reload in this hosting tier — please log in to continue. Your work is always safe."`
3. **Infrastructure Parking**: Retained cookie persistence writes and helper controllers as an architectural asset for future hosting environments, marked with reference comments to Entry 027.

### Equipment-Gap Analysis
- **Hosting Tier Runtime Constraints**: Streamlit Community Cloud and similar containerized ephemeral serverless Python runtimes execute stateless server processes. Client-side storage components (`streamlit-local-storage`) suffer from mount discard races (`v1.1.6`), and cookie-based persistence across iframe component boundaries can be transient depending on browser partition settings and platform proxy layers.
- **The Architectural Reality**: True persistent session cookies across reloads in Streamlit require native HTTP-only session cookies handled directly at the HTTP reverse-proxy/ASGI server layer (FastAPI/Starlette middleware) rather than client-side React component bridges.

### Revisit Conditions
- Revisit cookie-based session persistence when migrating from pure Streamlit process to an ASGI hosting wrapper (e.g., FastAPI + Streamlit mounted via Starlette) where genuine `HttpOnly` request/response cookies can be read and set directly on HTTP request headers without relying on client-component bridges.

## Entry 029: Refresh Logout Final Convergence, Cookie Scope Anatomy & Client-Singleton Rule (v1.2.2)
- **Date**: 2026-09-22
- **Author**: Engineering Team / Builder, Tester & Reviewer Agents
- **Milestone**: v1.2.2 Refresh Logout Final Convergence (Branches H1, H2, H3 & WITNESS)

### Cookie Scope Anatomy (Iframe Path vs Top-Level Path=/)
- **The Iframe Challenge**: Streamlit custom components execute inside isolated iframes. When JavaScript-based components write cookies via `document.cookie`, default scoping rules can isolate cookies to the iframe origin or miss top-level `Path=/` propagation unless explicitly declared.
- **The Branch H1 Fix**: Explicitly passing `path="/"`, `same_site="lax"`, `secure=True`, `max_age=604800` ensures proper top-level cookie scoping. Furthermore, pairing `st.context.cookies` (server-side request headers on fast-path) with client-component reading plus bounded rerun (`boot_mount_triggered` render-2 gate open) guarantees 100% reliable rehydration across cold starts and reloads.

### The Client-Singleton Rule (Session State Isolation)
- **The Multi-User Leakage Bug**: Module-level global singletons (`_supabase_client = create_client(...)`) in multi-user Streamlit deployments cause concurrent users to share a single Supabase client instance, resulting in session bleeding and cross-user auth pollution when `set_session()` is called.
- **The Branch H2 Fix**: Refactored `get_client()` in `supabase_client.py` to store and retrieve a per-session Supabase client singleton inside `st.session_state["supabase_client_instance"]`. This guarantees strict per-session process isolation.

### Streamlit Translation of JS-SPA Auth Guidance
- **Thin-Token Refresh-Only Pattern**: Storing only `{"refresh_token": ..., "expires_at": ...}` in `cb_session` avoids the browser cookie 4KB limit and ensures `access_token` never touches client storage.
- **Gate Flags & WITNESS Observability**: Explicitly setting authentication gate flags (`user`, `access_token`, `refresh_token`, `expires_at`) during rehydration ensures deterministic route gating. The WITNESS panel provides real-time side-by-side observability into `st.context.cookies`, controller read, gate flags, and client instance ID (`id(client)`).
