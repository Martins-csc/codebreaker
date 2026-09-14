import streamlit as st
from ai_engine import BlueprintError, generate_blueprint
from supabase_client import ConfigError, get_client

st.set_page_config(page_title="CodeBreaker", page_icon="⚡", layout="wide")

# Ensure Supabase client session is restored if access_token is in session_state
try:
    client = get_client()
    if "access_token" in st.session_state and "refresh_token" in st.session_state:
        try:
            client.auth.set_session(
                st.session_state["access_token"], st.session_state["refresh_token"]
            )
        except Exception:
            pass
except ConfigError as ce:
    st.error(f"Configuration Error: {ce}")

# Sidebar Navigation & Auth State
st.sidebar.title("CodeBreaker Navigation")

user = st.session_state.get("user")

if user:
    st.sidebar.success(f"Logged in as: {user.get('display_name') or user.get('email')}")
    if st.sidebar.button("Sign Out"):
        try:
            client.auth.sign_out()
        except Exception:
            pass
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Signed out successfully.")
        st.rerun()

    page = st.sidebar.radio(
        "Navigation", ["Home", "Analyze", "Blueprint", "Engineering Log"]
    )
else:
    page = st.sidebar.radio("Navigation", ["Login", "Home"])

# Auth gate for all modules except Login
if page != "Login" and not user:
    st.warning("Please log in or sign up to access CodeBreaker modules.")
    st.stop()

if page == "Login":
    st.title("CodeBreaker - Authentication")
    st.caption("Secure Access via Supabase Auth & Row Level Security (RLS)")
    st.markdown("---")

    auth_mode = st.radio("Mode", ["Log In", "Sign Up"], horizontal=True)

    if auth_mode == "Sign Up":
        st.subheader("Create a New Account")
        with st.form("signup_form"):
            signup_email = st.text_input("Email", placeholder="you@example.com")
            signup_password = st.text_input(
                "Password", type="password", placeholder="Secure password"
            )
            signup_display_name = st.text_input(
                "Display Name", placeholder="e.g. CodeBreaker Dev"
            )
            signup_submitted = st.form_submit_button("Sign Up")

        if signup_submitted:
            if not signup_email.strip() or not signup_password.strip():
                st.error("Please provide both email and password.")
            else:
                try:
                    client = get_client()
                    res = client.auth.sign_up(
                        {
                            "email": signup_email,
                            "password": signup_password,
                            "options": {"data": {"display_name": signup_display_name}},
                        }
                    )
                    if res.user:
                        if res.session:
                            st.session_state["user"] = {
                                "id": res.user.id,
                                "email": res.user.email,
                                "display_name": signup_display_name,
                            }
                            st.session_state["access_token"] = res.session.access_token
                            st.session_state["refresh_token"] = (
                                res.session.refresh_token
                            )
                            client.auth.set_session(
                                res.session.access_token, res.session.refresh_token
                            )
                            st.success("Account created and logged in successfully!")
                            st.rerun()
                        else:
                            st.success("Account created successfully! Please log in.")
                except Exception as e:
                    err_str = str(e)
                    if (
                        "already registered" in err_str.lower()
                        or "already exists" in err_str.lower()
                    ):
                        st.error(
                            "An account with this email already exists. Please log in."
                        )
                    else:
                        st.error(f"Sign-up failed: {err_str}")

    else:
        st.subheader("Log In to Your Account")
        with st.form("login_form"):
            login_email = st.text_input("Email", placeholder="you@example.com")
            login_password = st.text_input(
                "Password", type="password", placeholder="Your password"
            )
            login_submitted = st.form_submit_button("Log In")

        if login_submitted:
            if not login_email.strip() or not login_password.strip():
                st.error("Please provide both email and password.")
            else:
                try:
                    client = get_client()
                    res = client.auth.sign_in_with_password(
                        {"email": login_email, "password": login_password}
                    )
                    if res.user and res.session:
                        display_name = ""
                        if res.user.user_metadata:
                            display_name = res.user.user_metadata.get(
                                "display_name", ""
                            )
                        st.session_state["user"] = {
                            "id": res.user.id,
                            "email": res.user.email,
                            "display_name": display_name,
                        }
                        st.session_state["access_token"] = res.session.access_token
                        st.session_state["refresh_token"] = res.session.refresh_token
                        client.auth.set_session(
                            res.session.access_token, res.session.refresh_token
                        )
                        st.success("Logged in successfully!")
                        st.rerun()
                except Exception as e:
                    err_str = str(e)
                    if (
                        "invalid" in err_str.lower()
                        or "credentials" in err_str.lower()
                        or "password" in err_str.lower()
                        or "unauthorized" in err_str.lower()
                    ):
                        st.error(
                            "Invalid email or password. Please check your credentials."
                        )
                    else:
                        st.error(f"Login failed: {err_str}")

