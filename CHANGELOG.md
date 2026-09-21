# Changelog

All notable changes to the CodeBreaker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.6.1] - 2026-09-21

### Fixed
- Micro-hotfix v1.1.6.1 — Component bridge string serialization, corrupt-legacy cleanup, emission arming & temporary debug flag window:
  - **Component Bridge Serialization**: Only strings round-trip reliably across the component JS bridge; updated continuous session write to use `json.dumps(bundle)` and read side to use `json.loads` with try/except.
  - **Corrupt-Legacy Migration Path**: Strict handling of legacy/corrupt values (`"[object Object]"`, parse failures) → deletes `cb_session` (`deleteItem`), triggers clean login gate, and records exception class into `persist_debug`.
  - **Token-Write Sites & Expiry**: Verified all six token-write sites set `expires_at` in session state; emission guard unchanged.
  - **Persistence Debug Enhancements**: Added `"Emission armed: True/False"` and `"Raw stored head: <first 12 chars or None>"`. Temporarily restored `?pdebug=1` pre-auth visibility for diagnosis window only (to be retired after acceptance).
  - **Testing & Verification**: Added test coverage for string round-trip, corrupt cleanup, guard arming, and debug representation. Enforced compile gate and green pytest suite (`.venv/bin/pytest tests/ -q`).
  - **Documentation**: CHANGELOG v1.1.6.1 and Entry 025 addendum.

## [1.1.6] - 2026-09-21

### Fixed
- Hotfix v1.1.6 — persistence root cause & continuous idempotent emission:
  - **Root Cause & Pattern**: One-shot component writes are lost when their render is discarded before mount, so `cb_session` never lands. Continuous idempotent emission while authenticated re-issues `setItem("cb_session", ...)` and `setItem("cb_page", ...)` on every render — identical to the probe pattern that provably survives.
  - **Delete Exclusivity**: Restricted `deleteItem` calls exclusively to sign-out and reset paths.
  - **Retirement of `?pdebug=1`**: Retired pre-auth `?pdebug=1` query flag path; Persistence Debug is now strictly admin-email-gated post-login, and round-trip probe runs only while the expander is expanded (`persistence_debug_expander`).
  - **Testing & Verification**: Updated unit test suite in `tests/test_session_and_nav_paths.py` (continuous-write emission, no writes after sign-out, probe gating, admin post-login gate). Enforced pre-seal compile gate (`python3 -m py_compile`) and all tests passing green.
  - **Documentation**: CHANGELOG v1.1.6 and DEVLOG Entry 025.

## [1.1.5.4] - 2026-09-21

### Added
- Hotfix v1.1.5.4 — persistent storage boot inspection, bounded-rerun boot sequence & round-trip probe:
  - **Bounded-Rerun Boot Sequence**: Fresh unauthenticated sessions where boot read returns `None` and mount flag is unset trigger `st.rerun()` exactly once (`boot_mount_triggered`). Subsequent renders re-attempt rehydration while unauthenticated.
  - **Admin-Only Persistence Debug Panel**: Added sidebar expander `"Persistence Debug"` visible exclusively to the site owner (`ADMIN_EMAIL`) or pre-auth via query flag `?pdebug=1`. Displays render counter, mount flag state, raw boot-read value (presence/length only, leaking zero tokens), `persist_debug` error status, and a storage round-trip probe (`cb_probe`).
  - **Storage Round-Trip Probe**: Evaluates whether `streamlit-local-storage` round-trips correctly in the runtime environment by setting `cb_probe="1"` on every render and reporting the retrieved value on the subsequent render.
  - **Testing & Verification**: Added comprehensive test coverage in `tests/test_session_and_nav_paths.py` verifying rerun bounds, rehydration, probe mechanics, and admin-gating. Enforced pre-seal compile gate (`python3 -m py_compile app.py`) and all tests passing green.
  - **Documentation**: CHANGELOG v1.1.5.4 and DEVLOG Entry 024 addendum.

## [1.1.5.3] - 2026-09-21

