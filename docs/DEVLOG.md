# CodeBreaker Development Log

## Entry 054: True Single-Line Cross-Links, Auth Form Isolation & Uniform Module Cards (v1.7.10)
- **Date**: 2026-10-09
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.7.10 MICRO-MISSION — True single-line cross-links, auth form isolation, uniform module cards

### Design Notes & Architectural Decisions
1. **True Single-Line Cross-Links & `data-testid` Selector Law**:
   - Configured inner columns to `st.columns([0.7, 0.3], gap="small")` with right-aligned question text and left-aligned link button.
   - **Law**: Applied exact `data-testid` selectors (`button[data-testid="stBaseButton-tertiary"]`) and `:has()` scoping (`div[data-testid="stHorizontalBlock"]:has(button[data-testid="stBaseButton-tertiary"])`), completely purging legacy `button[kind=` selectors.
2. **Auth Form Isolation Rule**:
   - Defined `clear_auth_form_state()` managing the full key list (`auth_card_email`, `auth_card_password`, `auth_card_display_name`).
   - Enforced key deletion on every view transition (cross-links, landing CTAs, back-to-overview) and upon successful sign-in/sign-up, ensuring no credentials survive a view switch.
3. **Equal-Height Card Grid Rule**:
   - Rebuilt Workspace Modules cards to share a unified `.module-card` CSS class with a fixed min-height (`210px`) for equal vertical sizing.
   - Standardized the third card header to the identical icon + single-title pattern (`**Engineering Log**`, zero `"JOURNAL"` strings).
4. **Testing & Verification**:
   - Enforced compile gate (`py_compile`), source-scan unit tests (`tests/test_v1_7_10.py`), and verified green test suite.

## Entry 053: Cross-Link Single-Line Fix & Ghost Root-Cause Closure (v1.7.9)
- **Date**: 2026-10-09
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.7.9 MICRO-MISSION — Cross-link single-line fix + ghost root-cause closure

### Design Notes & Architectural Decisions
1. **Cross-Link Single-Line Precision & `:has()` Scoping Trick**:
   - Configured inner auth switch columns to `st.columns([0.75, 0.25], gap="small")` with the question rendered right-aligned (`text-align: right`).
   - Injected the CSS selector utilizing `:has(button[kind="tertiary"])` to scope zero-margin and matching line-height (`2.25rem`) precisely to the horizontal block containing the auth switch without collateral impact on other paragraphs or buttons.
2. **Ghost Root-Cause Closure & Custody Split**:
   - Verified that the v1.7.8 root-container pattern (`_ROOT = st.empty()` + `with _ROOT.container():`) is fully present and active.
   - **Custody Split**: Residual page ghosting during rapid interactions is a platform+network custody phenomenon caused by Streamlit's asynchronous WebSocket streaming repaint combined with client-side render latency. The root-container pattern is the maximum achievable server-side lever; a 100% atomic repaint cure requires full frontend control deferred to future hosting migration.
3. **Testing & Verification**:
   - Enforced compile gate (`py_compile`), source-scan unit tests (`tests/test_v1_7_9.py`), and verified green test suite.

## Entry 052: Theme Restore, One-Line Cross-Links & Root-Container Repaint Cure (v1.7.8)
- **Date**: 2026-10-09
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.7.8 MICRO-MISSION — Theme restore, one-line cross-links, root-container repaint cure

### Design Notes & Architectural Decisions
1. **Theme Restore & Config-Override Law**:
   - Restored full `[theme]` configuration (`primaryColor = "#1a73e8"`, `backgroundColor = "#ffffff"`, `secondaryBackgroundColor = "#f0f2f6"`, `textColor = "#111111"`, `font = "sans serif"`) alongside `[client] toolbarMode = "minimal"` in `.streamlit/config.toml`.
   - **Law**: Any future `config.toml` edit must preserve `[theme]` verbatim.
2. **One-Line Cross-Links Spec**:
   - Replaced scattered cross-link blocks with `outer = st.columns([0.25, 0.5, 0.25])` and inner `q, l = st.columns([0.72, 0.28])`.
   - Injected alignment CSS (`p {margin: 0;}` and `div[data-testid="stButton"] button[kind="tertiary"] {padding: 0; margin: 0; line-height: inherit;}`) so question and link sit on one cleanly centered line.
3. **Root-Container Repaint Pattern**:
   - Inserted `_ROOT = st.empty()` immediately after `st.set_page_config(...)`.
   - Wrapped the entire remaining UI in `with _ROOT.container():` via uniform mechanical indentation. This guarantees that each Streamlit run atomically clears the previous page content before streaming the new run.
4. **Testing & Verification**:
   - Enforced compile gate (`py_compile`), source-scan unit tests (`tests/test_v1_7_8.py`), and verified green test suite.

## Entry 051: In-Place Cross-Links, Single-Page Render & Minimal Toolbar (v1.7.6)
- **Date**: 2026-10-09
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.7.6 MICRO-MISSION — In-place cross-links, single-page render + light auth, minimal toolbar

### Design Notes & Architectural Decisions
1. **In-Place Cross-Links & Anchor-New-Tab Law**:
   - **Law**: Markdown/HTML anchors (`<a href="?mode=...">`) in Streamlit render as browser navigation elements that can trigger new tabs or full-page reloads.
   - **Mitigation**: Deleted all HTML/markdown anchors. Rebuilt auth switching cross-links using centered spacer columns `[0.3, 0.4, 0.3]` with the middle split into text (left column, default black) and tertiary button (right column, `type="tertiary"`, styled with `text-decoration: underline; color: #1a73e8;`) executing `st.session_state["auth_view"] = ...` and `st.rerun()` in-place. Zero anchors remain.
2. **Single-Page Render & Light Auth (Progressive Repaint)**:
   - Audited page gating: exactly one section renders per run (`if not user:` auth/landing block strictly `elif`/`else`-gated against authenticated workspace).
   - Auth form render path performs zero Supabase/network calls when no session token exists in `session_state`.
   - Login-success path clears email/password input widget states from `st.session_state` before triggering navigation rerun.
3. **Minimal Toolbar Decision**:
   - Created `.streamlit/config.toml` configuring `[client] toolbarMode = "minimal"`, suppressing extraneous development toolbar items for a clean production presentation.
4. **Testing & Verification**:
   - Enforced compile gate (`py_compile`), source-scan unit tests (`tests/test_v1_7_6.py`), and verified green test suite.