elif page == "Home":
    st.title("CodeBreaker")
    st.caption(
        "Deconstruct, Analyze, and Architect Systems with AI-Driven Engineering Insights"
    )
    st.markdown("---")
    st.subheader("Welcome to CodeBreaker v0.3")
    st.write(
        "CodeBreaker is a lightweight, documented, and safe AI-powered code analysis, "
        "system blueprint, and engineering log tool backed by Supabase Auth and RLS. "
        "Use the sidebar to navigate between modules."
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
    st.caption(
        "Record technical design decisions, logs, and milestones isolated by user & RLS."
    )
    st.markdown("---")

    # Form to insert an entry for the current user
    st.subheader("New Engineering Log Entry")
    with st.form("engineering_log_form"):
        log_progress = st.text_area(
            "Progress / Milestone", placeholder="What did you accomplish?"
        )
        log_bugs = st.text_area(
            "Bugs / Challenges", placeholder="What issues did you encounter?"
        )
        log_learnings = st.text_area(
            "Learnings / Insights", placeholder="What did you learn?"
        )
        log_submitted = st.form_submit_button("Submit Log Entry")

    if log_submitted:
        if (
            not log_progress.strip()
            and not log_bugs.strip()
            and not log_learnings.strip()
        ):
            st.error("Please fill out at least one field for the log entry.")
        else:
            try:
                client = get_client()
                if "access_token" in st.session_state:
                    client.auth.set_session(
                        st.session_state["access_token"],
                        st.session_state.get("refresh_token", ""),
                    )
                payload = {
                    "user_id": user["id"],
                    "progress": log_progress,
                    "bugs": log_bugs,
                    "learnings": log_learnings,
                }
                client.table("engineering_log").insert(payload).execute()
                st.success("Engineering log entry saved successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to save engineering log: {e}")

    st.markdown("---")
    st.subheader("Your Engineering Log Entries (Newest First)")

    try:
        client = get_client()
        if "access_token" in st.session_state:
            client.auth.set_session(
                st.session_state["access_token"],
                st.session_state.get("refresh_token", ""),
            )
        # Query entries newest first. Isolation relies on RLS (auth.uid() = user_id).
        response = (
            client.table("engineering_log")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        entries = getattr(response, "data", [])
        if entries:
            for entry in entries:
                with st.container():
                    st.markdown(f"**Timestamp:** {entry.get('created_at', 'N/A')}")
                    if entry.get("progress"):
                        st.markdown(f"- **Progress:** {entry.get('progress')}")
                    if entry.get("bugs"):
                        st.markdown(f"- **Bugs:** {entry.get('bugs')}")
                    if entry.get("learnings"):
                        st.markdown(f"- **Learnings:** {entry.get('learnings')}")
                    st.markdown("---")
        else:
            st.info(
                "No engineering log entries found yet. Submit your first entry above."
            )
    except Exception as e:
        st.warning(
            f"Could not load engineering log entries (Table or RLS setup required): {e}"
        )