### Fixed
- Hotfix v1.1.5.3 — persistence silent failure & visible degradation anti-pattern:
  - **Root Cause Resolution**: Addressed silent persistence failure where `LocalStorage.__init__` raised unhandled `KeyError` on missing session state keys and next-run component value semantics returned `None` on initial boot rehydration.
  - **End Silence / Visible Degradation**: Eliminated bare swallowing of storage exceptions; every storage try/except block now records exception class and message into `st.session_state["persist_debug"]` and renders a discreet sidebar `st.sidebar.caption("persistence: degraded — ")`.
  - **Robust Initialization**: Pre-initialized session state container for storage and wrapped initialization safely.
  - **Testing**: Added signature-compatibility and debug-flag regression tests in `tests/test_session_and_nav_paths.py`.
  - **Verification**: Enforced pre-seal compile gate and all tests passing green.

## [1.1.5.2] - 2026-09-21

### Fixed
- Hotfix v1.1.5.2 for `streamlit-local-storage` duplicate element key crash & syntax indentation error:
  - **Indentation Repair**: Repaired syntax IndentationError around line 125 in `app.py`.
  - **LocalStorage Unique Key Namespacing**: Assigned unique explicit `key=` attributes (`ls_refresh_set`, `ls_oauth_set`, `ls_signout_del_sess`, `ls_signout_del_page`, `ls_page_set`, `ls_reset_del_sess`, `ls_reset_del_page`, `ls_signup_set`, `ls_login_set`) to every `streamlit-local-storage` `setItem` and `deleteItem` call site.
  - **Graceful Exception Wrapping**: Wrapped all local storage operations (`getAll`, `getItem`, `setItem`, `deleteItem`) in `try / except (StreamlitAPIException, Exception):` blocks preventing unhandled exceptions and component crashes.
  - **Regression Testing**: Added regression test `test_storage_invariant_stream_api_exception_and_unique_keys` in `tests/test_session_and_nav_paths.py`.
  - **Documentation**: CHANGELOG v1.1.5.2 and DEVLOG Entry 023.

## [1.1.5.1] - 2026-09-20

### Fixed
- Hotfix for production login `StreamlitDuplicateElementKey` outage (v1.1.5.1):
  - **Explicit Widget Key Namespacing**: Assigned unique, explicit `key=` attributes to all form inputs across login, signup, and recovery/password-reset forms (`signup_email`, `signup_pw`, `signup_display_name`, `signup_submit_btn`, `login_email`, `login_pw`, `login_submit_btn`, `forgot_submit_btn`, `reset_pw_new`, `reset_pw_confirm`, `reset_submit_btn`).
  - **Exception Isolation**: Updated auth exception handlers to re-raise `StreamlitAPIException` / duplicate key errors instead of masking framework errors as auth failures.
  - **Unit Testing**: Added `tests/test_auth_widget_keys.py` enforcing key uniqueness and exception non-masking.
  - **Documentation**: CHANGELOG v1.1.5.1 and DEVLOG Entry 022.

## [1.1.5] - 2026-09-20

### Added
- Session Persistence & Navigation State (v1.1.5):
  - **LocalStorage Session Bundle**: Both login doors and sign-up write the `cb_session` bundle (`access_token`, `refresh_token`, `expires_at`) to browser localStorage via `streamlit-local-storage`.
  - **Boot Rehydration & Expiry Management**: Automatic session rehydration on app boot via `client.auth.set_session` and `client.auth.refresh_session`, with strict failure handling (deleting invalid/corrupt/expired keys and gating unauthenticated views).
  - **Sign-Out Cleanup**: Sidebar Sign Out explicitly deletes `cb_session` and `cb_page` from localStorage and clears session state.
  - **Navigation Persistence**: Sidebar active page persisted in localStorage as `cb_page` and restored automatically after browser refresh.
  - **Zero-Network Unit Tests**: Added unit tests in `tests/test_session_and_nav_paths.py` covering valid restore, expired session refresh, corrupt session handling, sign-out deletion, and navigation persistence.
  - **Indentation Repair**: Fixed syntax indentation error around line 547 in `app.py`.
  - **Documentation**: CHANGELOG v1.1.5 and DEVLOG Entry 021.

## [1.1.4] - 2026-09-19