## Entry 050: Relocate Log Out to Kill Sidebar Auto-Open Trigger (v1.7.4)
- **Date**: 2026-10-09
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.7.4 MICRO-MISSION — Relocate Log Out to kill sidebar auto-open trigger

### Design Notes & Architectural Decisions
1. **Sidebar Auto-Open Root Cause & Mitigation**:
   - Sidebar open/close state is client-persisted across reruns. `initial_sidebar_state` applies only on fresh loads. Interacting with or logging out from a sidebar control previously acted as the auto-open trigger.
   - Deleted the Log Out button from the sidebar entirely, converting the sidebar into a pure navigation-only component (`Section` radio).
2. **Account Card Log Out Relocation**:
   - Added a full-width `"Log Out"` button (`type="secondary"`, `use_container_width=True`) inside the Account card on Home, directly below the Member Since line.
   - Its handler performs the identical sign-out sequence (Supabase sign-out, session/token clears, nav to landing, rerun).
3. **Residual Law**:
   - A manually-opened sidebar survives logout→login (client memory) — close manually or reload the page to reset.
4. **Testing & Verification**:
   - Enforced compile gate (`py_compile`), source-scan unit tests (`tests/test_v1_7_4.py`), and verified green test suite.

## Entry 048: Provider-Diversity Rule, Blueprint Library Button Rename & Sidebar Platform Verdict (v1.7.3)
- **Date**: 2026-10-09
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.7.3 MICRO-MISSION — Provider-diversity rule, library copy rename, sidebar auto-open verdict

### Design Notes & Architectural Decisions
1. **Provider-Diversity Rule**:
   - Inserted verbatim rule text into `ai_engine.py` SYSTEM_PROMPT (affecting both generation and extend prompts): `"When the project requires an LLM/AI API or any third-party API, weigh alternatives (OpenAI, Google Gemini, Anthropic Claude, open-source models via Groq/Ollama) against the user's stated constraints (cost, privacy, offline use, latency); select the best-fit provider, reflect it in the tech stack, and justify the choice in one sentence inside the summary; never default to OpenAI GPT-4o without explicit justification."`
2. **Blueprint Library Button Copy Rename**:
   - Replaced button label `"← Back to All Blueprints"` with `"← Blueprint Library"` in `app.py`.
3. **Sidebar Auto-Open Verdict & Reset Note**:
   - Investigated branch (a) code-side vs (b) platform-side. Verified that `st.set_page_config` is called exactly once with `initial_sidebar_state="collapsed"`.
   - **Verdict**: Branch (b) platform-side is true. Streamlit mobile persists sidebar open/close state in client storage across sessions.
   - **Reset Note**: `"clear site data or use incognito to reset the persisted sidebar preference"`.
4. **Testing & Verification**:
   - Enforced pre-seal compile gate (`py_compile`), source-scan unit tests (`tests/test_v1_7_3.py`), and verified green test suite.

## Entry 047: Red Library Confirm, Two-Tone Cross-Links & Witness Retirement (v1.7.2)
- **Date**: 2026-10-09
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.7.2 MICRO-MISSION — Red library Confirm, two-tone cross-links, witness retirement

### Design Notes & Architectural Decisions
1. **Red Library Confirm via Expander Mechanism**:
   - Identified that Engineering Log successfully produces red confirms by housing entries in `st.expander` and targeting `div[data-testid="stExpander"] div.stButton > button[kind="primary"]`.
   - Converted Blueprint library items from `st.container` to `st.expander`, enabling the identical shared CSS mechanism so both library and log confirm buttons render in uniform red (`#d33`).
2. **Two-Tone Cross-Links & Boot Mode Handler**:
   - Deleted full-blue tertiary buttons.
   - Rendered bottom-centered markdown links (`"Don't have an account? <a href=\"?mode=signup\">Sign up</a>"` / `"Already have an account? <a href=\"?mode=login\">Log in</a>"`), where text stays default black and the anchor inherits theme primary blue without inline color overrides.
   - Added boot query-param handler (`st.query_params.get("mode") in ("signup", "login")`) to instantly switch auth view, delete param, and rerun.
3. **Witness Retirement & PDF Saga Final Closure**:
   - Permanently retired LIBRARY-WITNESS traceback rendering, restoring the library except branch to `st.info("Library unavailable.")` as the library is proven healthy.
   - PDF saga final closure (Hulk PDF as proof artifact) and adherence to two-tone link rule.
4. **Testing & Verification**:
   - Enforced pre-seal compile gate (`py_compile`), unit tests (`tests/test_v1_7_2.py`), and verified green test suite (`193 tests passed`).

## Entry 046: Library Red Confirm, Cross-Links Restyle & Module-Cache Cure (v1.7.1)
- **Date**: 2026-10-09
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.7.1 MICRO-MISSION — Library red confirm, cross-links restyle, ai_engine reload cure

### Design Notes & Architectural Decisions
1. **Library Confirm Red Unification**:
   - Inspected the exact CSS injection mechanism used to make Engineering Log confirm buttons red (`div[data-testid="stExpander"] div.stButton > button[kind="primary"]`).
   - Applied the identical mechanism to Blueprint library containers (`div[data-testid="stContainer"] div.stButton > button[kind="primary"]`) so both render red (`#d33`) instead of default blue.
2. **Auth Cross-Links Restyle**:
   - Deleted boxed switch buttons from under the Log In / Create Account rows.
   - Rendered each switch at the bottom of the auth view, centered via `st.columns([0.25, 0.5, 0.25])` in the middle column (`col_ac2`), using `type="tertiary"`, `use_container_width=True`, and existing keys (`auth_switch_to_signup` / `auth_switch_to_login`).
   - Injected ONCE via `st.markdown(unsafe_allow_html=True)` the CSS targeting `div[data-testid="stButton"] button[kind="tertiary"]` (`color: #1a73e8; font-weight: 600; font-size: 1.05em;`). Handlers maintain `nav_pending` + `st.rerun()`.
3. **The Imported-Module Cache Law & Module-Cache Cure**:
   - **Law**: Streamlit hot-reloads `app.py` on file save, but does **not** automatically reload imported non-Streamlit modules (`ai_engine.py`). Consequently, code changes in `ai_engine.py` were not reflected in the running application without a full server reboot.
   - **Cure**: Inserted an mtime-based reload block immediately after the `ai_engine` import in `app.py` checking `os.path.getmtime(ai_engine.__file__)` against session state (`_ae_mt`), invoking `importlib.reload(ai_engine)`, and rebinding every imported name into `globals()`. Reboot remains the ultimate backup.
