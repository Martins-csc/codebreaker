import streamlit as st

from ai_engine import BlueprintError, generate_blueprint

st.set_page_config(page_title="CodeBreaker", page_icon="⚡", layout="wide")

# Sidebar Navigation
st.sidebar.title("CodeBreaker Navigation")
page = st.sidebar.radio(
    "Navigation", ["Home", "Analyze", "Blueprint", "Engineering Log"]
)

if page == "Home":
    st.title("CodeBreaker")
    st.caption(
        "Deconstruct, Analyze, and Architect Systems with AI-Driven Engineering Insights"
    )
    st.markdown("---")
    st.subheader("Welcome to CodeBreaker v0.2")
    st.write(
        "CodeBreaker is a lightweight, documented, and safe AI-powered code analysis "
        "and system blueprint tool. Use the sidebar to navigate between modules."
    )
elif page == "Analyze":
    st.title("Analyze & Architecture Generation")
    st.write(
        "Fill out the project details below to generate an AI-driven system blueprint."
    )

    with st.form("analyze_form"):
        project_name = st.text_input(
            "Project Name", placeholder="e.g., Real-time Chat App"
        )
        problem = st.text_area(
            "Problem Description / Requirements",
            placeholder="What problem are you solving and what are the core requirements?",
        )
        target_audience = st.text_input(
            "Target Audience", placeholder="e.g., Developers, Enterprise, Consumers"
        )
        skill_level = st.selectbox(
            "Your Skill Level", ["Beginner", "Intermediate", "Advanced", "Expert"]
        )

        submitted = st.form_submit_button("Generate Blueprint")

    if submitted:
        if not project_name.strip() or not problem.strip():
            st.error("Please provide at least a Project Name and Problem Description.")
        else:
            analysis_payload = {
                "project_name": project_name,
                "problem": problem,
                "target_audience": target_audience,
                "skill_level": skill_level,
            }
            with st.spinner(
                "Generating system architecture blueprint via AI Engine..."
            ):
                try:
                    blueprint = generate_blueprint(analysis_payload)
                    st.session_state["blueprint"] = blueprint
                    st.success(
                        "Blueprint generated successfully! Navigate to the 'Blueprint' page to view it."
                    )
                except BlueprintError as e:
                    st.error(f"Blueprint Error: {e}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

elif page == "Blueprint":
    st.title("System Architecture Blueprint")

    blueprint = st.session_state.get("blueprint")
    if not blueprint:
        st.info(
            "No blueprint generated yet. Please submit a project analysis on the 'Analyze' page."
        )
    else:
        st.subheader(
            f"Blueprint for: {blueprint.get('project_name', 'Untitled Project')}"
        )

        tab_tech, tab_folder, tab_edges, tab_roadmap, tab_summary = st.tabs(
            ["Tech Stack", "Folder Structure", "Edge Cases", "Roadmap", "Summary"]
        )

        with tab_tech:
            st.markdown("### Recommended Technology Stack")
            tech_stack = blueprint.get("tech_stack", [])
            if tech_stack:
                for tech in tech_stack:
                    st.markdown(f"- {tech}")
            else:
                st.write("No tech stack specified.")

        with tab_folder:
            st.markdown("### Suggested Folder Structure")
            folder_tree = blueprint.get(
                "folder_structure", "No folder structure provided."
            )
            st.code(folder_tree, language="text")

        with tab_edges:
            st.markdown("### Potential Edge Cases & Risks")
            edge_cases = blueprint.get("edge_cases", [])
            if edge_cases:
                for edge in edge_cases:
                    st.markdown(f"- {edge}")
            else:
                st.write("No edge cases specified.")

        with tab_roadmap:
            st.markdown("### Implementation Roadmap (5 Steps)")
            roadmap = blueprint.get("roadmap", [])
            if roadmap:
                for i, step in enumerate(roadmap, 1):
                    st.markdown(f"**Step {i}:** {step}")
            else:
                st.write("No roadmap specified.")

        with tab_summary:
            st.markdown("### Executive Summary")
            st.write(blueprint.get("summary", "No summary provided."))

elif page == "Engineering Log":
    st.title("Engineering Log")
    st.info(
        "Engineering Log module records technical design decisions, logs, and development milestones."
    )
    st.markdown("---")
    st.subheader("Milestones & Releases")
    st.markdown(
        "- **v0.2.0**: AI Engine integration (Groq & Gemini fallback, requests-only wrapper, structured JSON output, Streamlit UI wiring)."
    )
    st.markdown(
        "- **v0.1.0**: Initial Streamlit framework scaffold and documentation setup."
    )