### Added
- Email saga closure batch (v1.1.4):
  - **Token Handling**: Enhanced `verify_otp` parameter parsing (`?type+token`) with robust fallback chain (`token_hash=` -> sha256-hex of token as `token_hash` -> `token=`). Success + signup renders dedicated `"Email confirmed ✅ — please log in"` screen and login gate; success + recovery initiates password reset; expired/invalid links trigger warnings with resend/forgot paths; query parameters strictly cleared.
  - **Duplicate Signup UX & Enumeration Trade-Off**: When `sign_up` returns empty identities (`identities=[]`), displays `st.warning("This email is already linked to an account. Please log in or reset your password.")` and sends nothing. Documented the enumeration trade-off as a founder decision in DEVLOG.
  - **Forgot-Password Form Integration**: Integrated forgot-password inside the login form as a second `form_submit_button` under Log In, reusing the Email field value; external button and collapsible form removed.
  - **Tour Persistence**: On dismiss, calls `supabase.auth.update_user(data={"tour_seen": True})`. Tour displays only when `user_metadata` lacks `tour_seen`; session-only flag removed.
  - **Admin Pulse RPC Refactor**: Replaced direct table select counts with `rpc("count_registered_users")` and `rpc("count_engineering_logs")` leveraging server-side security definer functions with graceful error handling.
  - **UI Refinement**: Removed Display Name placeholder entirely (empty string).
  - **Audit & Security**: Asserted zero user-facing `supabase.co` redirects or links anywhere (OAuth authorize hop excluded, documented).
  - **Zero-Network Tests & Compile Gate**: Added comprehensive unit tests in `tests/test_email_saga_closure.py` covering all six behaviors; enforced pre-seal compile check (`python3 -m py_compile`).
  - **Documentation**: CHANGELOG v1.1.4 and DEVLOG Entry 020.

## [1.1.2] - 2026-09-18

### Added
- Email link ownership & identity family: emails point directly at the app domain with server-side `verify_otp` (no Supabase intermediate hop, no `ref` parameter in email links).
- Robust `verify_otp` handling for signup and recovery links with token parameter parsing and automatic fallback from `token_hash=` to `token=` per installed `supabase-py` API.
- Clear success feedback (`"Email confirmed — please log in."` for signup; recovery session setup for password reset) and expired/invalid link warnings with one-click resend/forgot paths.
- Deleted old PKCE/code-exchange recovery detection from v1.1.0 while maintaining redirect-origin hygiene.
- Comprehensive zero-network unit tests (`tests/test_auth_confirmation.py`) covering verify_otp success, recovery session establishment, token_hash fallback, expired/invalid link handling, and query param cleanup.
- DEVLOG Entry 019 documenting email link ownership architecture.

## [1.1.0] - 2026-09-18

### Added
- Complete password reset flow: added "Forgot password?" button under Log In on the Login page with email format validation (`validate_email`) and `supabase.auth.reset_password_for_email`.
- Account enumeration protection: strictly suppresses all backend exceptions and displays exact enumeration-safe info message `"If an account exists for that email, a reset link is on its way."`.
- Recovery return handling: detects recovery sessions (`type=recovery` query parameter handling on page load), exchanges code, and renders a secure "Set new password" form.
- Password policy reuse: enforces the exact `security.py` 8-character password policy (at least 8 chars with 1 letter and 1 number) on new password updates (`supabase.auth.update_user`), followed by automatic sign-out and fresh login prompt.
- Comprehensive unit tests (`tests/test_security.py`) covering forgot-password wording, enumeration safety, recovery session detection, and password policy reuse.
- DEVLOG Entry 017 documenting auth family completion (signup → confirm → login → reset).

## [1.0.6] - 2026-09-18

### Added
- Live-ticking cooldown countdown UX: replaced the stuck-disabled cooldown state with a dynamic countdown loop (`time.sleep(1); st.rerun()`) while cooldown is active, visibly ticking down every second and instantly re-enabling the Sign Up button at 0 without requiring manual mode-toggling.
- Bounded cooldown rerun loop strictly tied to the stored session timestamp (`signup_cooldown_until`) preventing infinite loops.
- Server-side cooldown submission guard blocking signup attempts during active cooldown periods.
- Comprehensive unit tests (`tests/test_security.py`) verifying countdown remaining seconds, cooldown expiry re-enabling, and server-side submission blocking.
- DEVLOG Entry 016 documenting the cooldown UX challenge (Streamlit rendering model requiring explicit reruns for real-time timers).

