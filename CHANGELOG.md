# Changelog

All notable changes to the CodeBreaker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.spec/spec/v2.0.0.html).

## [1.7.4] - 2026-10-09

### Added / Changed
- MICRO-MISSION v1.7.4 — Relocate Log Out to kill sidebar auto-open trigger:
  - **Sidebar Log Out Deletion**: Deleted the Log Out button and sign-out handler from the sidebar entirely, turning the sidebar into a pure navigation-only component (`Section` radio).
  - **Account Card Log Out Relocation**: Added a full-width `"Log Out"` button (`type="secondary"`, `use_container_width=True`) inside the Account card on Home, directly below the Member Since line, executing the identical sign-out sequence (Supabase sign-out, session/token cleanup, param removal, redirect, rerun).
  - **Auto-Open Root Cause & Residual Law**: Identified sidebar interaction as the trigger for client-persisted sidebar auto-open. Documented in DEVLOG Entry 050 that `initial_sidebar_state` applies only on fresh loads, logout from sidebar was the trigger, and a manually-opened sidebar survives logout→login via client memory (requiring manual close or page reload to reset).
  - **Testing & Documentation**: Enforced compile gate (`py_compile`), source-scan assertions, unit tests (`tests/test_v1_7_4.py`), and verified green test suite. CHANGELOG v1.7.4 and DEVLOG Entry 050.

## [1.7.3] - 2026-10-09

### Added / Changed
- MICRO-MISSION v1.7.3 — Provider-diversity rule, library copy rename, sidebar auto-open verdict:
  - **Provider-Diversity Rule**: Inserted verbatim provider-diversity guidelines into `ai_engine.py` generation and extend prompts requiring explicit cost, privacy, offline, and latency evaluation before defaulting to OpenAI GPT-4o.
  - **Blueprint Library Copy Rename**: Renamed button label from `"← Back to All Blueprints"` to `"← Blueprint Library"`.
  - **Sidebar Auto-Open Platform Verdict**: Investigated and confirmed branch (b) platform-side — Streamlit mobile persists sidebar open/close state in client storage until site data is cleared or incognito is used. Documented reset note in DEVLOG.
  - **Testing & Documentation**: Enforced compile gate (`py_compile`), source-scan assertions, unit tests (`tests/test_v1_7_3.py`), and verified green test suite. CHANGELOG v1.7.3 and DEVLOG Entry 048.

## [1.7.2] - 2026-10-09

### Added / Changed
- MICRO-MISSION v1.7.2 — Red library Confirm, two-tone cross-links, witness retirement:
  - **Red Library Confirm Unification**: Standardized Blueprint library items to render via `st.expander` (matching Engineering Log), enabling the exact shared CSS selector `div[data-testid="stExpander"] div.stButton > button[kind="primary"]` so both render red (`#d33`).
  - **Two-Tone Cross-Links & Boot Mode Handler**: Deleted full-blue tertiary buttons; rendered bottom-centered markdown links (`"Don't have an account? <a href=\"?mode=signup\">Sign up</a>"` / `"Already have an account? <a href=\"?mode=login\">Log in</a>"`), inheriting theme primary blue without inline color override. Added boot query-param mode handler (`st.query_params.get("mode") in ("signup", "login")`).
  - **Witness Retirement**: Permanently retired LIBRARY-WITNESS traceback rendering, restoring library except branch to `st.info("Library unavailable.")`.
  - **Testing & Documentation**: Enforced compile gate (`py_compile`), source-scan and unit tests (`tests/test_v1_7_2.py`), and verified green test suite (`193 passed`). CHANGELOG v1.7.2 and DEVLOG Entry 047.

## [1.7.1] - 2026-10-09

### Added / Changed
- MICRO-MISSION v1.7.1 — Library red confirm, cross-links restyle, ai_engine reload cure:
  - **Library Confirm Red**: Applied the identical CSS mechanism used on Engineering Log (`div[data-testid="stContainer"] div.stButton > button[kind="primary"]`) to the Blueprint library Confirm button so both render red (`#d33`).
  - **Auth Cross-Links Restyle**: Removed boxed switch buttons under Log In/Create Account rows; rendered each switch at the bottom of the auth view, centered via `st.columns([0.25, 0.5, 0.25])` with middle column holding `st.button(..., type="tertiary", use_container_width=True, key=...)`. Injected CSS targeting tertiary buttons (`color: #1a73e8; font-weight: 600; font-size: 1.05em;`). Handlers preserve `nav_pending` + `st.rerun()`.
  - **Module-Cache Cure (`ai_engine` Hot-Reload & Rebind)**: Inserted mtime-based reload block immediately after `ai_engine` import in `app.py` (`_importlib.reload(ai_engine)` and rebinding loop over imported names into `globals()`), curing module staleness across edits without requiring manual server reboots (while Reboot remains the reliable backup).
  - **Testing & Documentation**: Enforced compile gate (`py_compile`), source-scan and unit tests (`tests/test_v1_7_1.py`), and verified green test suite (`191 passed`). CHANGELOG v1.7.1 and DEVLOG Entry 046.

## [1.7.0] - 2026-10-09

### Added / Changed
- MICRO-MISSION v1.7.0 — Confirm unification, DD-MM-YYYY display law, auth UX cross-links & sidebar rename:
  - **Confirm Unification & Caption Elimination**: Standardized Blueprint library and Engineering Log confirms to share the identical red confirm mechanism (`type="primary"`, side-by-side equal columns via `st.columns(2)`, `use_container_width=True`) and removed every instance of the `"Confirming will permanently delete this item."` caption from both surfaces.
  - **DD-MM-YYYY Display Law**: Added `fmt_date(d)` helper in `app.py` parsing ISO timestamps into Africa/Lagos calendar dates formatted as `"DD-MM-YYYY"`. Applied uniformly across library date chips, Home recent chips, log `[date]` prefixes, and expander Timestamp lines (retaining `HH:MM:SS`). DB storage remains ISO forever (`created_at`). PDF footer renders `DD-MM-YYYY` via `strftime("%d-%m-%Y")`. `build_pdf_lines` emits subtitle `"CodeBreaker System Architecture Blueprint"` (italic 9) and footer per `docs/pdf_chrome_spec.md`.
  - **Auth UX & Sidebar Rename**: Added bottom-centered cross-links `"Don't have an account? Sign up"` on login view and `"Already have an account? Log in"` on create-account view. Renamed sidebar `"Sign Out"` to `"Log Out"`. Set `initial_sidebar_state="collapsed"` in `st.set_page_config`. Both auth paths execute all session work before first render (render-after-work).
  - **Accepted Platform Artifacts & Verification**: Accepted platform repaint and mobile sidebar overlay behaviors; enforced `py_compile`, source-scan rules, quoted-lines report rule, and verified green pytest suite.

