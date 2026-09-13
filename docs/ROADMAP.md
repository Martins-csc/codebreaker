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

- AST-based "vibe check" of existing student code (static analysis, security patterns)
- Dependency graph + architecture visualization
- LLM refactoring suggestions + prompt template library
- PDF report export
- Team collaboration features

**Deferral rationale:** the core promise is planning *before* code; shipping to real users beats feature depth pre-launch; every backlog item is stronger with real users feeding it.