## [1.0.5] - 2026-09-17

### Added
- Auth input form refinement: removed `max_chars`, placeholder text, and password helper captions from authentication inputs for a cleaner UI experience.
- Onboarding tour polish: updated tour body to a clean vertical numbered 3-step list (`1. Analyze`, `2. Blueprint`, `3. Engineering Log`) via `st.markdown`, retaining `"Got it"` button and once-per-session dismissal logic.
- Login validation update: per-field empty and format validation messages with combined error string deleted.
- Pre-seal compile verification gate (`python -m py_compile`) and test suite updates covering tour markdown content.
- DEVLOG Entry 015 documenting v1.0.5 release refinements.

## [1.0.4] - 2026-09-17

### Added
- Password strength enforcement at signup (minimum 8 characters with at least one letter and one number), live `st.caption` guidance, and sanitized rejection messages (preventing rule-by-rule leakage).
- Enhanced signup validation UX addendum enforcing pre-Supabase per-field empty checks (email empty → `"Email cannot be empty."`, password empty → `"Password cannot be empty."`, both empty → email message first), app-side regex email format validation (`^[^@\s]+@[^@\s]+\.[^@\s]+$`), and verbatim 8-character password rule enforcement (`"Password must be at least 8 characters with at least one letter and one number."`), preventing raw platform error leakage.
- Server-side input length caps enforced in handlers and UI inputs (`max_chars`): email ≤254, password ≤128, display name ≤80, project idea/problem ≤2000, and each engineering log field ≤5000 characters, returning generic sanitized errors on overlong input.
- Signup cooldown mechanism disabling the signup button for 30 seconds via `st.session_state` timestamp after a failed signup attempt, with code comments noting server-side rate limits remain Supabase's job (platform layer already enforced).
- Comprehensive unit test suite (`tests/test_security.py`) verifying weak-password rejection, input length caps with mocked Supabase, and cooldown session state logic (all 36 tests passing).
- DEVLOG Entry 013 documenting the Abuse Guards family (defense in depth — Supabase platform limits + app caps + UX cooldown) and the application of the Category Batching Rule to the security family.

## [1.0.3] - 2026-09-17

### Added
- Dismissible 3-step Onboarding Tour ("Analyze", "Blueprint", "Engineering Log") shown on first login of a session via `st.expander` and storing `tour_dismissed` flag in `st.session_state` (never blocking the auth gate).
- New About page (`About`) featuring mission statement ("Plan before you code"), classroom lecturer usage (`Assignment Grade = System Blueprint + Engineering Log`), the two auth doors (Email/Password + GitHub OAuth), the four export formats (Markdown, Plain Text, HTML, PDF), public repository link, and version footer ("v1.0.3").
- Comprehensive unit tests (`tests/test_onboarding_and_about.py`) verifying tour rendering once per session, click-to-dismiss state updates, and About page content validation with zero network usage.
- DEVLOG Entry 012 documenting the Category Batching Rule credited to the founder, using the v0.4.1/v1.0.2 export format split as the definitive case study.

## [1.0.2] - 2026-09-17

### Added
- PDF Export (.pdf) on the Blueprint page supporting professional architecture document rendering (`render_blueprint_pdf`) via pure-python library `fpdf2`.
- Title header (project name + tagline), summary, tech stack bullets, folder tree in a monospace block, edge cases, numbered roadmap, and dynamic footer `"Generated by CodeBreaker v1.0.2 + date"`.
- In-memory BytesIO generation with zero temp files on disk and reused filename sanitization (`sanitize_filename`).
- Added `fpdf2` to `requirements.txt`.
- Comprehensive unit tests (`tests/test_ai_engine.py`) verifying PDF bytes start with `b"%PDF"`, >1KB size, safe None value handling, and zero secret presence.

## [1.0.1] - 2026-09-16

