import hashlib
import json
import secrets
import time
from datetime import datetime, timedelta, timezone

import streamlit as st
from ai_engine import (BlueprintError, generate_blueprint,
                       render_blueprint_html, render_blueprint_markdown,
                       render_blueprint_pdf, render_blueprint_text,
                       sanitize_filename)
from config import ADMIN_EMAIL
from security import validate_email, validate_input_length, validate_password
from supabase_client import ConfigError, get_client

st.set_page_config(page_title="CodeBreaker", page_icon="⚡", layout="wide")


def handle_storage_error(e):
    err_msg = f"{type(e).__name__}: {str(e)[:80]}"
    st.session_state["persist_debug"] = err_msg


def mint_and_set_rt(client, user_id, refresh_token):
    try:
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        client.rpc(
            "create_resume_token",
            {
                "p_uid": user_id,
                "p_refresh_token": refresh_token,
                "p_token_hash": token_hash,
                "p_expires_at": expires_at.isoformat(),
            },
        ).execute()
        st.query_params["rt"] = token
    except Exception as e:
        handle_storage_error(e)


if "render_count" not in st.session_state:
    st.session_state["render_count"] = 0
st.session_state["render_count"] += 1

# Boot session rehydration via URL capability token (?rt=...)
if "user" not in st.session_state or "access_token" not in st.session_state:
    try:
        client = get_client()
        rt_param = st.query_params.get("rt")
        if isinstance(rt_param, list):
            rt_param = rt_param[0] if rt_param else None

        if rt_param:
            token_hash = hashlib.sha256(rt_param.encode("utf-8")).hexdigest()
            try:
                verify_res = client.rpc(
                    "verify_resume_token", {"p_token_hash": token_hash}
                ).execute()
                verify_data = getattr(verify_res, "data", [])
            except Exception:
                verify_data = []

            v_len = len(verify_data)
            if verify_data and v_len > 0:
                row = verify_data[0] if isinstance(verify_data, list) else verify_data
                r_keys = sorted(list(row.keys()))
                refresh_token = row.get("refresh_token")
                user_id = row.get("user_id")
                has_rt = bool(refresh_token)
                st.session_state["boot_debug"] = (
                    f"len={v_len}, keys={r_keys}, has_rt={has_rt}"
                )
                if refresh_token:
                    restored = False
                    try:
                        refresh_res = client.auth.refresh_session(refresh_token)
                        if refresh_res and refresh_res.session:
                            new_sess = refresh_res.session
                            client.auth.set_session(
                                new_sess.access_token, new_sess.refresh_token
                            )
                            user_obj = getattr(refresh_res, "user", None)
                            if not user_obj:
                                user_res = client.auth.get_user(new_sess.access_token)
                                user_obj = (
                                    getattr(user_res, "user", None)
                                    if user_res
                                    else None
                                )

                            if user_obj:
                                display_name = ""
                                if user_obj.user_metadata:
                                    display_name = (
                                        user_obj.user_metadata.get("display_name", "")
                                        or user_obj.email.split("@")[0]
                                    )
                                elif user_obj.email:
                                    display_name = user_obj.email.split("@")[0]
                                user_metadata = (
                                    getattr(user_obj, "user_metadata", {}) or {}
                                )
                                st.session_state["user"] = {
                                    "id": user_obj.id,
                                    "email": user_obj.email,
                                    "display_name": display_name,
                                    "user_metadata": user_metadata,
                                }
                                st.session_state["access_token"] = new_sess.access_token
                                st.session_state["refresh_token"] = (
                                    new_sess.refresh_token
                                )
                                st.session_state["expires_at"] = getattr(
                                    new_sess, "expires_at", time.time() + 3600
                                )
                                st.session_state["last_verify_result"] = (
                                    "Verified & Rotated ✅"
                                )
                                restored = True

                                # Rotate token on each successful boot
                                try:
                                    client.rpc(
                                        "revoke_resume_token",
                                        {
                                            "p_token_hash": token_hash,
                                            "p_uid": user_obj.id,
                                        },
                                    ).execute()
                                except Exception:
                                    try:
                                        client.rpc(
                                            "revoke_resume_token",
                                            {"p_token_hash": token_hash},
                                        ).execute()
                                    except Exception:
                                        pass

                                new_token = secrets.token_urlsafe(32)
                                new_hash = hashlib.sha256(
                                    new_token.encode("utf-8")
                                ).hexdigest()
                                new_expires = datetime.now(timezone.utc) + timedelta(
                                    days=7
                                )
                                try:
                                    client.rpc(
                                        "create_resume_token",
                                        {
                                            "p_uid": user_obj.id,
                                            "p_refresh_token": new_sess.refresh_token,
                                            "p_token_hash": new_hash,
                                            "p_expires_at": new_expires.isoformat(),
                                        },
                                    ).execute()
                                except Exception:
                                    pass
                                st.query_params["rt"] = new_token
                    except Exception as e:
                        ex_msg = repr(e)[:200]
                        st.session_state["boot_debug"] = (
                            f"len={v_len}, keys={r_keys}, has_rt={has_rt}, ex={ex_msg}"
                        )
                        restored = False

                    if restored:
                        st.session_state["boot_debug"] = (
                            f"len={v_len}, keys={r_keys}, has_rt={has_rt}, restored=True"
                        )
                    else:
                        if "ex=" not in st.session_state["boot_debug"]:
                            st.session_state["boot_debug"] = (
                                f"len={v_len}, keys={r_keys}, has_rt={has_rt}"
                            )
                        st.session_state["boot_debug"] += ", restored=False"
                        st.session_state["last_verify_result"] = "Refresh failed"
                        if "rt" in st.query_params:
                            del st.query_params["rt"]
                else:
                    st.session_state["boot_debug"] = (
                        f"len={v_len}, keys={r_keys}, has_rt={has_rt}, restored=False"
                    )
                    st.session_state["last_verify_result"] = (
                        "No refresh token in record"
                    )
                    if "rt" in st.query_params:
                        del st.query_params["rt"]
            else:
                st.session_state["boot_debug"] = f"len={v_len}, restored=False"
                st.session_state["last_verify_result"] = "Token not found or expired"
                if "rt" in st.query_params:
                    del st.query_params["rt"]
        else:
            st.session_state["boot_debug"] = "None"
            st.session_state["last_verify_result"] = "None"
    except Exception as e:
        handle_storage_error(e)
        st.session_state["boot_debug"] = f"exception={repr(e)[:200]}"
        if "rt" in st.query_params:
            del st.query_params["rt"]