4. **Testing & Verification**:
   - Enforced pre-seal compile gate (`python3 -m py_compile`) and 100% test pass rate (`pytest tests/ -q` — 191 tests passed).

## Entry 045: Confirm Unification, DD-MM-YYYY Display Law & Auth UX (v1.7.0)
- **Date**: 2026-10-09
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.7.0 MICRO-MISSION — Confirm unification, DD-MM-YYYY display law, auth UX cross-links & sidebar rename

### Design Notes & Architectural Decisions
1. **Confirm Unification & Caption Elimination**:
   - Standardized Blueprint library and Engineering Log deletes to share the identical red confirm mechanism (`type="primary"`, side-by-side equal columns via `st.columns(2)`, `use_container_width=True`).
   - Completely deleted every instance of the `"Confirming will permanently delete this item."` caption from both surfaces, ensuring cleaner cards and unified destructive confirmation UX.
2. **ISO-Store / DD-MM-YYYY-Display Law**:
   - Implemented `fmt_date(d)` helper in `app.py` parsing ISO timestamps into Africa/Lagos calendar dates formatted as `"DD-MM-YYYY"`.
   - Applied uniformly across library date chips, Home recent chips, log `[date]` prefixes, and expander Timestamp lines (retaining `HH:MM:SS`).
   - DB storage remains ISO forever (`created_at`). PDF footer renders `DD-MM-YYYY` via `strftime("%d-%m-%Y")`. `build_pdf_lines` emits subtitle `"CodeBreaker System Architecture Blueprint"` (italic 9) and footer per `docs/pdf_chrome_spec.md`.
3. **Auth UX Cross-Links & Sidebar Rename**:
   - Added bottom-centered cross-links `"Don't have an account? Sign up"` on login view and `"Already have an account? Log in"` on create-account view.
   - Renamed sidebar `"Sign Out"` to `"Log Out"`.
   - Configured `initial_sidebar_state="collapsed"` in `st.set_page_config`. Both auth paths execute all session work before first render (render-after-work).
4. **Accepted Platform Artifacts & Verification**:
   - Accepted platform repaint and mobile sidebar overlay behaviors; enforced `py_compile`, source-scan rules, quoted-lines report rule, and verified green pytest suite.

## Entry 044: Red Confirm Law & Render-After-Work Pattern for Transition Cleanliness (v1.6.7)
- **Date**: 2026-10-08
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.6.7 MICRO-MISSION — Red Confirm, login flash minimization, footer chrome final

### Design Notes & Architectural Decisions
1. **Red Confirm Law for Destructive Actions**:
   - Every delete-confirm button across Blueprint library armed rows and Engineering Log armed entries utilizes `st.button(..., color="red")` (supported in Streamlit 1.65+).
   - A defensive `try/except TypeError` fallback injects a keyed CSS block targeting the confirm button with `#ff4b4b` background and white text, strictly preventing destructive confirmation buttons from falling back to blue primary style.
2. **Render-After-Work Pattern for Login Flash Minimization**:
   - In the auth branch (`if not user:`), all Supabase session rehydration (`?rt=`), OTP verification (`verify_otp`), OAuth code exchange (`oauth_states`), and client initialization are executed strictly *before* any UI rendering call.
   - Flash alerts, warnings, and errors are temporarily buffered in `st.session_state["auth_flash"]` and rendered once in a single atomic paint pass when the auth card / landing DOM renders at the end of the branch, reducing client repaint artifacts to imperceptible levels.
3. **Footer Chrome & PDF Structure Finalization**:
   - `build_pdf_lines` returns clean content without footer strings.
   - `render_blueprint_pdf` applies page-1 bold 16 title and italic 9 subtitle, formats the folder structure in Courier 9, and renders the exact footer string `"Generated by CodeBreaker Workspace + <date>"` italic 8 via `pdf.set_y(pdf.get_page_height() - 15)` on the last page only.
4. **Testing & Verification**:
   - Enforced pre-seal compile gate (`py_compile`), comprehensive test suite (`tests/test_v1_6_7.py`), source scans validating `color="red"` usage and render-order sequencing, and verified green test suite (`178 tests passed`).

## Entry 043: Consolidated Residuals Closure, N/A Law & Stacked Full-Width Button Rules (v1.6.6)
- **Date**: 2026-10-08
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.6.6 MICRO-MISSION — PDF Courier tree + italic footer chrome + heading count removal + login flash + radio label + arm/cancel final layout + N/A law

### Design Notes & Architectural Decisions
1. **N/A Law Enforcement**:
   - Enforced rigorous `"N/A"` fallback across all empty slots (engineering log fields, export Project Context, etc.), banning `"Null"` or blank fallbacks. Added a source-scan test asserting no `"Null"` fallback literal exists in `app.py` or `ai_engine.py`.
2. **Stacked Full-Width & Two-Row Layout Rule**:
   - *Blueprint Library Armed Row*: Renders two stacked rows — row1 `[Open][Extend]`, row2 `[Confirm][Cancel]` (labels exactly `"Confirm"` and `"Cancel"`, zero ellipsis, `use_container_width=True`).
   - *Engineering Log Armed Entry*: Renders `[Confirm]` then `[Cancel]` as two stacked full-width buttons in a single column (`use_container_width=True`), with un-armed showing one full-width `[Delete]`.
3. **Arm Expiry & Self-Disarm**:
   - Per-row arm timestamps stored in `session_state` (`arm_time_bp_...`, `arm_time_log_...`), with automatic expiry clearing stale arms older than 10 seconds on render.
4. **PDF Courier Tree & Footer Chrome**:
   - `build_pdf_lines` free of footer string; PDF title and subtitle on page 1; footer rendered once via `pdf.set_y(pdf.get_page_height() - 15)` on last page; Courier font applied to folder structure lines.
5. **Login Flash & Rerun Finalization**:
   - Landing `[Log In]` and `[Create Account]` handlers set `nav_pending` and call `st.rerun()` as the final statement of the branch.
6. **Roadmap Heading**:
   - Exactly `"Implementation Roadmap"` everywhere, deleting any `(N Steps)` count suffix.
7. **Testing & Verification**:
   - Enforced pre-seal compile gate (`py_compile`), comprehensive test suites including new `tests/test_v1_6_6.py`, and verified green test suite (`173 tests passed`).