## [1.6.9] - 2026-10-09

### Added / Changed
- MICRO-MISSION v1.6.9 — Platform-honest confirm styling + footer chrome per spec:
  - **Platform-Honest Confirm Styling**: Removed unsupported `color=` keyword from `st.button` calls (Streamlit 1.65 platform limit: colored buttons rejected; true red buttons deferred to hosting migration's custom frontend). Confirm buttons set to `type="primary"` with explicit warning markdown `st.markdown('<span style="color:#c0392b; font-size:0.85em">Confirming will permanently delete this item.</span>', unsafe_allow_html=True)` rendered directly above each Confirm button. Cancel stays neutral; Log In stays blue primary.
  - **PDF Chrome & Spec Doctrine**: Created `docs/pdf_chrome_spec.md` establishing the spec-file doctrine (future missions cite the spec file, never re-describe the look). Implemented folder-structure Courier 9 branch, exact footer block with `set_auto_page_break(auto=False)` before `set_y`, and strict ISO-to-DD-MM-YYYY footer date normalization (`strftime("%d-%m-%Y")`).
  - **Testing & Documentation**: Enforced compile gate (`py_compile`), source-scan assertions, unit test suite (`tests/test_v1_6_9.py`), and verified green test suite. CHANGELOG v1.6.9.

## [1.6.8] - 2026-10-08

### Added / Changed
- MICRO-MISSION v1.6.8 — Verbatim law (red Confirm, footer chrome, login flash):
  - **Verbatim Red Confirm & Footer Chrome**: Adopted exact button pattern (`ca, cb = st.columns(2)` with `color="red"` on Confirm and `disarm(row_id)` on Cancel) for Blueprint library and Engineering Log entry delete; implemented exact PDF footer chrome (`pdf.set_y(pdf.get_page_height() - 15)`, italic 8 footer string, and `CodeBreaker System Architecture Blueprint` title/subtitle handling) and clean `build_pdf_lines`.
  - **Landing CTAs & Auth Flow**: Landing CTAs updated to `cta_login` and `cta_signup` setting `nav_pending = "Auth"` and calling `st.rerun()`.
  - **Testing & Documentation**: Enforced compile gate (`py_compile`), source-scan and unit tests (`tests/test_v1_6_8.py`), and verified green test suite (`182 tests passed`). CHANGELOG v1.6.8.

## [1.6.7] - 2026-10-08

### Added / Changed
- MICRO-MISSION v1.6.7 — Red Confirm, login flash minimization, footer chrome final:
  - **Red Confirm Law**: Every delete-confirm button (Blueprint library armed rows AND Engineering Log armed entries) renders with `st.button(..., color="red")` (Streamlit 1.65 color param support) with a keyed CSS injection fallback guarding against `TypeError` — ensuring destructive confirms are never rendered in blue primary.
  - **Login Flash Minimization & Render-After-Work Pattern**: In the unauthenticated / auth branch (`if not user:`), all Supabase and session work (`rt` verification, client initialization, OTP verification, OAuth code exchange) executes completely BEFORE any UI rendering call. Flash messages and warnings are stored in session state and rendered once at the end of the branch when the auth card / landing view paints in a single atomic swap.
  - **Footer Chrome Final**: Footer string exactly `"Generated by CodeBreaker Workspace + <export_date>"` (proper spacing, no glue) rendered italic 8 via `pdf.set_y(pdf.get_page_height() - 15)` on the last page only; `build_pdf_lines` remains strictly free of footer text; page-1 title bold 16 + italic 9 subtitle retained.
  - **Testing & Documentation**: Enforced pre-seal compile gate (`py_compile`), comprehensive test suite (`tests/test_v1_6_7.py`), and verified green test suite (`178 tests passed`). CHANGELOG v1.6.7 and DEVLOG Entry 044.

## [1.6.6] - 2026-10-08

### Added / Changed
- MICRO-MISSION v1.6.6 — Consolidated residuals closure (PDF Courier tree + italic footer chrome + heading count removal + login flash + radio label + arm/cancel final layout + N/A law):
  - **N/A Law Enforcement**: Enforced rigorous `"N/A"` fallback across all empty slots (log fields, export Project Context, etc.), banning `"Null"` or blank fallbacks, validated by source-scan test asserting zero `"Null"` fallback literals exist in `app.py` or `ai_engine.py`.
  - **Stacked Full-Width & Two-Row Layout Rule**: Blueprint library armed row renders two stacked rows — row1 `[Open][Extend]`, row2 `[Confirm][Cancel]` (labels exactly `"Confirm"` and `"Cancel"`, zero ellipsis, `use_container_width=True`). Engineering Log armed entry renders `[Confirm]` then `[Cancel]` as two stacked full-width buttons in a single column (`use_container_width=True`), with un-armed showing one full-width `[Delete]`.
  - **Arm Expiry & Self-Disarm**: Per-row arm timestamps stored in `session_state`, with automatic expiry clearing stale arms older than 10 seconds on render.
  - **PDF Courier Tree & Footer Chrome**: `build_pdf_lines` free of footer string; PDF title and subtitle on page 1; footer rendered once via `pdf.set_y(pdf.get_page_height() - 15)` on last page; Courier font applied to folder structure lines.
  - **Login Flash & Rerun Finalization**: Landing `[Log In]` and `[Create Account]` handlers set `nav_pending` and call `st.rerun()` as the final statement of the branch.
  - **Roadmap Heading**: Exactly `"Implementation Roadmap"` everywhere, deleting any `(N Steps)` count suffix.
  - **Testing & Documentation**: Enforced pre-seal compile gate (`py_compile`), comprehensive test suites including new `tests/test_v1_6_6.py`, and verified green test suite (`173 tests passed`). CHANGELOG v1.6.6 and DEVLOG Entry 043.

## [1.6.5] - 2026-10-08

### Added / Changed
- MICRO-MISSION v1.6.5 — PDF tree monospace + real footer + heading count removal + version dedupe + delete arm/cancel + login flash + sidebar label cleanup:
  - **Builder PDF Tree Monospace**: Inside `render_blueprint_pdf`, lines belonging to the Folder Structure section (between `"## Folder Structure"` and the next `"## "` header) render with `pdf.set_font("Courier", "", 9)` so indentation aligns in fixed columns; all other lines stay Helvetica; Helvetica restored after section.
  - **Builder PDF Chrome & Footer**: `build_pdf_lines` no longer appends the footer line; page 1 renders title `# ` as bold 16 and adds an italic 9 subtitle line `"CodeBreaker System Architecture Blueprint"` beneath it; after content loop, on the last page calls `pdf.set_y(pdf.get_page_height() - 15)` and renders italic 8 `"Generated by CodeBreaker Workspace + <date>"` once. Added `pdf.get_page_height = lambda: pdf.h` compatibility helper.
  - **Roadmap Heading Count Removal**: Deleted `"(N Steps)"` suffix everywhere (in-app heading, Markdown export). Heading is now exactly `"Implementation Roadmap"`.
  - **Version Deduplication**: Render-time regex strips trailing `" — vN"` and `"(vN)"` from stored titles (Home list, library rows, blueprint header), showing version only as `"(vN)"` when version > 1. Extend stores base title + version = parent + 1.
  - **Delete Arm/Cancel Expiry**: First Delete arms row (`[Confirm delete]` + `[Cancel]`); Cancel disarms; 10-second auto-expiry clearing timestamp on rerun for both blueprints and engineering log entries. Un-armed rows show plain `[Delete]`.
  - **Login Flash & Immediate Rerun**: Landing CTAs (`[Log In]`, `[Create Account]`) set `nav_pending` and `st.rerun()` immediately.
  - **Sidebar Radio Label Cleanup**: Non-empty label (`label="Section"`) with `label_visibility="collapsed"` and zero `index=` argument, making `session_state` the sole driver and eliminating both Streamlit log warning floods.
  - **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`), comprehensive test suites including new `tests/test_v1_6_5.py`, and verified green test suite (`164 tests passed`). CHANGELOG v1.6.5 and DEVLOG Entry 042.

## [1.6.4-hotfix] - 2026-10-06

### Added / Changed
- **Verbatim Renderer Replacement (v1.6.4-hotfix)**: Replaced `sanitize_pdf_text`, `build_pdf_lines`, and `render_blueprint_pdf` in `ai_engine.py` with exact verbatim code implementation. Verified `.venv` compilation, updated test suites, and verified 159 tests passing green.

## [1.6.4] - 2026-10-06

### Added / Changed
- MICRO-MISSION v1.6.4 — Single PDF Renderer, Version-Tag Dedupe, Delete Arm/Cancel, Copy + Nav Flash Fixes:
  - **Single-Renderer Law**: Enforced single PDF generation function (`render_blueprint_pdf`) utilizing `build_pdf_lines` and `multi_cell` (zero `.cell(` calls in renderer). Deleted duplicate FPDF/render implementations and preserved non-ASCII error guard.
  - **Version-Tag Deduplication**: Stopped appending `"— v2"` to stored blueprint titles on extend. Stored titles save base name, and render-time regex `r"\s*—\s*v\d+$"` strips any existing trailing `— vN` from legacy rows while displaying clean `(vN)` badges exclusively for version > 1.
  - **Delete Arm/Cancel Pattern**: First Delete press arms the row exclusively; armed row renders `[Confirm delete]` + `[Cancel]`. Cancel disarms, and arm state auto-expires after 10 seconds via timestamp verification on every rerun. Un-armed rows show plain `[Delete]`.
  - **Roadmap Display & Keycap Stripping**: Roadmap headings now dynamically report actual step count (`({len} Steps)`). Strip keycap glyphs (U+20E3, U+FE0F) and leading number prefixes at render time in-app and across all export formats, numbering each step exactly once.
  - **Login Flash & Immediate Rerun**: Landing CTA handlers (`[Log In]`, `[Create Account]`) set `nav_pending` and call `st.rerun()` immediately.
  - **Testing & Documentation**: Enforced pre-seal compile gate (`py_compile`), source-scan test asserting single fpdf function and zero `.cell(` calls, unit tests (`tests/test_v1_6_4.py`), and verified green test suite (`159 passed`). CHANGELOG v1.6.4 and DEVLOG Entry 042.

## [1.6.3] - 2026-10-06

### Added / Changed
- MICRO-MISSION v1.6.3 — nav pending-flag fix + AI key presence diagnostic:
  - **Nav Pending-Flag Pattern**: Removed EVERY post-instantiation assignment to `st.session_state["nav_radio"]` (lines ~1301/1306/1311 and others). Replaced with `st.session_state["nav_pending"] = ...` followed by `st.rerun()`. At the top of the script before sidebar radio instantiation, `nav_pending` is popped into `nav_radio` and mirrored into `pg` query param, eliminating Streamlit API state mutation exceptions.
  - **AI Key Presence Diagnostic**: Added admin-only diagnostic inside Persistence Debug panel listing which provider and system keys (`GROQ_API_KEY`, `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`) are PRESENT or MISSING (names and presence only, never values).
  - **Testing & Documentation**: Enforced pre-seal compile gate (`py_compile`), source-scan test asserting zero post-instantiation `nav_radio` assignments and top-level `nav_pending` handling, comprehensive unit tests (`tests/test_v1_6_3.py`), and verified green test suite (`.venv/bin/pytest`). CHANGELOG v1.6.3.

## [1.6.2] - 2026-10-05

### Added / Changed
- Mission v1.6.2 — PDF Renderer Rewrite, Extend Provider Unification, Nav Single-Source, Context N/A, Home Count Removal, Log N/A + Optional Title:
  - **PDF Renderer Rewrite**: Exposed `sanitize_pdf_text(s)` with codepoint mapping and fallback (`ord > 255` → `-`). Exposed `build_pdf_lines(bp)` returning full document lines. PDF renderer strictly uses `pdf.multi_cell(0, 5.5, line)` per line with `get_y()` page-break checks and `set_font(style="B")` for headers (zero cell/write calls for dynamic content).
  - **Extend Provider Unification**: Unified AI provider calls between `generate_blueprint` and `extend_blueprint` via shared `_call_ai` helper using exact same model constants, retry chain, and named provider error reporting.
  - **Project Context N/A & Home Count Removal**: Missing/empty context fields render `"N/A"` (legacy sentences deleted). Removed "Saved Blueprints" count metric from Home dashboard.
  - **Navigation Single Source**: Synchronized navigation via `nav_radio` session state key and `pg` query param across all navigation triggers (sidebar radio, Home open, view all blueprints, Quick Start buttons, About contact), ensuring second blueprint opens reliably every time.
  - **Log N/A & Optional Milestone Title**: Milestone title is now optional (`"Milestone Title (optional)"`, no validation error when blank, defaulting to progress excerpt or `"N/A"`). Empty progress/bugs/learnings store as `"N/A"`, and expanders always list all three fields. Quick Start button renamed to `"Eng. Log"`.
  - **Testing & Documentation**: Enforced pre-seal compile gate (`py_compile`), comprehensive test suite (`tests/test_v1_6_1.py`), and verified green test suite (`149 passed`). CHANGELOG v1.6.2 and DEVLOG Entry 041.

## [1.6.1] - 2026-10-05

### Added / Changed
- Mission v1.6.1 — Responsive Layout, Extend Fix, Export Shape+Context, Library Placement, Home Linking, PDF+TXT Fixes, Roadmap Scaling:
  - **Extend Blueprint Signature & Flow**: Defined `extend_blueprint(old_json, new_requirements, notes)` in `ai_engine.py` with schema preservation and context carry-over. Wired Submit Extension in `app.py` to save new versioned row (`v<N+1>`) and open it.
  - **Export Shape & Project Context**: Export rows structured as 2 columns (`[0.82, 0.18]`) with full-width download button in col1 and single small `:material/info:` popover in col2. Stored `project_name`, `project_description`, and `target_audience` in `blueprint_json` at generation and extend. All exports begin with a Project Context block (Name / Description / Target Audience) with legacy fallback handling.
  - **Library Placement & Home Linking**: Removed "Blueprint Library" from sidebar. Rendered full list in Blueprint page main area (`[Open]`, `[Extend]`, `[Delete(confirm)]`, full-width on mobile). Home `[Open]` sets DB pointer + session state + `pg=Blueprint` + rerun (overwriting previous pointer). `[View all blueprints]` lands on Blueprint page where the full list renders unconditionally.
  - **PDF & TXT Encoding Fixes**: PDF sanitized for unicode (`├─→|-`, `└─→+`, `–—‑→-`, emoji→""), single roadmap numbering (`1. 1.` killed), 90-char wrapping, page-break check before each item, and footer once per page. TXT encoded with UTF-8 BOM (`utf-8-sig`) and ASCII tree (`|- +`).
  - **Engine Roadmap Scaling**: Prompt states roadmap step count follows complexity (simple 3-4, medium 5-7, complex 8-10; never default to 5) with extend preserving scaling and no caps/pads to 5.
  - **Testing & Documentation**: Enforced pre-seal compile gate (`py_compile`), comprehensive test suite (`tests/test_v1_6_1.py`), and verified green test suite (`148 passed`). CHANGELOG v1.6.1 and DEVLOG Entry 040.

## [1.6.0] - 2026-10-04

### Added / Changed
- Mission v1.6.0 — Library Completeness, Extend, Log Titles, Workspace Freshness & Export Restructure:
  - **Library Completeness**: Home library retains recent 5 with `[View all blueprints]` button. Blueprint page renders ALL user blueprints (newest first, scrollable) as rows with unique button keys per row id (`[Open]`, `[Extend]`, `[Delete(confirm)]`).
  - **Extend Versioning Flow**: Added `[Extend]` session panel (new changes + optional notes textareas) calling AI engine to produce a new versioned row (`v<N+1>`), linked via `parent_id`, leaving the parent untouched and opening the new version.
  - **Log Titles & Workspace Freshness**: Enforced required Milestone title (max 40 chars) on engineering logs; backfilled old rows on read. On login, `profiles.active_blueprint_id` is nulled; Blueprint page loads pointer or shows empty state `"Open a blueprint from your library or generate a new one."` when null.
  - **Export Restructure**: Markdown/TXT/HTML formatted with consistent section order, bullet/numbered lists, and unicode folder trees. PDF formatted with ASCII trees (`|-`, `+`), 90-character line wrapping, and section headers repeated across pages.
  - **Testing & Documentation**: Enforced pre-seal compile gate (`py_compile`), comprehensive test suite (`tests/test_v1_6_0.py`), and verified green test suite (`138 passed`, `.venv/bin/pytest`). CHANGELOG v1.6.0 and DEVLOG Entry 039.

## [1.5.8] - 2026-10-04

### Added / Changed
- Micro-Mission v1.5.8 — Hardcode winning OAuth exchange + remove witnesses:
  - **Hardcoded Winning Call**: Replaced the six-variant diagnostic sweep with the single winning call (`POST {SUPABASE_URL}/auth/v1/token?grant_type=pkce` with `apikey=ANON` and JSON `{"auth_code": code, "code_verifier": verifier}`).
  - **Witness Removal**: Deleted both diagnostics (`OAUTH-WITNESS` and `TOKEN-WITNESS`). Guaranteed zero witness strings remain in `app.py`.
  - **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`), asserted zero witness occurrences, and verified green test suite (`.venv/bin/pytest`).
  - **Documentation**: CHANGELOG v1.5.8 and DEVLOG Entry 037 (OAuth saga post-mortem).

## [1.5.7] - 2026-10-04

### Added / Changed
- Micro-Mission v1.5.7 — OAuth token grant-type sweep (diagnostic):
  - **Diagnostic Grant-Type Sweep**: Replaced single token POST / 400 retry with an ordered sweep of six attempts against `{SUPABASE_URL}/auth/v1/token` (query `grant_type=pkce`, query `grant_type=authorization_code`, form-encoded variants, and no-query grant body variants), stopping at the first HTTP 200 with `TOKEN-WITNESS` winner logging or fallback `st.error` with last response body.
  - **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and verified green test suite (`.venv/bin/pytest`).

## [1.5.6] - 2026-10-03

### Added / Changed
- Micro-Mission v1.5.6 — Single-Slot PKCE Verifier (Supabase State Stripping Rationale):
  - **Single-Slot Verifier Architecture**: Handled Supabase OAuth `/auth/v1/authorize` stripping custom state parameters. Before rendering the GitHub login link, any existing pending state row (`state='pending'`) in `public.oauth_states` is deleted, and a fresh single slot is inserted with `state='pending'` and `code_verifier=verifier`.
  - **Return Path & Token Exchange**: Return-path trigger relies on `code` alone (state optional). Fetches `code_verifier` where `state='pending'`, ordered by `created_at desc limit 1`. Issues POST request to `{SUPABASE_URL}/auth/v1/token?grant_type=pkce`. Retries once with `grant_type=authorization_code` on 400. On success, establishes session, mints `rt`, deletes the pending row, clears auth query params, and redirects to Home.
  - **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and verified green test suite (`133 passed`, including pending-slot insert/lookup and code-only return path tests).
  - **Documentation**: CHANGELOG v1.5.6 and DEVLOG Entry 036.

## [1.5.5] - 2026-10-02

### Added / Changed
- Micro-Mission v1.5.5 — GitHub Manual PKCE Flow, Auth Mode & Sign-Out Parameter Cleanup:
  - **Builder Manual GitHub PKCE**: Implemented manual cryptographic PKCE code verifier (`secrets.token_urlsafe(43)`), unpadded base64url SHA-256 code challenge (`s256`), and random state token (`secrets.token_urlsafe(16)`). Inserted state-verifier pairs into `public.oauth_states` table. Constructed `authorize_url` as `st.link_button` with state parameter separated from `redirect_to`.
  - **Builder Return & Token Exchange**: Handled `code` + `state` callback, looked up verifier in `public.oauth_states`, executed POST request to `{SUPABASE_URL}/auth/v1/token?grant_type=pkce`, established session, minted capability token (`rt`), deleted state row, pruned states older than 10 minutes, and redirected to Home. Removed v1.5.3 cookie storage module (`pkce_storage.py`).
  - **Builder Auth Mode & Sign-Out Cleanup**: Query-parameter driven mode selection (`mode=login` vs `mode=signup` with Display Name support). Sign-out cleanup now deletes all specified authentication query parameters (`rt`, `pg`, `code`, `state`, `type`, `token`, `token_hash`, `error`, `error_description`, `oauth_state`, `mode`, `auth_view`).
  - **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and verified green test suite (`130 passed`).
  - **Documentation**: CHANGELOG v1.5.5 and DEVLOG Entry 035.

## [1.5.3] - 2026-10-02

### Added / Changed
- Micro-Mission v1.5.3 — Restore GitHub OAuth via Scoped PKCE Verifier Storage:
  - **Builder PKCE Storage Module (`pkce_storage.py`)**: Restored minimal cookie get/set helper (`PkceCookieStorage` subclass of `SyncSupportedStorage`) scoped strictly to keys prefixed `"sb-pkce"` (code verifiers) with automatic in-memory fallback if the cookie component is unavailable.
  - **Builder Supabase Client Wiring**: Wired `PkceCookieStorage` into `get_client` with `options={"auth": {"storage": PkceCookieStorage(), "flow_type": "pkce", "persist_session": False}}`, ensuring the PKCE verifier survives the GitHub OAuth redirect while session persistence remains disabled (`rt` URL remains the sole session mechanism).
  - **Builder GitHub OAuth Restoration**: Restored the "Continue with GitHub" button and "or" divider on the auth card.
  - **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and verified green test suite (all tests passing, including round-trip storage tests).
  - **Documentation**: CHANGELOG v1.5.3 and DEVLOG Entry 033 (scoped verifier storage rationale).

## [1.5.1] - 2026-10-02

### Added / Changed
- Micro-Mission v1.5.1 — Auth Polish + FAQ Rename + OAuth Visibility:
  - **Builder Auth Page**: Removed "Account Access" header and "Mode" radio entirely. Mode is now driven by landing CTAs (`[Log In]` sets query param `mode=login`, `[Create Account]` sets `mode=signup`), read directly by the auth page.
  - **Builder Sign Up Button**: Enforced `use_container_width=True` on the Sign Up button so it spans full width like the GitHub button.
  - **Builder About FAQ**: Renamed "Mini-FAQ" header to "FAQ".
  - **Builder GitHub OAuth & Redirect Whitelist**: On OAuth exchange failure, displays `st.error` with the actual error message. On success, mints `rt`, sets session, and lands on Home. Added code comment documenting Supabase redirect URL whitelist requirements (app domain + `/streamlit` public URL).
  - **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and verified green test suite (all tests passing).
  - **Documentation**: CHANGELOG v1.5.1 and DEVLOG Entry 039 (plus Entry 032 addendum).

## [1.5.2] - 2026-10-02

### Added / Changed
- Micro-Mission v1.5.2 — Blueprint Refresh-Restore + Save Visibility:
  - **Builder Blueprint Default-Load**: When `active_blueprint_id` is missing in session state (e.g., after browser refresh), queries the current user's most recent row from `public.blueprints` and loads it automatically, showing the "generate or open from Home" message only when the library is truly empty.
  - **Builder Save Visibility**: Wrapped auto-save database insert in `try/except`; on failure, surfaces `st.warning("Blueprint generated but could not be saved to your library: {e}")` to make silent save failure impossible.
  - **Builder Home List Re-query**: Re-queries `public.blueprints` on every render (no stale caching).
  - **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and verified green test suite (all tests passing, including new unit tests in `tests/test_v1_5_0.py`).
  - **Documentation**: CHANGELOG v1.5.2 and DEVLOG Entry 038 (plus Entry 032 addendum).

## [1.5.0] - 2026-10-01

### Added / Changed
- Mission v1.5.0 — Persistent Blueprint Library:
  - **Builder Analyze Auto-Save**: Automatically inserts generated blueprints into `public.blueprints` (`title`, `blueprint_json`) on successful generation and stores `active_blueprint_id` in session state.
  - **Builder Home Library List**: Replaced placeholder on Dashboard with live query to `public.blueprints` (top 5 by date) showing Title, Date, and an `[Open]` button that loads the blueprint and navigates to the Blueprint page.
  - **Builder Blueprint DB Rehydration**: Blueprint page loads and parses `blueprint_json` from `public.blueprints` when `active_blueprint_id` is set, with clean fallback messaging.
  - **Database Migration & RLS**: Added `blueprints_migration.sql` with RLS policies (`auth.uid() = user_id`).
  - **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and verified green test suite (`123 passed`, including new unit tests in `tests/test_v1_5_0.py`).
  - **Documentation**: CHANGELOG v1.5.0 and DEVLOG Entry 037.

## [1.4.7] - 2026-10-01

### Added / Changed
- Micro-Hotfix v1.4.7 — Fixed `StreamlitWidgetAlreadyInstantiatedError` on contact submit by replacing post-render widget state assignments with `contact_clear_pending` and `contact_success` flags processed before widget instantiation coupled with `st.rerun()`.

## [1.4.5] - 2026-09-28

### Added / Changed
- Micro-Mission v1.4.5 — Export Redesign + Contact Clear + SMTP Fix:
  - **Builder Export Redesign**: Removed export format selectbox and top help tooltips. Rendered four explicit export format rows (Markdown / Plain text / HTML / PDF), each with a direct download button in col1 and an info popover (with expander fallback) in col2 displaying the format purpose explanation only when tapped.
  - **Builder Contact Clear**: Cleared Name, Email, and Message widget values in `session_state` on successful submit so the form is instantly empty while preserving the success message.
  - **Builder SMTP Config & Send**: Added pre-send assertion for `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, and `SMTP_PASSWORD` (showing `Contact form unavailable — email service not configured` if missing). Configured `smtplib.SMTP_SSL` for port 465 and `SMTP` with `starttls()` for 587. Caught `smtplib.SMTPException` specifically, showing `Email send failed: {e}` on failure without clearing the form, and printing `Contact email sent to {to_email}` on success.
  - **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and verified green test suite (`121 passed`, including new unit tests in `tests/test_v1_4_5.py`).
  - **Documentation**: CHANGELOG v1.4.5 and DEVLOG Entry 036 (plus Entry 031 addendum).

## [1.4.4] - 2026-09-27

### Added / Changed
- Micro-Mission v1.4.4 — Phase-2 Feedback Round 4 + Hint Elimination:
  - **Builder Stable Member-Since Field**: Computed formatted member-since (`"%d %b %Y"`, e.g. `"16 Sep 2026"`) once at login, signup, OAuth, and resume paths, storing as `user["member_since"]`; dashboard + account read only that field.
  - **Builder Vertical Folder Structure**: Rendered folder structures via `st.code(tree, language=None)` with `.replace("\\n", "\n")` so folders stack vertically.
  - **Builder Inline Export Purposes**: Integrated format purposes inline into export format selectbox labels (`"Markdown (.md) — editable spec for repos & AI assistants"`, etc.) and removed caption-below.
  - **Builder Auth Polish**: Removed email placeholder and rendered `"or"` divider as a flexbox line-text-line (`— or —`).
  - **Builder Danger Buttons & Hint Elimination**: Enforced `use_container_width=True` on all delete/cancel buttons. Injected aggressive CSS hiding `stWidgetTrailer`, `stCharCounter`, and browser hints. Asserted zero `st.form` remain in `app.py`.
  - **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and green pytest suite (`118 passed`, including new unit tests in `tests/test_v1_4_4.py`).
  - **Documentation**: CHANGELOG v1.4.4 and DEVLOG Entry 035 (plus Entry 031 addendum).

## [1.4.3] - 2026-09-27

### Added / Changed
- Micro-Mission v1.4.3 — Phase-2 Feedback Round 3:
  - **Builder Delete-All Expander Styling**: Wrapped delete-ALL two-step confirmation inside an `st.expander("Confirm delete all", expanded=True)` so existing expander-scoped red CSS applies to its Delete button (`#d33`) while Cancel stays gray.
  - **Builder Elimination of `st.form`**: Removed final remaining `st.form` wrapper (Analyze form) and `st.form_submit_button`, replacing them with plain widgets + `st.button`, completely killing the "Press Ctrl+Enter to submit form" hint everywhere in the app.
  - **Builder Dynamic Export Captions**: Added dynamic `st.caption` hints directly beneath the Export Format selectbox changing with selection (Markdown: `"editable spec for repos/AI assistants"`; Plain text: `"universal, opens anywhere"`; HTML: `"styled page for browsers/offline"`; PDF: `"fixed-layout for print/share"`).
  - **Builder Clean Member-Since Formatting**: Implemented `format_member_since` formatting ISO timestamps and date strings into clean calendar dates (`"%d %b %Y"`, e.g., `"16 Sep 2026"`), applied across login, signup, resume, OAuth, and dashboard tile.
  - **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and green pytest suite (`111 passed`, including new unit tests in `tests/test_v1_4_3.py`).
  - **Documentation**: CHANGELOG v1.4.3 and DEVLOG Entry 034 (plus Entry 031 addendum).

## [1.4.2] - 2026-09-27

### Added / Changed
- Micro-Mission v1.4.2 — Phase-2 Feedback Rounds 1+2 Combined:
  - **Builder Analyze Placeholders & Length Limits**: Restored Analyze form placeholders (`"e.g. Chat App"`, `"e.g. Students, Enterprise, Consumers"`, problem description example prompt) and removed `max_chars` from all Analyze inputs so counters ("0/200") vanish while placeholders stay.
  - **Builder Log Delete Red Styling**: Injected scoped CSS (`div[data-testid="stExpander"] div.stButton > button[kind="primary"]`) on Engineering Log page so confirm-Delete renders red (`#d33`) while Cancel stays gray.
  - **Builder Account Member-Since Persistence**: Included `created_at` in the rebuilt user dictionary on URL-resume refresh path (`?rt=...`) so Member Since survives refresh.
  - **Builder Log Timestamp Localization**: Converted UTC timestamps to Africa/Lagos local clock time using standard library `zoneinfo.ZoneInfo("Africa/Lagos")`.
  - **Builder De-Emoji Professionalism Sweep**: Removed all emoji glyphs from user-facing strings (module cards, sidebar headers, onboarding tour, delete markers), replacing them with Streamlit material icons (`:material/analytics:`, `:material/description:`, `:material/journal:`, `:material/shield:`, `:material/terminal:`) and clean plain text.
  - **Builder About Signature**: Updated signature to `"Built by CodeBreaker Dev"` (retaining the `[Contact us]` button).
  - **Builder Export Help Tooltips**: Added native hover tooltips (`help=`) to export format selectbox and all four export download buttons explaining format purpose and destination.
  - **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and green pytest suite (`106 passed`, including new unit tests in `tests/test_v1_4_2.py`).
  - **Documentation**: CHANGELOG v1.4.2 and DEVLOG Entry 033.

## [1.4.1] - 2026-09-27

### Added / Changed
- Micro-Mission v1.4.1 — Phase-2 Feedback Fixes & Contact Form:
  - **Builder PDF (`_latin1_safe`)**: Added robust `_latin1_safe(text)` mapping common arrows/symbols/emojis to ASCII and sanitizing via `.encode("latin-1","replace").decode("latin-1")`. Wrapped every string passed to FPDF in `render_blueprint_pdf` to eliminate `FPDFUnicodeEncodingException` recurrence. Added test coverage with emoji + arrow input.
  - **Builder Log Form & Project Labeling**: Removed `max_chars` from all log text areas, replaced `st.form` with plain widgets + `[Submit Log Entry]` button (removing Ctrl+Enter hint), added editable project name prefilled from Analyze session state (default "General"), stored `project_name` in Supabase, and rendered entries grouped by project with label `"[date] Project — milestone"`.
  - **Builder Contact Page**: Added new sidebar section "Contact" featuring form with Name, Email, Message (5 rows), and `[Send Message]` button. Implemented input validation, valid email format checks, Gmail SMTP integration to `codebreakerbuild@gmail.com`, success message `"Message sent. We'll respond within 24 hours."`, and 60s submission cooldown.
  - **Builder About & FAQ Accordions**: Replaced invented contact clause with "Built by Martins" + `[Contact us]` button linking to the Contact page (`st.query_params["pg"]="Contact"`, `st.rerun()`). Converted Mini-FAQ four items into `st.expander` accordions.
  - **Builder Log Delete Controls**: Updated two-step confirmation buttons to `use_container_width=True` with short labels `"Delete"` / `"Cancel"`.
  - **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and green pytest suite (`98 passed`, including new unit tests in `tests/test_v1_4_1.py`).
  - **Documentation**: CHANGELOG v1.4.1 and DEVLOG Entry 032.

## [1.4.0] - 2026-09-25

### Added / Changed
- Mission v1.4.0 — Dashboard, copy hygiene, log controls, About six:
  - **Builder Home Dashboard (Authenticated)**: Four tiles in 2x2 layout — (a) My Blueprints: session count + "persistent library arrives next update" caption; (b) My Engineering Logs: count + three most recent milestone titles (from Supabase, own rows only); (c) Quick Start: three action buttons (Analyze / Blueprint / Engineering Log) setting `st.query_params["pg"]=target` and `st.rerun()`; (d) Account: display name, email, member-since date. No version strings, no "AI-driven" phrasing.
  - **Builder Copy Hygiene**: Analyze — deleted subtitle, all placeholder texts, word-counter hints, and Skill Level selectbox; Blueprint — status line set to "Generating blueprint…", deleted "What do I do with this file?" explanatory block (export format boxes untouched); Engineering Log — deleted subtitle and textarea placeholder/word-counter hints. Banned-strings list fully enforced.
  - **Builder Engineering Log Controls**: Added sort selectbox `["Newest first","Oldest first","A→Z (milestone)","Z→A (milestone)"]` default Newest, applied at render; per-entry delete made two-step (`[Confirm delete]` + `[Cancel]` via per-entry session_state flag); added separate "Delete ALL my logs" button with its own two-step confirm.
  - **Builder About Six Additions in Order**: (1) "How CodeBreaker protects you" trust section; (2) Module guide one-liners; (3) Workflow recipe (`Analyze→Blueprint→export→Log→repeat`); (4) Mini-FAQ four questions; (5) renamed lecturer playbook to "For Lecturers & Supervisors"; (6) signature line "Built by Martins — The CodeBreaker Team" + contact placeholder.
  - **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`), zero-network tests, mock supabase dashboard rendering, sort reordering, two-step delete, and green pytest suite (`90 passed`, including `tests/test_v1_4_0.py`).
  - **Documentation**: CHANGELOG v1.4.0 and DEVLOG Entry 031.

## [1.3.0] - 2026-09-25

### Added / Changed
- Mission v1.3.0 — Landing + One-Card Auth + Sidebar Contract:
  - **Public Landing Page**: Professional logged-out default view featuring headline, one-paragraph value proposition, "How it works" three steps, module icon-cards (Analyze, Blueprint, Engineering Log), and CTAs `[Log In]` `[Create Account]`. No sidebar pre-auth.
  - **One-Card Auth View**: Reached exclusively via landing CTAs. Single container card housing mode toggle (Log In / Sign Up), email, password, conditional display name, button row (`[Log In]` / `[Forgot Password]` or `[Sign Up]`), thin divider `"or"`, `[Continue with GitHub]`, and `← Back to overview` link. Reset flow stays inside the card.
  - **Authenticated Sidebar Contract**: Strict order enforced — Admin Pulse (admin only) → section radios (Home, Analyze, Blueprint, Engineering Log, About) with no "Navigation" caption → Persistence Debug (admin only) → Sign Out LAST.
  - **Routing & Home Polish**: Authenticated users hitting root land on Home. Version banners removed from Home.
  - **Banned-Strings Sweep**: Zero user-facing occurrences of "Row Level Security", "RLS", "Supabase", "handshake", "AI-driven", version strings (`v1.x`), "press enter", or "0/100 words". Tone professional and jargon-free.
  - **Testing & Verification**: Enforced pre-seal compile gate (`python3 -m py_compile`) and green pytest suite (`86 passed`, including new unit tests in `tests/test_v1_3_0.py`).
  - **Documentation**: CHANGELOG v1.3.0 and DEVLOG Entry 028.

## [1.2.6] - 2026-09-23

### Fixed
- Micro-hotfix v1.2.6 — RPC parameter-name drift:
  - **API Contract Alignment**: Updated every RPC call site in `app.py` (`create_resume_token`, `verify_resume_token`, `revoke_resume_token`) to pass exactly the `p_`-prefixed parameter names (`p_uid`, `p_refresh_token`, `p_token_hash`, `p_expires_at`) as defined in `resume_sessions_migration.sql`.
  - **Zero-Network Source-Consistency Test**: Added `tests/test_rpc_source_consistency.py` to statically parse migration function signatures and assert that every RPC parameter dictionary key in `app.py` matches its target database function.
  - **API Change Governance**: Renaming DB function parameters is an API change; RPC callers migrate in the same release.
  - **Testing & Verification**: Enforced pre-seal compile gate (`python3 -m py_compile`) and green test suite (`.venv/bin/pytest tests/ -q`).
  - **Documentation**: CHANGELOG v1.2.6 and Entry 030 addendum.

## [1.2.5] - 2026-09-23

### Fixed
- Micro-hotfix v1.2.5 — 42702 on `"token_hash"` (PL/pgSQL parameter renaming class-wide):
  - **Parameter & Out-Param Collision Class**: PL/pgSQL parameters and `RETURNS TABLE` out-parameters collide with table column names even on the comparison side of qualified expressions (`rs.token_hash = token_hash`).
  - **Durable Fix (p_ prefix)**: Renamed ALL function parameters and `RETURNS TABLE` out-params with `p_` prefix (`p_token_hash`, `p_user_id`, `p_refresh_token`, `p_expires_at`, `p_uid`) across all four security-definer functions (`create_resume_token`, `verify_resume_token`, `revoke_resume_token`, `prune_expired_resume_sessions`).
  - **Variable_Conflict Pragmas Banned**: Enforced parameter renaming as the sole durable architectural fix (variable_conflict pragmas banned).
  - **Re-Run Safe Migration**: Preserved re-run safety (omitting DROP TABLE).
  - **Testing & Verification**: Enforced pre-seal compile gate (`python3 -m py_compile`) and green pytest suite.
  - **Documentation**: CHANGELOG v1.2.5 and Entry 030 addendum.

## [1.2.4] - 2026-09-23

### Fixed
- Micro-hotfix v1.2.4 — Postgres 42702 ambiguity in `resume_sessions` definer functions:
  - **PL/pgSQL RETURNS TABLE Out-Params & Column Collisions**: PL/pgSQL `RETURNS TABLE` out-parameters act as local variables inside function bodies, causing Postgres error 42702 ("column reference is ambiguous") when unquoted/unqualified column names like `expires_at` match out-params/variables. Fully qualified all column references with `resume_sessions.` across all four security definer functions (`create_resume_token`, `verify_resume_token`, `revoke_resume_token`, `prune_expired_resume_sessions`).
  - **Re-Run Safe Migration**: Removed any DROP TABLE statements (retaining `create table if not exists` and `create or replace function`) so database re-runs never clear active sessions.
  - **Testing & Verification**: Enforced pre-seal compile gate (`python3 -m py_compile`) and green pytest suite.
  - **Documentation**: CHANGELOG v1.2.4 and Entry 030 addendum.

## [1.2.3] - 2026-09-22

### Added / Changed
- Mission v1.2.3 — URL capability resume & abandonment of all client storage:
  - **SQL Migration & Security Definers**: Created `public.resume_sessions` table with RLS (owners select/delete own rows only) and security-definer functions (`create_resume_token`, `verify_resume_token`, `revoke_resume_token`, `prune_expired_resume_sessions`).
  - **URL Capability Tokens (`?rt=...`)**: Abandoned all client storage (localStorage & cookies). Replaced with secure server-side session persistence via URL capability tokens (`rt = secrets.token_urlsafe(32)`).
  - **Token Rotation & Revocation**: Automatic token rotation on each successful boot (new mint, revoke old hash, update URL query parameter) and sign-out row revocation + parameter clearing.
  - **Persistence Debug Shrink**: Shrank Persistence Debug to site owners (`ADMIN_EMAIL`) showing `rt` present (bool), last verify result, and gate flags. Retired `?pdebug=1`.
  - **Testing & Verification**: Zero-network unit tests for minting, verification, rotation, revocation, expired tokens, and admin persistence debug. Enforced pre-seal compile gate and green pytest suite (`80 passed`).
  - **Documentation**: CHANGELOG v1.2.3 and DEVLOG Entry 030.

## [1.2.2] - 2026-09-22

### Added / Changed
- Mission v1.2.2 — Refresh Logout Final Convergence (Branches H1, H2, H3 & WITNESS):
  - **Branch H1 (Cookie Options & Iframe Scope / Fallback)**: Explicitly passed `path="/"`, `same_site="lax"`, `secure=True`, `max_age=604800` to cookie controller; structured boot flow with `st.context.cookies` fast-path optimization and client-component read with bounded rerun (render-2 gate open).
  - **Branch H2 (Per-Session Supabase Singleton)**: Refactored `get_client()` in `supabase_client.py` to store/retrieve a per-session Supabase client singleton inside `st.session_state["supabase_client_instance"]`, eliminating cross-user session leakage across concurrent Streamlit sessions.
  - **Branch H3 (Gate Flags)**: Guaranteed rehydration sets all authentication gate flags (`user`, `access_token`, `refresh_token`, `expires_at`).
  - **WITNESS Panel**: Added side-by-side observability in Persistence Debug showing `st.context.cookies` names/lengths, controller read (`cb_session`), gate flags, and client instance ID (`id(client)`).
  - **Testing & Verification**: Added zero-network unit tests for cookie options, singleton identity, flags set, and render-2 gate open. Enforced pre-seal compile gate and green pytest suite (`75 passed`).
  - **Documentation**: CHANGELOG v1.2.2 and DEVLOG Entry 029.

## [1.2.1] - 2026-09-22

### Added / Changed
- Mission v1.2.1 — Persistence Parked & Window Closed:
  - **Retirement of `?pdebug=1`**: Removed the temporary `?pdebug=1` diagnostic query flag path entirely. Persistence Debug is now strictly restricted to site owners post-login (`ADMIN_EMAIL`).
  - **Login User Expectation Caption**: Added user-reassurance caption on the login page: `"Sessions reset on reload in this hosting tier — please log in to continue. Your work is always safe."`
  - **Cookie Persistence Parked**: Kept cookie writing infrastructure intact as an architectural asset, adding a comment referencing DEVLOG Entry 027.
  - **Testing & Verification**: Enforced pre-seal compile gate (`python3 -m py_compile`) and green test suite (`.venv/bin/pytest tests/ -q`).
  - **Documentation**: CHANGELOG v1.2.1 and DEVLOG Entry 027.

## [1.2.0] - 2026-09-22

### Added / Changed
- Mission v1.2.0 — Cookie-Based Persistence & Library Abandonment Postmortem:
  - **Replaced `streamlit-local-storage`**: Removed `streamlit-local-storage` from requirements and all call sites, replacing it with `streamlit-cookies-controller` (`CookieController`).
  - **Server-Side Request Cookie Boot Read**: Implemented server-side synchronous boot read via `st.context.cookies` FIRST on the initial render, eliminating the need for client-component boot delay or re-run hacks on standard server-rendered loads.
  - **Bounded Fallback & Cleanup**: Fallback to component get retained only when `st.context` is unavailable. Robust corrupt-value cleanup (`json.loads` failure, legacy `"[object Object]"`) deletes cookies, cleans login gate, and records exception class into `persist_debug`.
  - **Admin Gating Independence**: Admin Pulse is strictly gated when logged-in email == `ADMIN_EMAIL`, never influenced by `?pdebug=1`. Persistence Debug is strictly admin post-login OR the temporary `?pdebug=1` window (retiring in v1.2.1 after acceptance).
  - **Testing & Verification**: Enforced pre-seal compile gate (`python3 -m py_compile`) and green test suite (`.venv/bin/pytest tests/ -q`).
  - **Documentation**: CHANGELOG v1.2.0 and DEVLOG Entry 026 (Library Abandonment Postmortem).

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