### Added
- Admin Pulse feature in the sidebar showing total registered users count and total engineering log entries count, visible exclusively to the designated owner (`ADMIN_EMAIL`).
- Secure config loader integration for `ADMIN_EMAIL` supporting `os.environ` with fallback to `st.secrets`.
- Efficient Supabase counting using `select("id", count="exact")`.
- Local `.env` and `.env.example` configuration entries for `ADMIN_EMAIL`.
- Comprehensive unit tests (`tests/test_admin_pulse.py`) verifying admin sees counts and non-admin sees nothing, with zero network calls.

## [1.0.0] - 2026-09-15

### Added
- Email Confirmation flow: Supabase handles delivery (`auth.sign_up`), while the application manages UX states (`st.info("Check your email to confirm your account")`, blocking login gate for unconfirmed users).
- "Resend confirmation email" button on the Login page (visible when an unconfirmed user exists), calling `supabase.auth.resend({"type": "signup", "email": email})` with future rate-limit note.
- Success confirmation notice ("Confirmation email sent to {email}. Check your inbox (and spam folder).") upon signup.
- Comprehensive unit tests (`tests/test_auth_confirmation.py`) with mocked Supabase covering unconfirmed user blocking, resend call, and confirmed user success.
- Production safety: Dev convenience flags removed in favor of strict email confirmation validation.

## [0.5.0] - 2026-09-15

### Added
- Unified config loader (`config.py`) implementing a robust two-tier resolution order: `os.environ` first, falling back to Streamlit `st.secrets` (with runtime and exception guards for Streamlit Community Cloud).
- Integrated config loader across `supabase_client.py` and `ai_engine.py` for seamless environment and cloud secret retrieval.
- Comprehensive unit test suite (`tests/test_config.py`) verifying environment precedence, `st.secrets` fallback, required config validation, and zero network calls.
- Verified `requirements.txt` containing `streamlit`, `requests`, `supabase`, `markdown`, and `pytest`.
- "Deploy on Streamlit Community Cloud" section in `README.md` listing required secret names (`GROQ_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`) and step-by-step deployment instructions.
- Full pre-deploy security audit confirming zero secret patterns (`gsk_`, `eyJ`, `password=`), clean documentation, and intact RLS reliance.
- CHANGELOG v0.5.0 and DEVLOG Entry 007 documenting deployment architecture and design decisions.

## [0.4.1] - 2026-09-15

### Added
- Multi-format export selector on the Blueprint page supporting Markdown (.md), Plain text (.txt), and HTML (.html).
- Self-contained styled HTML export using the `markdown` package (`render_blueprint_html`), including title and "Generated by CodeBreaker v0.4.1" footer.
- Plain text export (`render_blueprint_text`) capturing all blueprint sections and footer.
- `st.info` guidance box ("What do I do with this file?") above export controls explaining GitHub repo drops, AI assistant specs, and file format usage.
- Extended renderer tests in `tests/test_ai_engine.py` covering text sections, HTML headings and valid wrappers, and zero-secret safety across all formats.

## [0.4.0] - 2026-09-14

### Added
- Blueprint Export feature (`st.download_button`) on the Blueprint page rendering clean Markdown (title, summary, tech stack bullets, fenced folder tree, edge cases, numbered roadmap, and footer "Generated by CodeBreaker v0.4 + date").
- Robust filename sanitization (`sanitize_filename`) stripping path separators, risky characters, and special symbols.
- Engineering Log Polish: styled expanders with date badges and per-entry delete button enforcing ownership (`user_id` + RLS).
- Comprehensive unit tests (`tests/test_ai_engine.py`) for Markdown rendering and filename sanitization.

### Fixed
- Fixed the literal `<br>` artifact on the Login page by replacing it with proper Markdown spacing.

## [0.3.1] - 2026-09-14

### Added
- GitHub OAuth authentication integration ("Continue with GitHub" button on Login page calling `sign_in_with_oauth` with dynamic app URL `redirect_to` and rendering `st.link_button`).
- Automatic PKCE authorization code exchange on page load (`exchange_code_for_session`), secure session storage in `st.session_state`, and query parameter cleanup.
- Unit tests (`tests/test_oauth.py`) covering OAuth sign-in and PKCE code exchange with zero network calls and query-param cleanup assertion.

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