## Entry 042: PDF Tree Monospace, Footer Chrome, Heading Count Removal & Cloud Hot-Reload Cache Law (v1.6.5)
- **Date**: 2026-10-08
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.6.5 MICRO-MISSION — PDF tree monospace + real footer + heading count removal + version dedupe + delete arm/cancel + login flash + sidebar label cleanup

### Design Notes & Architectural Decisions
1. **PDF Saga Post-Mortem & Proof-Gate**:
   - *Bytearray / Output type safety*: Ensuring `render_blueprint_pdf` returns `bytes` via `_out if isinstance(_out, bytes) else bytes(_out)` preventing type mismatches in file download buttons.
   - *Guard-as-Witness*: Codepoint sanitizer mapping unicode tree drawing characters (`├`, `└`, `─`, `│`) to ASCII equivalents (`|`, `+`, `-`) and falling back for `ord > 255`, guaranteeing latin-1 safe output under FPDF.
   - *Proof-Gate*: Pre-seal compile gate (`py_compile`) and test suite verification (`pytest`) ensuring zero regressions across all 164 tests.
2. **Cloud Hot-Reload Cache Law**:
   - *Reboot after pushing imported-module changes*: When underlying module functions (such as `ai_engine.py` rendering logic or helper functions) are updated, Streamlit server hot-reload caches imported module namespaces unless explicitly rebooted or reloaded, reinforcing the rule that dependency changes require process synchronization.
3. **Courier-Tree & Footer Chrome Decisions**:
   - *Courier Tree Font*: Inside `render_blueprint_pdf`, lines belonging to the Folder Structure section (between `"## Folder Structure"` and the next `"## "` header) render with `pdf.set_font("Courier", "", 9)` so indentation aligns in fixed columns; all other lines stay Helvetica; Helvetica is restored after the section.
   - *Footer Chrome*: `build_pdf_lines` no longer appends the footer line; page 1 renders title `# ` as bold 16 and adds an italic 9 subtitle line `"CodeBreaker System Architecture Blueprint"` beneath it; after content loop, on the last page calls `pdf.set_y(pdf.get_page_height() - 15)` and renders italic 8 `"Generated by CodeBreaker Workspace + <date>"` once. Added `pdf.get_page_height = lambda: pdf.h` compatibility helper.
4. **Heading Count Removal & Version Dedupe**:
   - *Roadmap Heading*: In-app heading and Markdown exports standardized to exactly `"Implementation Roadmap"`, deleting the `"(N Steps)"` suffix everywhere.
   - *Version Deduplication*: Render-time regex strips trailing `" — vN"` and `"(vN)"` from stored titles (Home list, library rows, blueprint header), showing version only as `"(vN)"` when version > 1. Extend stores base title + version = parent + 1.
5. **Delete Arm/Cancel Expiry & UI Cleanups**:
   - *Delete Arm/Cancel*: First Delete arms row (`[Confirm delete]` + `[Cancel]`); Cancel disarms; 10-second auto-expiry clearing timestamp on rerun for both blueprints and engineering log entries. Un-armed rows show plain `[Delete]`.
   - *Sidebar Radio Label Cleanup*: Non-empty label (`label="Section"`) with `label_visibility="collapsed"` and zero `index=` argument, making `session_state` the sole driver and eliminating both Streamlit log warning floods.
   - *Login Flash*: Landing CTAs (`[Log In]`, `[Create Account]`) set `nav_pending` and `st.rerun()` immediately.
6. **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`), comprehensive test suites including new `tests/test_v1_6_5.py`, and verified green test suite (`164 tests passed`).

## Entry 041: Codepoint Sanitizer + Multi_Cell-Only PDF Contract + Nav Single-Source Rule (v1.6.2)
- **Date**: 2026-10-05
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.6.2 PDF Renderer Rewrite, Extend Provider Unification, Nav Single-Source, Context N/A, Home Count Removal, Log N/A + Optional Title

### Design Notes & Architectural Decisions
1. **PDF Renderer Rewrite (Strict Contract)**: Exposed `sanitize_pdf_text(s)` with codepoint-wise mapping (`├`→`|`, `└`→`+`, `─`→`-`, `│`→`|`, `–—‑`→`-`, etc.) plus fallback where any character with `ord > 255` becomes `"-"`. Exposed `build_pdf_lines(bp)` returning full document lines. Restricted `render_blueprint_pdf` to ONLY call `pdf.multi_cell(0, 5.5, line)` per line with `get_y()` page-break checks and `set_font(style="B")` for headers (zero cell/write calls for dynamic content).
2. **Extend Provider Unification**: Unified `extend_blueprint` and `generate_blueprint` behind a shared `_call_ai` helper using exact same model constants, retry chain, and named provider error reporting.
3. **Project Context N/A & Home Count Removal**: Missing/empty context fields render `"N/A"` (legacy sentences deleted). Removed "Saved Blueprints" count metric from Home dashboard.
4. **Navigation Single Source**: Synchronized navigation via `nav_radio` session state key and `pg` query param across all navigation triggers (sidebar radio, Home open, view all blueprints, Quick Start buttons, About contact), ensuring second blueprint opens reliably every time.
5. **Log N/A & Optional Milestone Title**: Milestone title made optional (`"Milestone Title (optional)"`, no validation error when blank, defaulting to progress excerpt or `"N/A"`). Empty progress/bugs/learnings store as `"N/A"`, and expanders always list all three fields. Quick Start button renamed to `"Eng. Log"`.
6. **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`), comprehensive test suite (`tests/test_v1_6_1.py`), and verified green test suite (`149 passed`).

## Entry 040: PDF/TXT Encoding, Roadmap Scaling & Project Context Storage (v1.6.1)
- **Date**: 2026-10-05
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.6.1 Responsive Layout, Extend Fix, Export Shape+Context, Library Placement, Home Linking, PDF+TXT Fixes, Roadmap Scaling