# Ensure client session is restored if access_token is in session_state
try:
    client = get_client()

    # Check query parameters on page load for email verification (signup/recovery) or OAuth authorization code
    type_param = st.query_params.get("type")
    token_param = (
        st.query_params.get("token")
        or st.query_params.get("token_hash")
        or st.query_params.get("code")
    )
    code_param = st.query_params.get("code")

    if isinstance(type_param, list):
        type_param = type_param[0] if type_param else None
    if isinstance(token_param, list):
        token_param = token_param[0] if token_param else None
    if isinstance(code_param, list):
        code_param = code_param[0] if code_param else None

    # 1. Handle email link ownership verification (signup or recovery) via verify_otp
    if type_param in ["signup", "recovery"] and (token_param or code_param):
        otp_token = token_param or code_param
        verified = False
        res = None
        # Try token_hash= first, fall back to sha256-hex of token as token_hash, then token=
        try:
            res = client.auth.verify_otp({"token_hash": otp_token, "type": type_param})
            verified = True
        except Exception:
            try:
                import hashlib

                token_hash_sha256 = hashlib.sha256(
                    otp_token.encode("utf-8")
                ).hexdigest()
                res = client.auth.verify_otp(
                    {"token_hash": token_hash_sha256, "type": type_param}
                )
                verified = True
            except Exception:
                try:
                    res = client.auth.verify_otp(
                        {"token": otp_token, "type": type_param}
                    )
                    verified = True
                except Exception:
                    verified = False

        if verified and res:
            if type_param == "recovery":
                st.session_state["recovery_mode"] = True
                if res.session:
                    st.session_state["access_token"] = res.session.access_token
                    st.session_state["refresh_token"] = res.session.refresh_token
                    st.session_state["expires_at"] = getattr(
                        res.session, "expires_at", time.time() + 3600
                    )
                st.success(
                    "Recovery session established. Please set your new password."
                )
            elif type_param == "signup":
                st.success("Email confirmed ✅ — please log in")
                st.session_state["email_confirmed_success"] = True
        else:
            st.warning("This link has expired or is invalid. Please request a new one.")
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                if st.button("Resend confirmation email"):
                    st.session_state["show_resend_link"] = True
            with col_res2:
                if st.button("Forgot password?"):
                    st.session_state["show_forgot_password"] = True

        st.query_params.clear()
        st.rerun()

    # 2. Handle GitHub OAuth authorization code exchange (old recovery detection deleted)
    elif code_param:
        code = code_param
        try:
            try:
                res = client.auth.exchange_code_for_session(code)
            except Exception:
                res = client.auth.exchange_code_for_session({"auth_code": code})

            if res and res.session:
                client.auth.set_session(
                    res.session.access_token, res.session.refresh_token
                )
                if res.user:
                    display_name = ""
                    if res.user.user_metadata:
                        display_name = (
                            res.user.user_metadata.get("display_name", "")
                            or res.user.email.split("@")[0]
                        )
                    elif res.user.email:
                        display_name = res.user.email.split("@")[0]
                    user_metadata = getattr(res.user, "user_metadata", {}) or {}
                    u_created = getattr(
                        res.user, "created_at", None
                    ) or user_metadata.get("created_at", "")
                    c_display = (
                        u_created.split("T")[0]
                        if u_created and "T" in str(u_created)
                        else (str(u_created) if u_created else "N/A")
                    )
                    st.session_state["user"] = {
                        "id": res.user.id,
                        "email": res.user.email,
                        "display_name": display_name,
                        "user_metadata": user_metadata,
                        "created_at": c_display,
                    }
                    st.session_state["access_token"] = res.session.access_token
                    st.session_state["refresh_token"] = res.session.refresh_token
                    expires_at = getattr(res.session, "expires_at", time.time() + 3600)
                    st.session_state["expires_at"] = expires_at
                    mint_and_set_rt(client, res.user.id, res.session.refresh_token)
                    st.success("Successfully logged in with GitHub!")
        except Exception as e:
            st.error(f"GitHub OAuth authentication failed: {e}")
        finally:
            st.query_params.clear()
            st.rerun()

    if "access_token" in st.session_state and "refresh_token" in st.session_state:
        try:
            client.auth.set_session(
                st.session_state["access_token"], st.session_state["refresh_token"]
            )
        except Exception:
            pass
