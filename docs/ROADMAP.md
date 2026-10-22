# CodeBreaker Roadmap

## Shipping spine (committed)

| Version | Status | Milestone | Key Features |
|---|---|---|---|
| v0.1 | ✅ Completed | Foundation & UI Skeleton | Streamlit scaffold, sidebar pages, docs, security baseline |
| v0.2 | 🔜 Next | AI Engine | Groq (Llama 3) JSON blueprints, provider wrapper with Gemini fallback |
| v0.3 | Planned | Accounts & Data | Supabase auth + Engineering Log storage |
| v0.4 | Planned | Export & Habit | Blueprint → README.md download, Engineering Log UI |
| v0.5 | Planned | Launch | Streamlit Cloud deploy, secrets hardening, final security audit |

## Backlog (v1.x candidates — evaluated, deliberately deferred)


# CodeBreaker Roadmap & Context

## Current Status
- **Phases 1, 2, & 3 (Core Build & Security Audit):** 100% Complete. 
- The app features secure GitHub OAuth (using PKCE and Security Definer RPCs), Row Level Security (RLS) enabled on the database, and a functional UI for Engineering Logs and Blueprint storage.

## The Engine Architecture (How we build)
We use a strict 4-agent loop for all development:
1. **Orchestrator:** Defines mission scope and constraints.
2. **Builder:** Writes minimal diffs, quotes changed lines.
3. **Tester:** Runs `py_compile`, `pytest`, and source-scans.
4. **Reviewer:** Verifies UI/logs and seals with `git push`.

**Golden Rules:**
- **Frozen-Code Rule:** Never rewrite working logic to "make it cleaner."
- **VERIFY-PATH LAW:** Every data flow (Insert -> RPC -> UI) must be traced.
- **No Silent Failures:** Every `except` block must log to `app.errors`.

## Upcoming Phases (What we are doing next)

### Phase 4A: UI/UX Refinement (Completed)
- Cleaned up navigation, added delete confirmations, and sorting to Engineering Logs.

### Phase 4B: The Blueprint Wizard - Input (NEXT TARGET)
- **Objective:** Build the 26-Section Project Blueprint Input form.
- **Reference:** See `docs/CodeBreaker (1) (1).pdf` for the exact 26 sections.
- **Architecture:** Multi-Step Wizard (Option A) using `st.session_state`.
  - Step 1: Foundation (Sections 1-4)
  - Step 2: Mechanics (Sections 5-8)
  - Step 3: Data & Rules (Sections 9-12)
  - Step 4: Tech & Scale (Sections 13-20)
  - Step 5: Scope & Strategy (Sections 21-26)
- **Storage:** Save the completed form as a JSONB object in the `blueprints` table.

### Phase 4C: The AI Generation Engine
- **Objective:** Process the 26 sections into three required outputs (Product, Technical, Implementation Blueprints) using an LLM.
- **Formatting:** Must separate Confirmed Requirements, Recommended Decisions, Assumptions, and Open Questions.

### Phase 4D: Performance & State Management
- Implement `@st.cache_data`, optimize DB queries, and use `st.fragment` to prevent full-page reruns.

### Phase 5: Launch & Scale
- CI/CD pipelines, error tracking, custom domain, and user acquisition.

- AST-based "vibe check" of existing student code (static analysis, security patterns)
- Dependency graph + architecture visualization
- LLM refactoring suggestions + prompt template library
- PDF report export
- Team collaboration features

**Deferral rationale:** the core promise is planning *before* code; shipping to real users beats feature depth pre-launch; every backlog item is stronger with real users feeding it.