### Design Notes & Architectural Decisions
1. **Extend Blueprint Signature**: Defined `extend_blueprint(old_json, new_requirements, notes)` in `ai_engine.py` incorporating change requirements and notes while preserving confirmed content and schema. Wired Submit Extension in `app.py` to save new versioned row (`v<N+1>`) and open it.
2. **Export Shape & Project Context**: Export rows restructured into 2 columns (`[0.82, 0.18]`) with full-width download button and single `:material/info:` popover. Stored `project_name`, `project_description`, and `target_audience` inside `blueprint_json` at generation and extend. Every export (MD, TXT, HTML, PDF) begins with a Project Context block with robust legacy fallback messaging.
3. **Library Placement & Home Linking**: Removed "Blueprint Library" from sidebar entirely. Rendered full list in Blueprint page main area (`[Open]`, `[Extend]`, `[Delete(confirm)]`, full-width on mobile). Home `[Open]` overwrites DB pointer and session state and lands on Blueprint page; `[View all blueprints]` renders the full list unconditionally.
4. **PDF & TXT Formatting Fixes**: PDF sanitized for unicode (`├─→|-`, `└─→+`, `–—‑→-`, emoji→""), single roadmap numbering, 90-char wrapping, page-break checks before each item, and footer once per page. TXT encoded with UTF-8 BOM (`utf-8-sig`) and ASCII tree (`|- +`).
5. **Engine Roadmap Scaling**: Prompt specifies step count follows complexity (simple 3-4, medium 5-7, complex 8-10; never default to 5). Extend preserves scaling, with zero caps/pads to 5.
6. **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`), comprehensive test suite (`tests/test_v1_6_1.py`), and verified green test suite (`148 passed`).

## Entry 036: Supabase Strips Custom State; Single-Slot Verifier Rationale (v1.5.6)
- **Date**: 2026-10-03
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.5.6 Single-Slot PKCE Verifier

### Design Notes & Architectural Decisions
1. **Supabase Custom State Stripping**: Supabase OAuth `/auth/v1/authorize` endpoint strips or replaces custom `state` parameters passed in the redirect URL when communicating with upstream identity providers (GitHub). Consequently, returning callback requests lack the original client `state` parameter (`state_param` is `None` or arbitrary).
2. **Single-Slot Verifier Architecture**: To handle state stripping while maintaining cryptographic PKCE security, CodeBreaker adopts a single-slot OAuth state strategy. Before rendering the GitHub login link, any existing pending state row (`state='pending'`) in `public.oauth_states` is deleted, and a fresh single slot is inserted with `state='pending'` and the newly generated `code_verifier`. On return callback (`code` present, state optional), the server fetches the latest verifier from `public.oauth_states` where `state='pending'`, ordered by `created_at desc limit 1`. If no pending slot exists, session expiration is reported (`st.error` + stop).
3. **Token Exchange & Fallback**: Issues POST request to `{SUPABASE_URL}/auth/v1/token?grant_type=pkce`. If status 400 is returned, retries once with `grant_type=authorization_code`. On success, sets session, mints `rt`, deletes the pending slot, clears query params, and redirects to Home.
4. **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and verified green test suite (`133 passed`, including pending-slot insert/lookup and code-only return path tests).
5. **Documentation**: CHANGELOG v1.5.6 and DEVLOG Entry 036.

## Entry 035: GitHub Manual PKCE Flow, Auth Mode & Sign-Out Cleanup (v1.5.5)
- **Date**: 2026-10-02
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.5.5 GitHub Manual PKCE Flow, Auth Mode & Sign-Out Cleanup

### Design Notes & Architectural Decisions
1. **Manual Cryptographic PKCE**: Replaced cookie-backed client storage with robust manual PKCE generation (`verifier = secrets.token_urlsafe(43)`, unpadded base64url SHA-256 challenge, `state = secrets.token_urlsafe(16)`). State-verifier pairs are stored in `public.oauth_states`.
2. **Secure Token Exchange & Pruning**: On return callback (`code` + `state`), validates/looks up verifier in `public.oauth_states`, issues a direct `POST` request to `{SUPABASE_URL}/auth/v1/token?grant_type=pkce`, establishes session, mints capability token (`rt`), deletes state row, prunes states older than 10 minutes, and lands on Home.
3. **Auth Mode & Comprehensive Sign-Out**: Query-parameter driven auth mode (`mode=login` vs `mode=signup` with Display Name). Sign-out cleanup explicitly purges all auth query parameters (`rt`, `pg`, `code`, `state`, `type`, `token`, `token_hash`, `error`, `error_description`, `oauth_state`, `mode`, `auth_view`).
4. **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and verified green unit test suite (`130 passed`).
5. **Documentation**: CHANGELOG v1.5.5 and DEVLOG Entry 035.

## Entry 033: Why Verifier Storage is Scoped to PKCE Keys Only (Collateral of the v1.2.0 Purge) (v1.5.3)
- **Date**: 2026-10-02
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.5.3 Restore GitHub OAuth via Scoped PKCE Verifier Storage

### Design Notes & Architectural Decisions
1. **The PKCE Verifier Loss Root Cause**: When CodeBreaker abandoned general client-side session storage in v1.2.3 in favor of URL capability tokens (`?rt=...`), cookie storage utilities were completely purged. However, Supabase OAuth in PKCE flow (`flow_type="pkce"`) generates a cryptographic code verifier prior to redirecting to GitHub and expects the verifier to be stored across the cross-domain redirect in order to exchange the authorization code upon return. Without cookie/storage backing for the PKCE verifier, the redirect cycle broke.
2. **Scoped PKCE Storage (`pkce_storage.py`)**: Restored the minimal pre-v1.2.0 cookie helper using `streamlit-cookies-controller`, implementing a `SyncStorage` subclass (`PkceCookieStorage`).
3. **Strict Scoping (`sb-pkce`)**: Scoped cookie persistence exclusively to keys prefixed `"sb-pkce"` (and code-verifier keys). All user session persistence remains strictly handled server-side via URL capability tokens (`?rt=...`). No auth tokens are cached in cookies.
4. **Runtime Fallback**: If the cookie component is unavailable or encounters an error at runtime, it gracefully falls back to `SyncMemoryStorage` to ensure the auth page never crashes.
5. **Testing & Verification**: Verified via pre-seal compile check (`py_compile`) and full green test suite (including storage round-trip tests).
6. **Documentation**: CHANGELOG v1.5.3 and DEVLOG Entry 033.

## Entry 039: Auth Polish + FAQ Rename + OAuth Visibility (v1.5.1)
- **Date**: 2026-10-02
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.5.1 Auth Polish + FAQ Rename + OAuth Visibility

### Design Notes & Architectural Decisions
1. **Builder Auth Page**: Removed "Account Access" header and "Mode" radio entirely. Mode is now driven directly by landing CTAs (`[Log In]` sets query param `mode=login`, `[Create Account]` sets `mode=signup`), read cleanly by the auth view on load.
2. **Builder Sign Up Button**: Enforced `use_container_width=True` on the Sign Up button so it spans full width matching the GitHub OAuth button.
3. **Builder About FAQ**: Renamed "Mini-FAQ" header to "FAQ".
4. **Builder GitHub OAuth & Redirect Whitelist**: On OAuth exchange failure, displays `st.error` with the actual error message (never silently returning to login). On success, mints `rt`, sets session, and lands on Home. Added code comment detailing Supabase redirect URL whitelist requirements (app domain + `/streamlit` public URL).
5. **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and green test suite (all 126 tests passing).
6. **Documentation**: CHANGELOG v1.5.1 and DEVLOG Entry 039 (plus Entry 032 addendum).

## Entry 032 Addendum: Auth Polish & OAuth Whitelist (v1.5.1)
- Added query-param driven auth mode selection, full-width sign up button, FAQ rename, and explicit GitHub OAuth error surfacing with Supabase redirect URL documentation.

## Entry 038: Blueprint Refresh-Restore + Save Visibility (v1.5.2)
- **Date**: 2026-10-02
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.5.2 Blueprint Refresh-Restore + Save Visibility

### Design Notes & Architectural Decisions
1. **Builder Blueprint Default-Load (Refresh Restore)**: When `active_blueprint_id` is not present in `session_state` (e.g. following a browser reload or refresh), queries the current user's most recent row from `public.blueprints` (`order("created_at", desc=True).limit(1)`) and loads it automatically, ensuring persistence across sessions and reloads. Displays the "generate or open from Home" fallback message strictly when the library is truly empty.
2. **Builder Save Visibility**: Wrapped the auto-save database insert in `try/except` and caught exceptions, surfacing `st.warning(f"Blueprint generated but could not be saved to your library: {e}")` on failure so silent save failures are impossible.
3. **Builder Home List Re-Query**: Ensured `public.blueprints` is re-queried directly on every render of the Home dashboard without stale caching.
4. **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and green test suite (all tests passing, including `test_v1_5_2_requirements` in `tests/test_v1_5_0.py`).
5. **Documentation**: CHANGELOG v1.5.2 and DEVLOG Entry 038 (plus Entry 032 addendum).

## Entry 032 Addendum: Blueprint Persistence Refinements (v1.5.2)
- Added refresh-restore default loading of the most recent blueprint and warning feedback for auto-save failures.

## Entry 037: Persistent Library Architecture (v1.5.0)
- **Date**: 2026-10-01
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.5.0 Persistent Blueprint Library

### Design Notes & Architectural Decisions
1. **Builder Analyze Auto-Save**: On successful `generate_blueprint`, immediately inserts a row into `public.blueprints` (`user_id`, `title` = project name, `blueprint_json` = raw blueprint object), storing the new row's `id` in `st.session_state["active_blueprint_id"]`.
2. **Builder Home Library List**: Replaced session placeholder with a live query to `public.blueprints` for the current user (ordered by `created_at desc`, limit 5). Renders Title, Date, and an `[Open]` button. Clicking `[Open]` sets `active_blueprint_id`, sets `st.query_params["pg"] = "Blueprint"`, and calls `st.rerun()`.
3. **Builder Blueprint DB Rehydration**: On Blueprint page load, if `active_blueprint_id` is set, fetches the row from `public.blueprints`, parses `blueprint_json`, and renders the 5 tabs. Graceful clean fallback message when no active ID and no session blueprint exists.
4. **Database Migration & RLS**: Provided `blueprints_migration.sql` creating `public.blueprints` with Row Level Security (RLS) policies enforcing multi-tenant isolation (`auth.uid() = user_id`).
5. **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and green test suite (`123 passed`, including new unit tests in `tests/test_v1_5_0.py`).
6. **Documentation**: CHANGELOG v1.5.0 and DEVLOG Entry 037.

## Entry 036: Export Redesign, Contact Clear & SMTP Fix (v1.4.5)
- **Date**: 2026-09-28
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.4.5 Export Redesign + Contact Clear + SMTP Fix

### Design Notes & Architectural Decisions
1. **Builder Export Redesign**: Removed export format selectbox, inline purpose labels, top help tooltip, and caption. Rendered four format rows (Markdown / Plain text / HTML / PDF). Each row features two columns: col1 `st.download_button("Export as <Format>")` triggering direct export; col2 `st.popover(":material/info:")` (with `st.expander("ⓘ")` fallback) containing the format's explanation ("what do I do with this file") appearing only when tapped.
2. **Builder Contact Clear & Validation**: On successful contact message send, widget values (`contact_name_input`, `contact_email_input`, `contact_message_input`) are cleared in `session_state` (`""`), keeping the success message.
3. **Builder SMTP Config Check & Send**: Enforced pre-send assertion of `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` present in `st.secrets` or `os.environ`; if any missing, displays `st.error("Contact form unavailable — email service not configured")` and stops. Used `smtplib.SMTP_SSL` for port 465 or `SMTP` for 587 with `starttls()`. Caught `smtplib.SMTPException` specifically, displaying `st.error(f"Email send failed: {e}")` and preserving form inputs on failure. On success, prints `Contact email sent to {to_email}`.
4. **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and verified green test suite (`121 passed`, including new unit tests in `tests/test_v1_4_5.py`).
5. **Documentation**: CHANGELOG v1.4.5, DEVLOG Entry 036 (plus Entry 031 addendum).

## Entry 035: Phase-2 Feedback Round 4 + Hint Elimination (v1.4.4)
- **Date**: 2026-09-27
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.4.4 Phase-2 Feedback Round 4 + Hint Elimination

### Design Notes & Architectural Decisions
1. **Builder Stable Member-Since Field**: Computed formatted member-since (`"%d %b %Y"`, e.g., `"16 Sep 2026"`) once at login, signup, OAuth, and capability resume rehydration paths, storing it as `user["member_since"]`. Dashboard and account tiles read exclusively from this field.
2. **Builder Vertical Folder Structure**: Rendered folder structures via `st.code(tree, language=None)` with `.replace("\\n", "\n")` handling literal escape sequences so folder trees stack vertically.
3. **Builder Inline Export Purposes**: Integrated format purposes inline into export selectbox option labels (`"Markdown (.md) — editable spec for repos & AI assistants"`, `"Plain text (.txt) — universal, opens anywhere"`, `"HTML (.html) — styled page for browser/offline"`, `"PDF (.pdf) — fixed-layout for print & share"`) and removed the separate caption below.
4. **Builder Auth Polish**: Removed email placeholder (`placeholder=""`) and rendered the `"or"` divider as a professional flexbox line-text-line divider (`— or —`).
5. **Builder Danger Buttons & Hint Elimination**: Enforced `use_container_width=True` on all delete/cancel buttons. Added aggressive CSS suppression for `stWidgetTrailer`, `stCharCounter`, widget label trailing hints, and browser `aria-label` trailing hints. Asserted zero `st.form` remain in `app.py`.
6. **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and verified green test suite (`118 passed`, including new unit tests in `tests/test_v1_4_4.py`).
7. **Documentation**: CHANGELOG v1.4.4 and DEVLOG Entry 035 (plus Entry 031 addendum).

## Entry 034: Phase-2 Feedback Round 3 (v1.4.3)
- **Date**: 2026-09-27
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.4.3 Phase-2 Feedback Round 3

### Design Notes & Architectural Decisions
1. **Builder Delete-All Expander Styling**: Wrapped the delete-ALL two-step confirmation inside an `st.expander("Confirm delete all", expanded=True)` when the confirmation flag is active. This leverages the existing expander-scoped red CSS selector (`div[data-testid="stExpander"] div.stButton > button[kind="primary"]`) so the confirm-Delete button renders red (`#d33`) while Cancel stays gray.
2. **Builder Elimination of `st.form`**: Removed the final remaining `st.form` wrapper (Analyze form) and `st.form_submit_button`, replacing them with plain widgets backed by `st.session_state` and explicit `st.button` controls. This completely eliminates the "Press Ctrl+Enter to submit form" hint across every textbox in the application.
3. **Builder Dynamic Export Captions**: Added dynamic `st.caption` hints directly beneath the Export Format selectbox that update in real time based on selection (Markdown: `"editable spec for repos/AI assistants"`; Plain text: `"universal, opens anywhere"`; HTML: `"styled page for browsers/offline"`; PDF: `"fixed-layout for print/share"`).
4. **Builder Clean Member-Since Formatting**: Implemented `format_member_since(created_at_val)` to parse ISO timestamps and date strings safely, stripping time components, microseconds, and UTC offsets to render as clean calendar dates (`"%d %b %Y"`, e.g., `"16 Sep 2026"`), applied uniformly across login, signup, URL-resume rehydration, OAuth, and dashboard tiles.
5. **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and verified green test suite (`111 passed`, including new unit tests in `tests/test_v1_4_3.py`).
6. **Documentation**: CHANGELOG v1.4.3 and DEVLOG Entry 034 (plus Entry 031 addendum).