except ConfigError as ce:
    st.error(f"Configuration Error: {ce}")

user = st.session_state.get("user")
if not user:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.get("auth_view"):
        if st.button("← Back to overview", key="auth_back_to_overview"):
            del st.session_state["auth_view"]
            st.rerun()

        st.markdown("---")
        with st.container():
            st.subheader("Account Access")
            auth_mode = st.radio(
                "Mode", ["Log In", "Sign Up"], horizontal=True, key="auth_card_mode"
            )

            st.markdown(
                """
                <style>
                .stForm [data-testid="InputInstructions"], div[data-baseweb="input"] + div {
                    display: none !important;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            auth_email = st.text_input(
                "Email", placeholder="you@example.com", key="auth_card_email"
            )
            auth_password = st.text_input(
                "Password", type="password", placeholder="", key="auth_card_password"
            )

            auth_display_name = ""
            if auth_mode == "Sign Up":
                auth_display_name = st.text_input(
                    "Display Name", placeholder="", key="auth_card_display_name"
                )

            col_b1, col_b2 = st.columns(2)
            if auth_mode == "Log In":
                with col_b1:
                    login_submitted = st.button(
                        "Log In",
                        type="primary",
                        use_container_width=True,
                        key="card_login_btn",
                    )
                with col_b2:
                    forgot_submitted = st.button(
                        "Forgot Password",
                        use_container_width=True,
                        key="card_forgot_btn",
                    )
                signup_submitted = False
            else:
                login_submitted = False
                forgot_submitted = False
                with col_b1:
                    signup_submitted = st.button(
                        "Sign Up",
                        type="primary",
                        use_container_width=True,
                        key="card_signup_btn",
                    )

            if login_submitted:
                if not auth_email.strip():
                    st.error("Email cannot be empty.")
                elif not auth_password.strip():
                    st.error("Password cannot be empty.")
                else:
                    email_format_valid, email_format_err = validate_email(
                        auth_email.strip()
                    )
                    if not email_format_valid:
                        st.error(email_format_err)
                    else:
                        try:
                            client = get_client()
                            res = client.auth.sign_in_with_password(
                                {
                                    "email": auth_email.strip(),
                                    "password": auth_password.strip(),
                                }
                            )
                            user_obj = getattr(res, "user", None)
                            session_obj = getattr(res, "session", None)

                            if user_obj and (
                                getattr(user_obj, "confirmed_at", None) is None
                                or not session_obj
                            ):
                                st.info("Check your email to confirm your account")
                                st.session_state["unconfirmed_email"] = (
                                    auth_email.strip()
                                )
                                st.error(
                                    "Email not confirmed. Please check your email to confirm your account."
                                )
                            elif user_obj and session_obj:
                                display_name = ""
                                if user_obj.user_metadata:
                                    display_name = user_obj.user_metadata.get(
                                        "display_name", ""
                                    )
                                user_metadata = (
                                    getattr(user_obj, "user_metadata", {}) or {}
                                )
                                u_created = getattr(
                                    user_obj, "created_at", None
                                ) or user_metadata.get("created_at", "")
                                c_display = (
                                    u_created.split("T")[0]
                                    if u_created and "T" in str(u_created)
                                    else (str(u_created) if u_created else "N/A")
                                )
                                st.session_state["user"] = {
                                    "id": user_obj.id,
                                    "email": user_obj.email,
                                    "display_name": display_name,
                                    "user_metadata": user_metadata,
                                    "created_at": c_display,
                                }
                                st.session_state["access_token"] = (
                                    res.session.access_token
                                )
                                st.session_state["refresh_token"] = (
                                    res.session.refresh_token
                                )
                                st.session_state["expires_at"] = getattr(
                                    res.session, "expires_at", time.time() + 3600
                                )
                                client.auth.set_session(
                                    res.session.access_token, res.session.refresh_token
                                )
                                mint_and_set_rt(
                                    client, user_obj.id, res.session.refresh_token
                                )
                                st.success("Logged in successfully!")
                                del st.session_state["auth_view"]
                                st.rerun()
                        except Exception as e:
                            err_str = str(e)
                            if "not confirmed" in err_str.lower():
                                st.info("Check your email to confirm your account")
                                st.error(
                                    "Email not confirmed. Please check your email to confirm your account."
                                )
                            elif (
                                "invalid" in err_str.lower()
                                or "credentials" in err_str.lower()
                            ):
                                st.error(
                                    "Invalid email or password. Please check your credentials."
                                )
                            else:
                                st.error(f"Login failed: {err_str}")

            elif forgot_submitted:
                if not auth_email.strip():
                    st.error("Email cannot be empty.")
                else:
                    email_valid, email_err = validate_email(auth_email.strip())
                    if not email_valid:
                        st.error(email_err)
                    else:
                        try:
                            client = get_client()
                            redirect_to = getattr(st.context, "url", None)
                            if redirect_to:
                                redirect_to = redirect_to.split("?")[0]
                            else:
                                redirect_to = "http://localhost:8501"

                            client.auth.reset_password_for_email(
                                auth_email.strip(),
                                options={"redirect_to": redirect_to},
                            )
                        except Exception:
                            pass

                        st.info(
                            "If an account exists for that email, a reset link is on its way."
                        )

            elif signup_submitted:
                if not auth_email.strip():
                    st.error("Email cannot be empty.")
                elif not auth_password.strip():
                    st.error("Password cannot be empty.")
                else:
                    email_format_valid, email_format_err = validate_email(
                        auth_email.strip()
                    )
                    email_len_valid, email_len_err = validate_input_length(
                        "email", auth_email.strip()
                    )
                    pwd_valid, pwd_err = validate_password(auth_password)
                    name_valid, name_err = validate_input_length(
                        "display_name", auth_display_name.strip()
                    )

                    if not email_len_valid:
                        st.error(email_len_err)
                    elif not email_format_valid:
                        st.error(email_format_err)
                    elif not pwd_valid:
                        st.error(pwd_err)
                    elif not name_valid:
                        st.error(name_err)
                    else:
                        try:
                            client = get_client()
                            res = client.auth.sign_up(
                                {
                                    "email": auth_email.strip(),
                                    "password": auth_password.strip(),
                                    "options": {
                                        "data": {
                                            "display_name": auth_display_name.strip()
                                        }
                                    },
                                }
                            )
                            user_obj = getattr(res, "user", None)
                            session_obj = getattr(res, "session", None)

                            if user_obj:
                                identities = getattr(user_obj, "identities", None)
                                confirmed_at = getattr(user_obj, "confirmed_at", None)

                                if identities is not None and len(identities) == 0:
                                    st.warning(
                                        "This email is already linked to an account. Please log in or reset your password."
                                    )
                                elif (
                                    not identities
                                    or confirmed_at is None
                                    or not session_obj
                                ):
                                    st.info("Check your email to confirm your account")
                                    st.success(
                                        f"Confirmation email sent to {auth_email.strip()}. Check your inbox."
                                    )
                                else:
                                    display_name = (
                                        auth_display_name.strip()
                                        or auth_email.strip().split("@")[0]
                                    )
                                    user_metadata = (
                                        getattr(user_obj, "user_metadata", {}) or {}
                                    )
                                    u_created = getattr(
                                        user_obj, "created_at", None
                                    ) or user_metadata.get("created_at", "")
                                    c_display = (
                                        u_created.split("T")[0]
                                        if u_created and "T" in str(u_created)
                                        else (str(u_created) if u_created else "N/A")
                                    )
                                    st.session_state["user"] = {
                                        "id": user_obj.id,
                                        "email": user_obj.email,
                                        "display_name": display_name,
                                        "user_metadata": user_metadata,
                                        "created_at": c_display,
                                    }
                                    st.session_state["access_token"] = (
                                        session_obj.access_token
                                    )
                                    st.session_state["refresh_token"] = (
                                        session_obj.refresh_token
                                    )
                                    st.session_state["expires_at"] = getattr(
                                        session_obj, "expires_at", time.time() + 3600
                                    )
                                    client.auth.set_session(
                                        session_obj.access_token,
                                        session_obj.refresh_token,
                                    )
                                    mint_and_set_rt(
                                        client, user_obj.id, session_obj.refresh_token
                                    )
                                    st.success(
                                        "Account created and logged in successfully!"
                                    )
                                    del st.session_state["auth_view"]
                                    st.rerun()
                        except Exception as e:
                            err_str = str(e)
                            if (
                                "already registered" in err_str.lower()
                                or "already exists" in err_str.lower()
                            ):
                                st.warning(
                                    "This email is already linked to an account. Please log in or reset your password."
                                )
                            else:
                                st.error(f"Sign-up failed: {err_str}")

            st.markdown("or")

            redirect_to = getattr(st.context, "url", None)
            if redirect_to:
                redirect_to = redirect_to.split("?")[0]
            else:
                redirect_to = "http://localhost:8501"

            try:
                client = get_client()
                try:
                    oauth_res = client.auth.sign_in_with_oauth(
                        {"provider": "github", "options": {"redirect_to": redirect_to}}
                    )
                except TypeError:
                    oauth_res = client.auth.sign_in_with_oauth(
                        provider="github", options={"redirect_to": redirect_to}
                    )

                oauth_url = getattr(oauth_res, "url", None)
                if not oauth_url and isinstance(oauth_res, dict):
                    oauth_url = oauth_res.get("url")

                if oauth_url:
                    st.link_button(
                        "Continue with GitHub",
                        oauth_url,
                        use_container_width=True,
                        key="card_github_link_btn",
                    )
            except Exception as e:
                st.error(f"Could not generate GitHub OAuth link: {e}")
    else:
        st.title("Deconstruct, Analyze, and Architect Systems")
        st.write(
            "CodeBreaker is a streamlined engineering workspace designed to help developers plan, "
            "structure, and document robust software systems before writing code. Transform complex "
            "project requirements into clean architecture blueprints, structured documentation, and "
            "reliable engineering logs."
        )
        st.markdown("---")

        st.subheader("How It Works")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.markdown(
                "**1. Analyze**\n\nDefine project specifications and core requirements."
            )
        with col_s2:
            st.markdown(
                "**2. Blueprint**\n\nGenerate comprehensive architecture specs and roadmaps."
            )
        with col_s3:
            st.markdown(
                "**3. Engineering Log**\n\nTrack progress, milestones, and daily insights."
            )

        st.markdown("---")
        st.subheader("Workspace Modules")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.info(
                "🔍 **Analyze**\n\nTransform project requirements into structured technical specs."
            )
        with col_m2:
            st.info(
                "📐 **Blueprint**\n\nExplore multi-tab system architecture, tech stacks, and exportable documentation."
            )
        with col_m3:
            st.info(
                "📝 **Engineering Log**\n\nMaintain a secure, chronological record of daily progress and technical insights."
            )

        st.markdown("---")
        col_cta1, col_cta2 = st.columns(2)
        with col_cta1:
            if st.button(
                "Log In",
                type="primary",
                use_container_width=True,
                key="landing_login_cta",
            ):
                st.session_state["auth_view"] = "login"
                st.rerun()
        with col_cta2:
            if st.button(
                "Create Account", use_container_width=True, key="landing_signup_cta"
            ):
                st.session_state["auth_view"] = "signup"
                st.rerun()

    st.stop()
else:
    # Authenticated sidebar contract:
    # 1. Admin Pulse (admin only)
    # 2. section radios with NO "Navigation" caption
    # 3. Persistence Debug (admin only)
    # 4. Sign Out LAST
    user_email = user.get("email", "") if user else ""
    is_admin = (
        bool(ADMIN_EMAIL)
        and bool(user_email)
        and ADMIN_EMAIL.strip().lower() == user_email.strip().lower()
    )

    if is_admin:
        st.sidebar.subheader("🛡️ Admin Pulse")
        try:
            client = get_client()
            if "access_token" in st.session_state:
                client.auth.set_session(
                    st.session_state["access_token"],
                    st.session_state.get("refresh_token", ""),
                )
            res_users = client.rpc("count_registered_users").execute()
            users_count = getattr(res_users, "data", 0)

            res_logs = client.rpc("count_engineering_logs").execute()
            logs_count = getattr(res_logs, "data", 0)

            st.sidebar.metric("Registered Users", users_count)
            st.sidebar.metric("Engineering Logs", logs_count)
        except Exception as e:
            st.sidebar.warning(f"Could not load Admin Pulse: {e}")
        st.sidebar.markdown("---")

    options = ["Home", "Analyze", "Blueprint", "Engineering Log", "About"]
    _pg = st.query_params.get("pg")
    if isinstance(_pg, list):
        _pg = _pg[0] if _pg else None
    default_index = options.index(_pg) if _pg in options else 0
    page = st.sidebar.radio(
        "", options, index=default_index, label_visibility="collapsed"
    )
    if page != _pg:
        st.query_params["pg"] = page

    if is_admin:
        st.sidebar.markdown("---")
        with st.sidebar.expander(
            "Persistence Debug", expanded=False, key="persistence_debug_expander"
        ):
            rt_present = bool(st.query_params.get("rt"))
            last_verify = st.session_state.get("last_verify_result", "None")
            gate_flags = f"user={bool(user)}, access_token={bool(st.session_state.get('access_token'))}, refresh_token={bool(st.session_state.get('refresh_token'))}"

            st.write(f"**RT Present**: {rt_present}")
            st.write(f"**Last Verify Result**: {last_verify}")
            st.write(f"**Gate Flags**: {gate_flags}")

    st.sidebar.markdown("---")
    if st.sidebar.button("Sign Out", key="sidebar_sign_out_btn"):
        try:
            rt_param = st.query_params.get("rt")
            if isinstance(rt_param, list):
                rt_param = rt_param[0] if rt_param else None
            if rt_param:
                token_hash = hashlib.sha256(rt_param.encode("utf-8")).hexdigest()
                client.rpc(
                    "revoke_resume_token", {"p_token_hash": token_hash}
                ).execute()
        except Exception:
            pass
        try:
            client.auth.sign_out()
        except Exception:
            pass
        if "rt" in st.query_params:
            del st.query_params["rt"]
        if "pg" in st.query_params:
            del st.query_params["pg"]
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Signed out successfully.")
        st.rerun()

# First-run onboarding tour for authenticated sessions
user_meta = user.get("user_metadata", {}) if user else {}
if user and not user_meta.get("tour_seen", False):
    with st.expander(
        "👋 Welcome to CodeBreaker — First-Run Onboarding Tour", expanded=True
    ):
        st.markdown(
            "1. **Analyze**: Describe any project idea to generate an automated blueprint.\n"
            "2. **Blueprint**: Explore the 5 tabs and export your spec in 4 formats.\n"
            "3. **Engineering Log**: Record progress, bugs, and learnings."
        )
        if st.button("Got it", key="tour_got_it_btn"):
            try:
                client = get_client()
                if "access_token" in st.session_state:
                    client.auth.set_session(
                        st.session_state["access_token"],
                        st.session_state.get("refresh_token", ""),
                    )
                client.auth.update_user({"data": {"tour_seen": True}})
            except Exception:
                pass
            user_meta["tour_seen"] = True
            st.session_state["user"]["user_metadata"] = user_meta
            st.rerun()

if page == "About":
    st.title("About CodeBreaker")
    st.markdown("---")

    st.subheader("How CodeBreaker protects you")
    st.write(
        "Your project data and engineering logs are securely isolated to your account using robust authorization and access controls. "
        "No other user can access your private blueprints or logs."
    )

    st.subheader("Module Guide")
    st.markdown(
        "- **Analyze**: Define system requirements and project specifications.\n"
        "- **Blueprint**: Generate and export architecture roadmaps in multiple formats.\n"
        "- **Engineering Log**: Maintain a secure chronological record of progress and milestones."
    )

    st.subheader("Workflow Recipe")
    st.write("Analyze→Blueprint→export→Log→repeat")

    st.subheader("Mini-FAQ")
    st.markdown(
        "1. **Privacy**: Are my logs private? Yes, strictly isolated to your authenticated account.\n"
        "2. **Forgot Password**: How do I reset my password? Use the password reset link on the login screen.\n"
        "3. **Reload Login Note**: Do I stay logged in across reloads? Yes, via secure session tokens.\n"
        "4. **Where is my exported file**: Where do exports go? Straight to your browser's default download location."
    )

    st.subheader("For Lecturers & Supervisors")
    st.write(
        "Computer science and software engineering professors use CodeBreaker as a core instructional tool in class. "
        "A typical semester assignment formula is:\n\n"
        "$$\\text{Assignment Grade} = \\text{System Blueprint} + \\text{Engineering Log}$$ \n\n"
        "- **System Blueprint**: Students submit their initial architecture analysis (Tech Stack, Folder Structure, Edge Cases, Roadmap) exported as Markdown, HTML, or PDF.\n"
        "- **Engineering Log**: Students maintain an ongoing log of daily progress, encountered bugs, and technical insights, securely isolated by user accounts."
    )

    st.markdown("---")
    st.markdown(
        "Built by Martins — The CodeBreaker Team • Contact: support@codebreaker.dev"
    )

elif page == "Home":
    st.title("Dashboard")
    st.markdown("---")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        with st.container(border=True):
            st.subheader("My Blueprints")
            bp_count = st.session_state.get(
                "blueprint_count", 1 if st.session_state.get("blueprint") else 0
            )
            st.metric("Generated This Session", bp_count)
            st.caption("persistent library arrives next update")

    with col_t2:
        with st.container(border=True):
            st.subheader("My Engineering Logs")
            try:
                client = get_client()
                if "access_token" in st.session_state:
                    client.auth.set_session(
                        st.session_state["access_token"],
                        st.session_state.get("refresh_token", ""),
                    )
                res_logs = (
                    client.table("engineering_log")
                    .select("progress, created_at")
                    .eq("user_id", user["id"])
                    .order("created_at", desc=True)
                    .execute()
                )
                log_rows = getattr(res_logs, "data", [])
                log_count = len(log_rows)
                st.metric("Total Logs", log_count)
                st.markdown("**Recent Milestones:**")
                if log_rows:
                    for row in log_rows[:3]:
                        prog = row.get("progress", "Milestone")
                        preview = prog.split("\n")[0][:40] if prog else "Milestone"
                        st.markdown(f"- {preview}")
                else:
                    st.write("No logs recorded yet.")
            except Exception:
                st.metric("Total Logs", 0)
                st.write("No logs recorded yet.")

    col_t3, col_t4 = st.columns(2)
    with col_t3:
        with st.container(border=True):
            st.subheader("Quick Start")
            qs_c1, qs_c2, qs_c3 = st.columns(3)
            with qs_c1:
                if st.button("Analyze", use_container_width=True, key="qs_analyze"):
                    st.query_params["pg"] = "Analyze"
                    st.rerun()
            with qs_c2:
                if st.button("Blueprint", use_container_width=True, key="qs_blueprint"):
                    st.query_params["pg"] = "Blueprint"
                    st.rerun()
            with qs_c3:
                if st.button("Engineering Log", use_container_width=True, key="qs_log"):
                    st.query_params["pg"] = "Engineering Log"
                    st.rerun()

    with col_t4:
        with st.container(border=True):
            st.subheader("Account")
            st.markdown(f"**Display Name:** {user.get('display_name', 'N/A')}")
            st.markdown(f"**Email:** {user.get('email', 'N/A')}")
            st.markdown(f"**Member Since:** {user.get('created_at', 'N/A')}")

elif page == "Analyze":
    st.title("Analyze & Architecture Generation")

    with st.form("analyze_form"):
        project_name = st.text_input("Project Name", max_chars=100)
        problem = st.text_area("Problem Description / Requirements", max_chars=2000)
        target_audience = st.text_input("Target Audience", max_chars=200)

        submitted = st.form_submit_button("Generate Blueprint")

    if submitted:
        pn_valid, pn_err = validate_input_length("project_name", project_name)
        prob_valid, prob_err = validate_input_length("problem", problem)
        ta_valid, ta_err = validate_input_length("target_audience", target_audience)

        if not pn_valid or not prob_valid or not ta_valid:
            st.error("Input exceeds maximum allowed length. Please shorten your input.")
        elif not project_name.strip() or not problem.strip():
            st.error("Please provide at least a Project Name and Problem Description.")
        else:
            analysis_payload = {
                "project_name": project_name,
                "problem": problem,
                "target_audience": target_audience,
                "skill_level": "Intermediate",
            }
            with st.spinner("Generating blueprint…"):
                try:
                    blueprint = generate_blueprint(analysis_payload)
                    st.session_state["blueprint"] = blueprint
                    st.session_state["blueprint_count"] = (
                        st.session_state.get("blueprint_count", 0) + 1
                    )
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
        col_title, col_export = st.columns([2, 2])
        with col_title:
            st.subheader(
                f"Blueprint for: {blueprint.get('project_name', 'Untitled Project')}"
            )
        with col_export:
            export_format = st.selectbox(
                "Export Format",
                ["Markdown (.md)", "Plain text (.txt)", "HTML (.html)", "PDF (.pdf)"],
                key="blueprint_export_format",
            )
            base_fname = sanitize_filename(blueprint.get("project_name", "blueprint"))
            if base_fname.endswith(".md"):
                txt_fname = base_fname[:-3] + ".txt"
                html_fname = base_fname[:-3] + ".html"
                pdf_fname = base_fname[:-3] + ".pdf"
            else:
                txt_fname = base_fname + ".txt"
                html_fname = base_fname + ".html"
                pdf_fname = base_fname + ".pdf"

            if "Markdown" in export_format:
                content = render_blueprint_markdown(blueprint)
                fname = base_fname
                mime = "text/markdown"
                btn_label = "📥 Export as Markdown (.md)"
            elif "Plain text" in export_format:
                content = render_blueprint_text(blueprint)
                fname = txt_fname
                mime = "text/plain"
                btn_label = "📥 Export as Plain Text (.txt)"
            elif "HTML" in export_format:
                content = render_blueprint_html(blueprint)
                fname = html_fname
                mime = "text/html"
                btn_label = "📥 Export as HTML (.html)"
            else:
                content = render_blueprint_pdf(blueprint)
                fname = pdf_fname
                mime = "application/pdf"
                btn_label = "📥 Export as PDF (.pdf)"

            st.download_button(
                label=btn_label,
                data=content,
                file_name=fname,
                mime=mime,
                use_container_width=True,
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
    st.markdown("---")

    # Form to insert an entry for the current user
    st.subheader("New Engineering Log Entry")
    with st.form("engineering_log_form"):
        log_progress = st.text_area("Progress / Milestone", max_chars=5000)
        log_bugs = st.text_area("Bugs / Challenges", max_chars=5000)
        log_learnings = st.text_area("Learnings / Insights", max_chars=5000)
        log_submitted = st.form_submit_button("Submit Log Entry")

    if log_submitted:
        lp_valid, _ = validate_input_length("progress", log_progress)
        lb_valid, _ = validate_input_length("bugs", log_bugs)
        ll_valid, _ = validate_input_length("learnings", log_learnings)

        if not lp_valid or not lb_valid or not ll_valid:
            st.error("Input exceeds maximum allowed length. Please shorten your input.")
        elif (
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
    st.subheader("Your Engineering Log Entries")

    sort_option = st.selectbox(
        "Sort Entries",
        ["Newest first", "Oldest first", "A→Z (milestone)", "Z→A (milestone)"],
        key="eng_log_sort_option",
    )

    try:
        client = get_client()
        if "access_token" in st.session_state:
            client.auth.set_session(
                st.session_state["access_token"],
                st.session_state.get("refresh_token", ""),
            )
        response = (
            client.table("engineering_log")
            .select("*")
            .eq("user_id", user["id"])
            .execute()
        )
        entries = getattr(response, "data", [])

        # Apply sorting
        if sort_option == "Newest first":
            entries = sorted(
                entries, key=lambda x: x.get("created_at", ""), reverse=True
            )
        elif sort_option == "Oldest first":
            entries = sorted(entries, key=lambda x: x.get("created_at", ""))
        elif sort_option == "A→Z (milestone)":
            entries = sorted(entries, key=lambda x: str(x.get("progress", "")).lower())
        elif sort_option == "Z→A (milestone)":
            entries = sorted(
                entries,
                key=lambda x: str(x.get("progress", "")).lower(),
                reverse=True,
            )

        if entries:
            for entry in entries:
                entry_id = entry.get("id")
                created_at = entry.get("created_at", "N/A")
                date_display = (
                    created_at.split("T")[0]
                    if "T" in str(created_at)
                    else str(created_at)
                )
                progress_text = str(entry.get("progress", "Milestone"))
                progress_preview = (
                    progress_text.split("\n")[0][:40] if progress_text else "Milestone"
                )

                expander_label = f"📅 [{date_display}] {progress_preview}"
                with st.expander(expander_label, expanded=False):
                    st.markdown(f"**Timestamp:** `{created_at}`")
                    if entry.get("progress"):
                        st.markdown(
                            f"**Progress / Milestone:**\n{entry.get('progress')}"
                        )
                    if entry.get("bugs"):
                        st.markdown(f"**Bugs / Challenges:**\n{entry.get('bugs')}")
                    if entry.get("learnings"):
                        st.markdown(
                            f"**Learnings / Insights:**\n{entry.get('learnings')}"
                        )

                    col_space, col_btn = st.columns([4, 1])
                    with col_btn:
                        confirm_del_key = f"confirm_del_{entry_id}"
                        if not st.session_state.get(confirm_del_key, False):
                            if st.button("🗑️ Delete", key=f"del_log_{entry_id}"):
                                st.session_state[confirm_del_key] = True
                                st.rerun()
                        else:
                            st.write("Delete entry?")
                            col_c1, col_c2 = st.columns(2)
                            with col_c1:
                                if st.button(
                                    "Confirm delete",
                                    key=f"conf_del_{entry_id}",
                                    type="primary",
                                ):
                                    try:
                                        client = get_client()
                                        if "access_token" in st.session_state:
                                            client.auth.set_session(
                                                st.session_state["access_token"],
                                                st.session_state.get(
                                                    "refresh_token", ""
                                                ),
                                            )
                                        client.table("engineering_log").delete().eq(
                                            "id", entry_id
                                        ).eq("user_id", user["id"]).execute()
                                        st.session_state[confirm_del_key] = False
                                        st.success("Log entry deleted successfully.")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed to delete log entry: {e}")
                            with col_c2:
                                if st.button("Cancel", key=f"canc_del_{entry_id}"):
                                    st.session_state[confirm_del_key] = False
                                    st.rerun()

            st.markdown("---")
            all_confirm_key = "confirm_delete_all_logs"
            if not st.session_state.get(all_confirm_key, False):
                if st.button("Delete ALL my logs", key="btn_delete_all_logs"):
                    st.session_state[all_confirm_key] = True
                    st.rerun()
            else:
                st.warning(
                    "Are you sure you want to delete ALL your engineering logs? This cannot be undone."
                )
                col_all1, col_all2 = st.columns(2)
                with col_all1:
                    if st.button(
                        "Confirm delete ALL logs",
                        key="btn_conf_delete_all",
                        type="primary",
                    ):
                        try:
                            client = get_client()
                            if "access_token" in st.session_state:
                                client.auth.set_session(
                                    st.session_state["access_token"],
                                    st.session_state.get("refresh_token", ""),
                                )
                            client.table("engineering_log").delete().eq(
                                "user_id", user["id"]
                            ).execute()
                            st.session_state[all_confirm_key] = False
                            st.success("All engineering logs deleted successfully.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to delete all logs: {e}")
                with col_all2:
                    if st.button("Cancel", key="btn_canc_delete_all"):
                        st.session_state[all_confirm_key] = False
                        st.rerun()
        else:
            st.info(
                "No engineering log entries found yet. Submit your first entry above."
            )
    except Exception as e:
        st.warning(
            f"Could not load engineering log entries (Table setup required): {e}"
        )