## Entry 033: Phase-2 Feedback Rounds 1+2 Combined (v1.4.2)
- **Date**: 2026-09-27
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.4.2 Phase-2 Feedback Rounds 1+2 Combined

### Design Notes & Architectural Decisions
1. **Builder Analyze Placeholders & Length Limits**: Restored Analyze form placeholder texts (`"e.g. Chat App"`, `"e.g. Students, Enterprise, Consumers"`, and problem description example prompt) while removing `max_chars` from all Analyze inputs so character counters ("0/200") disappear cleanly while instructional placeholders remain.
2. **Builder Engineering Log Delete Styling**: Injected scoped CSS (`div[data-testid="stExpander"] div.stButton > button[kind="primary"]`) on the Engineering Log page so confirm-Delete renders red (`#d33`) while Cancel buttons remain gray.
3. **Builder Account Member-Since Persistence**: Included `created_at` in the rebuilt user dictionary on the URL-resume refresh path (`?rt=...`), ensuring "Member Since" correctly survives browser refresh and dashboard tiles read it safely.
4. **Builder Log Timestamp Localization**: Converted UTC timestamps to Africa/Lagos local clock time using standard library `zoneinfo.ZoneInfo("Africa/Lagos")` for both expander headers and internal log details.
5. **Builder De-Emoji Professionalism Sweep**: Removed all emoji glyphs from user-facing strings (module cards, sidebar headers, onboarding tour, delete markers, status alerts), replacing them with Streamlit material icons (`:material/analytics:`, `:material/description:`, `:material/journal:`, `:material/shield:`, `:material/terminal:`) and clean plain text.
6. **Builder About Signature**: Updated signature to `"Built by CodeBreaker Dev"` while retaining the functional `[Contact us]` button.
7. **Builder Export Help Tooltips**: Added native hover tooltips (`help=`) to the Export Format selectbox and all four export download buttons, explaining file purpose and browser download destination.
8. **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`) and verified green unit test suite (`106 passed`, including new unit tests in `tests/test_v1_4_2.py`).
9. **Documentation**: CHANGELOG v1.4.2 and DEVLOG Entry 033 (plus Entry 031 addendum).

## Entry 032: Phase-2 Feedback Fixes & Contact Form (v1.4.1)
- **Date**: 2026-09-27
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.4.1 Phase-2 Feedback Fixes & Contact Form

### Design Notes & Architectural Decisions
1. **Builder PDF Unicode Safety (`_latin1_safe`)**: Implemented `_latin1_safe(text)` to map common arrows (`→`, `←`, `↔`), symbols (`•`, quotes, dashes), and emojis to safe ASCII equivalents, followed by `.encode("latin-1","replace").decode("latin-1")`. Wrapped every string passed to FPDF across `render_blueprint_pdf` and footer generation, completely eliminating `FPDFUnicodeEncodingException` vulnerability. Verified via dedicated emoji+arrow unit test.
2. **Builder Log Form & Project Labeling**:
   - Removed `max_chars` from all log text areas.
   - Replaced `st.form` wrappers with plain widgets + `[Submit Log Entry]` button, successfully eliminating the Streamlit Ctrl+Enter submission hint.
   - Added `project_name` field prefilled from the current Analyze project name in `session_state`, editable, defaulting to `"General"`, and stored in database logs.
   - Rendered engineering log entries grouped by project with clean header labels `"[date] Project — milestone"`.
3. **Builder Contact Page**: Added dedicated sidebar navigation section `"Contact"` with a secure contact form (Name, Email, Message with 5 rows height, `[Send Message]` button). Enforced validation (non-empty fields, email regex format), SMTP delivery via Gmail to `codebreakerbuild@gmail.com`, success feedback `"Message sent. We'll respond within 24 hours."`, and strict 60s submission cooldown.
4. **Builder About & Mini-FAQ Accordions**: Refined About page by replacing the old contact clause with `"Built by Martins"` and a `[Contact us]` button setting `st.query_params["pg"]="Contact"` and triggering `st.rerun()`. Converted Mini-FAQ four questions into interactive `st.expander` accordions.
5. **Builder Log Delete Controls**: Refined two-step delete confirmation buttons with `use_container_width=True` and short labels `"Delete"` / `"Cancel"`.
6. **Testing & Verification**: Enforced pre-seal compile check (`python3 -m py_compile`) and verified green test suite (`98 passed`, including `tests/test_v1_4_1.py`).

## Entry 031: Dashboard Contract, Log Control UX & About Six Structure (v1.4.0)
- **Date**: 2026-09-25
- **Author**: Engineering Team / Builder, Tester, Reviewer & Orchestrator Agents
- **Milestone**: v1.4.0 Dashboard, Copy Hygiene, Log Controls & About Six

### Design Notes & Architectural Decisions
1. **Builder Home Dashboard (Authenticated)**: Four tiles in a 2×2 grid layout providing immediate operational overview:
   - (a) **My Blueprints**: Session generation count + "persistent library arrives next update" caption.
   - (b) **My Engineering Logs**: Total log count + three most recent milestone titles fetched securely from Supabase (own rows only).
   - (c) **Quick Start**: Three direct action buttons (Analyze / Blueprint / Engineering Log) updating `st.query_params["pg"]` and triggering `st.rerun()`.
   - (d) **Account**: Display name, email, and member-since date (`created_at`).
   Strict adherence to professional tone with zero version strings and no "AI-driven" phrasing.
2. **Builder Copy Hygiene**: Streamlined form and module interfaces:
   - **Analyze**: Deleted subtitle, all placeholder texts, word-counter hints, and the Skill Level selectbox (defaulting server-side).
   - **Blueprint**: Status line updated to "Generating blueprint…", deleted the "What do I do with this file?" explanatory block while leaving export format boxes untouched.
   - **Engineering Log**: Deleted subtitle and all placeholder/word-counter hints inside textareas.
   - **Banned-Strings Sweep**: Fully enforced across all UI strings and documentation.
3. **Builder Engineering Log Controls**:
   - **Sort Selectbox**: `["Newest first","Oldest first","A→Z (milestone)","Z→A (milestone)"]` default Newest, applied at render.
   - **Two-Step Per-Entry Delete**: First click reveals `[Confirm delete]` + `[Cancel]` via per-entry session state flag; confirm executes deletion, cancel clears.
   - **Delete ALL My Logs**: Separate two-step confirmation button scoping deletion strictly to the authenticated user's own rows.
4. **Builder About Six Additions in Order**:
   (1) "How CodeBreaker protects you" trust section;
   (2) Module guide one-liners;
   (3) Workflow recipe (`Analyze→Blueprint→export→Log→repeat`);
   (4) Mini-FAQ four questions (privacy / forgot password / reload login note / where is my exported file);
   (5) Renamed existing lecturer playbook to "For Lecturers & Supervisors";
   (6) Signature line "Built by Martins — The CodeBreaker Team" + contact placeholder.
5. **Testing & Verification**: Enforced pre-seal compile gate (`py_compile`), zero-network tests, mock supabase dashboard rendering, sort selector reordering, two-step delete verification, and green test suite (`90 passed` including `tests/test_v1_4_0.py`).

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

## Entry 037: OAuth Saga Post-Mortem & Hosting Migration Tuition (v1.5.8)
- **Date**: 2026-10-04
- **Author**: Engineering Team / Builder, Tester & Reviewer Agents
- **Milestone**: v1.5.8 Hardcoded Winning OAuth Exchange & Witness Removal

### OAuth Saga Post-Mortem
1. **Supabase State Stripping**: Supabase `/auth/v1/authorize` strips custom state parameters passed in redirect URLs. Solved via single-slot pending verifier architecture (`public.oauth_states` table with `state='pending'`).
2. **Single-Slot Pending Verifier**: Before rendering the GitHub login link, any existing pending state row is pruned and a single fresh state row is inserted.
3. **GoTrue Token Endpoint Contract**: GoTrue accepts `grant_type=pkce` as a query parameter combined with a JSON request body containing `{"auth_code": code, "code_verifier": verifier}` and header `apikey=ANON`.
4. **Table GRANTs**: Database row-level security and `GRANT SELECT, INSERT, DELETE ON public.oauth_states TO anon, authenticated` are mandatory for public PKCE state storage.
5. **Diagnostics & Witnesses**: Temporary observability tools (`oauth-witness`, `token-witness`, and the 6-variant sweep) successfully diagnosed and isolated the exchange protocol, then were fully purged in v1.5.8.
*This entry is the tuition receipt for the hosting migration.*

## Entry 039: Workspace-vs-Library Model & Extend Versioning (v1.6.0)
- **Date**: 2026-10-04
- **Author**: Engineering Team / Builder, Tester & Reviewer Agents
- **Milestone**: v1.6.0 Library Completeness, Extend Flow, Log Titles, Workspace Freshness & Export Restructure

### Workspace-vs-Library Architecture
1. **Fresh Workspace on Login**: Upon successful login, signup, or OAuth exchange, `profiles.active_blueprint_id` is nulled out so users start with a clean workspace slate ("Open a blueprint from your library or generate a new one.").
2. **Persistent Pointer**: The active blueprint pointer is stored in `profiles.active_blueprint_id` and loaded on Blueprint page navigation. Opening, generating, or extending a blueprint updates the pointer.
3. **Library Completeness**: Full library list on the Blueprint page renders ALL user blueprints (newest first, scrollable) with unique button keys per row (`[Open]`, `[Extend]`, `[Delete(confirm)]`).
4. **Extend Versioning**: `[Extend]` session panel (new changes + optional notes) sends old JSON + context to AI engine, saving the result as a new linked row (`version=N+1`, `parent_id=old_id`) while leaving the parent untouched.
5. **Engineering Log Titles**: Required Milestone title input (max 40 chars) with auto-backfill on read for legacy rows.
6. **Export Restructure**: Markdown/TXT/HTML formatted with consistent section order and unicode trees. PDF formatted with ASCII trees (`|-`, `+`), 90-character line wrapping, and section headers repeated across pages.
