import json
import time

import streamlit as st
from streamlit.errors import StreamlitAPIException
from streamlit_local_storage import LocalStorage

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


try:
    if "cb_local_storage" not in st.session_state:
        st.session_state["cb_local_storage"] = {}
    local_storage = LocalStorage(key="cb_local_storage")
except Exception as e:
    handle_storage_error(e)
    local_storage = None

if "render_count" not in st.session_state:
    st.session_state["render_count"] = 0
st.session_state["render_count"] += 1

if "boot_mount_triggered" not in st.session_state:
    st.session_state["boot_mount_triggered"] = False

# Storage round-trip probe
try:
    if local_storage:
        probe_val = local_storage.getAll().get("cb_probe") or local_storage.getItem(
            "cb_probe"
        )
        if probe_val:
            st.session_state["persist_probe_last"] = (
                f"present (len {len(str(probe_val))})"
            )
        else:
            st.session_state["persist_probe_last"] = "None"
        local_storage.setItem("cb_probe", "1", key="ls_probe_set")
    else:
        st.session_state["persist_probe_last"] = "LocalStorage unavailable"
except (StreamlitAPIException, Exception) as e:
    handle_storage_error(e)
    st.session_state["persist_probe_last"] = f"error: {type(e).__name__}"

# Boot session rehydration from localStorage if session_state has no active user
if "user" not in st.session_state or "access_token" not in st.session_state:
    try:
        client = get_client()
        try:
            if local_storage:
                session_data = local_storage.getAll().get(
                    "cb_session"
                ) or local_storage.getItem("cb_session")
            else:
                session_data = None
        except (StreamlitAPIException, Exception) as e:
            handle_storage_error(e)
            session_data = None

        if session_data:
            st.session_state["debug_boot_raw"] = (
                f"present (len {len(str(session_data))})"
            )
            st.session_state["debug_raw_head"] = str(session_data)[:12]
        else:
            st.session_state["debug_boot_raw"] = "None"
            st.session_state["debug_raw_head"] = "None"

        if session_data is None and not st.session_state.get("boot_mount_triggered"):
            st.session_state["boot_mount_triggered"] = True
            st.rerun()

        if session_data:
            if isinstance(session_data, str):
                if session_data == "[object Object]":
                    try:
                        handle_storage_error(ValueError("LegacyCorruptSessionObject"))
                        if local_storage:
                            local_storage.deleteItem(
                                "cb_session", key="ls_boot_del_legacy"
                            )
                    except (StreamlitAPIException, Exception) as e:
                        handle_storage_error(e)
                    session_data = None
                else:
                    try:
                        session_data = json.loads(session_data)
                    except Exception as e:
                        handle_storage_error(e)
                        try:
                            if local_storage:
                                local_storage.deleteItem(
                                    "cb_session", key="ls_boot_del_parse"
                                )
                        except (StreamlitAPIException, Exception) as e2:
                            handle_storage_error(e2)
                        session_data = None

            if not isinstance(session_data, dict):
                try:
                    handle_storage_error(TypeError("InvalidSessionTypeNonDict"))
                    if local_storage:
                        local_storage.deleteItem(
                            "cb_session", key="ls_boot_del_nondict"
                        )
                except (StreamlitAPIException, Exception) as e:
                    handle_storage_error(e)
                session_data = None

            if isinstance(session_data, dict):
                access_token = session_data.get("access_token")
                refresh_token = session_data.get("refresh_token")
                expires_at = session_data.get("expires_at")

                if access_token and refresh_token:
                    restored = False
                    is_expired = False
                    if expires_at is not None:
                        try:
                            if float(expires_at) <= time.time():
                                is_expired = True
                        except Exception:
                            pass

                    if not is_expired:
                        try:
                            client.auth.set_session(access_token, refresh_token)
                            user_res = client.auth.get_user(access_token)
                            user_obj = (
                                getattr(user_res, "user", None) if user_res else None
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
                                st.session_state["access_token"] = access_token
                                st.session_state["refresh_token"] = refresh_token
                                st.session_state["expires_at"] = (
                                    expires_at
                                    if expires_at is not None
                                    else time.time() + 3600
                                )
                                restored = True
                        except Exception:
                            restored = False

                    if not restored:
                        try:
                            refresh_res = client.auth.refresh_session(refresh_token)
                            if refresh_res and refresh_res.session:
                                new_sess = refresh_res.session
                                client.auth.set_session(
                                    new_sess.access_token, new_sess.refresh_token
                                )
                                user_obj = getattr(refresh_res, "user", None)
                                if not user_obj:
                                    user_res = client.auth.get_user(
                                        new_sess.access_token
                                    )
                                    user_obj = (
                                        getattr(user_res, "user", None)
                                        if user_res
                                        else None
                                    )

                                if user_obj:
                                    display_name = ""
                                    if user_obj.user_metadata:
                                        display_name = (
                                            user_obj.user_metadata.get(
                                                "display_name", ""
                                            )
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
                                    st.session_state["access_token"] = (
                                        new_sess.access_token
                                    )
                                    st.session_state["refresh_token"] = (
                                        new_sess.refresh_token
                                    )
                                    new_expires = getattr(
                                        new_sess, "expires_at", time.time() + 3600
                                    )
                                    st.session_state["expires_at"] = new_expires
                                    restored = True
                        except Exception:
                            restored = False

                    if not restored:
                        try:
                            if local_storage:
                                local_storage.deleteItem(
                                    "cb_session", key="ls_boot_del_1"
                                )
                        except (StreamlitAPIException, Exception) as e:
                            handle_storage_error(e)
                else:
                    try:
                        if local_storage:
                            local_storage.deleteItem("cb_session", key="ls_boot_del_2")
                    except (StreamlitAPIException, Exception) as e:
                        handle_storage_error(e)
            else:
                try:
                    if local_storage:
                        local_storage.deleteItem("cb_session", key="ls_boot_del_3")
                except (StreamlitAPIException, Exception) as e:
                    handle_storage_error(e)
    except Exception as e:
        handle_storage_error(e)
        try:
            if local_storage:
                local_storage.deleteItem("cb_session", key="ls_boot_del_4")
        except (StreamlitAPIException, Exception) as e2:
            handle_storage_error(e2)

# Ensure Supabase client session is restored if access_token is in session_state
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
                    st.session_state["user"] = {
                        "id": res.user.id,
                        "email": res.user.email,
                        "display_name": display_name,
                        "user_metadata": user_metadata,
                    }
                    st.session_state["access_token"] = res.session.access_token
                    st.session_state["refresh_token"] = res.session.refresh_token
                    expires_at = getattr(res.session, "expires_at", time.time() + 3600)
                    st.session_state["expires_at"] = expires_at
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

# Sidebar Navigation & Auth State
st.sidebar.title("CodeBreaker Navigation")
if st.session_state.get("persist_debug"):
    st.sidebar.caption(f"persistence: degraded — {st.session_state['persist_debug']}")

user = st.session_state.get("user")
user_email = user.get("email", "") if user else ""

pdebug_param = st.query_params.get("pdebug")
if isinstance(pdebug_param, list):
    pdebug_param = pdebug_param[0] if pdebug_param else None

is_admin = (
    bool(ADMIN_EMAIL)
    and bool(user_email)
    and ADMIN_EMAIL.strip().lower() == user_email.strip().lower()
) or pdebug_param == "1"

if is_admin:
    with st.sidebar.expander(
        "Persistence Debug", expanded=False, key="persistence_debug_expander"
    ):
        if st.session_state.get("persistence_debug_expander", False):
            try:
                if local_storage:
                    probe_val = local_storage.getAll().get(
                        "cb_probe"
                    ) or local_storage.getItem("cb_probe")
                    if probe_val:
                        st.session_state["persist_probe_last"] = (
                            f"present (len {len(str(probe_val))})"
                        )
                    else:
                        st.session_state["persist_probe_last"] = "None"
                    local_storage.setItem("cb_probe", "1", key="ls_probe_set")
                else:
                    st.session_state["persist_probe_last"] = "LocalStorage unavailable"
            except (StreamlitAPIException, Exception) as e:
                handle_storage_error(e)
                st.session_state["persist_probe_last"] = f"error: {type(e).__name__}"
        else:
            st.session_state["persist_probe_last"] = "Expander collapsed (probe paused)"

        st.write(f"**Render Count**: {st.session_state.get('render_count', 0)}")
        st.write(
            f"**Mount Flag**: {st.session_state.get('boot_mount_triggered', False)}"
        )
        st.write(f"**Raw Boot-Read**: {st.session_state.get('debug_boot_raw', 'None')}")
        st.write(
            f"**Raw Stored Head**: {st.session_state.get('debug_raw_head', 'None')}"
        )
        st.write(
            f"**Emission Armed**: {bool('access_token' in st.session_state and 'refresh_token' in st.session_state)}"
        )
        st.write(f"**Persist Debug**: {st.session_state.get('persist_debug', 'None')}")
        st.write(
            f"**Round-Trip Probe**: {st.session_state.get('persist_probe_last', 'None')}"
        )

if user:
    st.sidebar.success(f"Logged in as: {user.get('display_name') or user.get('email')}")
    if st.sidebar.button("Sign Out"):
        try:
            client.auth.sign_out()
        except Exception:
            pass
        try:
            if local_storage:
                local_storage.deleteItem("cb_session", key="ls_signout_del_sess")
                local_storage.deleteItem("cb_page", key="ls_signout_del_page")
        except (StreamlitAPIException, Exception) as e:
            handle_storage_error(e)
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Signed out successfully.")
        st.rerun()

    user_email = user.get("email", "")
    if (
        ADMIN_EMAIL
        and user_email
        and ADMIN_EMAIL.strip().lower() == user_email.strip().lower()
    ):
        st.sidebar.markdown("---")
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

    options = ["Home", "Analyze", "Blueprint", "Engineering Log", "About"]
else:
    options = ["Login", "Home", "About"]

try:
    if local_storage:
        saved_page = local_storage.getAll().get("cb_page") or local_storage.getItem(
            "cb_page"
        )
    else:
        saved_page = None
except (StreamlitAPIException, Exception) as e:
    handle_storage_error(e)
    saved_page = None
default_index = options.index(saved_page) if saved_page in options else 0

page = st.sidebar.radio("Navigation", options, index=default_index)

# Continuous idempotent storage emission for authenticated sessions
if (
    local_storage
    and "access_token" in st.session_state
    and "refresh_token" in st.session_state
):
    try:
        expires_at = st.session_state.get("expires_at", time.time() + 3600)
        bundle = {
            "access_token": st.session_state["access_token"],
            "refresh_token": st.session_state["refresh_token"],
            "expires_at": expires_at,
        }
        local_storage.setItem(
            "cb_session",
            json.dumps(bundle),
            key="ls_continuous_session",
        )
        local_storage.setItem("cb_page", page, key="ls_continuous_page")
    except (StreamlitAPIException, Exception) as e:
        handle_storage_error(e)

# Handle password recovery mode return
if st.session_state.get("recovery_mode"):
    st.title("CodeBreaker - Set New Password")
    st.caption("Enter your new password below.")
    st.markdown("---")

    with st.form("set_new_password_form"):
        new_pwd = st.text_input(
            "New Password", type="password", placeholder="", key="reset_pw_new"
        )
        confirm_pwd = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="",
            key="reset_pw_confirm",
        )
        update_submitted = st.form_submit_button(
            "Update Password", key="reset_submit_btn"
        )

    if update_submitted:
        if not new_pwd.strip():
            st.error("Password cannot be empty.")
        elif new_pwd != confirm_pwd:
            st.error("Passwords do not match.")
        else:
            pwd_valid, pwd_err = validate_password(new_pwd)
            if not pwd_valid:
                st.error(pwd_err)
            else:
                try:
                    client = get_client()
                    if "access_token" in st.session_state:
                        client.auth.set_session(
                            st.session_state["access_token"],
                            st.session_state.get("refresh_token", ""),
                        )
                    client.auth.update_user({"password": new_pwd})
                    try:
                        client.auth.sign_out()
                    except Exception:
                        pass
                    try:
                        if local_storage:
                            local_storage.deleteItem(
                                "cb_session", key="ls_reset_del_sess"
                            )
                            local_storage.deleteItem("cb_page", key="ls_reset_del_page")
                    except (StreamlitAPIException, Exception) as e:
                        handle_storage_error(e)

                    for key in list(st.session_state.keys()):
                        del st.session_state[key]

                    st.success(
                        "Password updated successfully! Please log in with your new password."
                    )
                    st.session_state["password_reset_success"] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update password: {e}")
    st.stop()

# Auth gate for all modules except Login and About
if page not in ["Login", "About"] and not user:
    st.warning("Please log in or sign up to access CodeBreaker modules.")
    st.stop()

# First-run onboarding tour for authenticated sessions
user = st.session_state.get("user")
user_meta = user.get("user_metadata", {}) if user else {}
if user and not user_meta.get("tour_seen", False):
    with st.expander(
        "👋 Welcome to CodeBreaker — First-Run Onboarding Tour", expanded=True
    ):
        st.markdown(
            "1. **Analyze**: Describe any project idea to generate an AI-driven blueprint.\n"
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

if page == "Login":
    st.title("CodeBreaker - Authentication")
    st.caption("Secure Access via Supabase Auth & Row Level Security (RLS)")
    st.markdown("---")

    auth_mode = st.radio("Mode", ["Log In", "Sign Up"], horizontal=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        if auth_mode == "Sign Up":
            st.subheader("Create a New Account")
            import time

            cooldown_until = st.session_state.get("signup_cooldown_until", 0)
            cooldown_active = time.time() < cooldown_until
            if cooldown_active:
                remaining = int(cooldown_until - time.time())
                if remaining > 0:
                    st.warning(
                        f"Signup temporarily disabled due to recent failed attempt. Please wait {remaining}s."
                    )
                    time.sleep(1)
                    st.rerun()
                else:
                    cooldown_active = False

            # Scoped CSS to hide any default form submit hint / character counter remnants
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

            with st.form("signup_form"):
                signup_email = st.text_input(
                    "Email", placeholder="you@example.com", key="signup_email"
                )
                signup_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="",
                    key="signup_pw",
                )
                signup_display_name = st.text_input(
                    "Display Name", placeholder="", key="signup_display_name"
                )
                signup_submitted = st.form_submit_button(
                    "Sign Up", disabled=cooldown_active, key="signup_submit_btn"
                )

            if time.time() < st.session_state.get("signup_cooldown_until", 0):
                st.error(
                    "Please wait for the cooldown timer to expire before trying again."
                )
            elif signup_submitted:
                if not signup_email.strip():
                    st.session_state["signup_cooldown_until"] = time.time() + 30
                    st.error("Email cannot be empty.")
                elif not signup_password.strip():
                    st.session_state["signup_cooldown_until"] = time.time() + 30
                    st.error("Password cannot be empty.")
                else:
                    email_format_valid, email_format_err = validate_email(
                        signup_email.strip()
                    )
                    email_len_valid, email_len_err = validate_input_length(
                        "email", signup_email.strip()
                    )
                    pwd_valid, pwd_err = validate_password(signup_password)
                    name_valid, name_err = validate_input_length(
                        "display_name", signup_display_name.strip()
                    )

                    if not email_len_valid:
                        st.session_state["signup_cooldown_until"] = time.time() + 30
                        st.error(email_len_err)
                    elif not email_format_valid:
                        st.session_state["signup_cooldown_until"] = time.time() + 30
                        st.error(email_format_err)
                    elif not pwd_valid:
                        st.session_state["signup_cooldown_until"] = time.time() + 30
                        st.error(pwd_err)
                    elif not name_valid:
                        st.session_state["signup_cooldown_until"] = time.time() + 30
                        st.error(name_err)
                    else:
                        try:
                            client = get_client()
                            res = client.auth.sign_up(
                                {
                                    "email": signup_email.strip(),
                                    "password": signup_password.strip(),
                                    "options": {
                                        "data": {
                                            "display_name": signup_display_name.strip()
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
                                        f"Confirmation email sent to {signup_email.strip()}. Check your inbox (and spam folder)."
                                    )
                                    st.session_state["unconfirmed_email"] = (
                                        signup_email.strip()
                                    )
                                else:
                                    display_name = (
                                        signup_display_name.strip()
                                        or signup_email.strip().split("@")[0]
                                    )
                                    user_metadata = (
                                        getattr(user_obj, "user_metadata", {}) or {}
                                    )
                                    st.session_state["user"] = {
                                        "id": user_obj.id,
                                        "email": user_obj.email,
                                        "display_name": display_name,
                                        "user_metadata": user_metadata,
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
                                    st.success(
                                        "Account created and logged in successfully!"
                                    )
                                    st.rerun()
                        except Exception as e:
                            if (
                                type(e).__name__.startswith("Streamlit")
                                or "DuplicateElementKey" in type(e).__name__
                            ):
                                raise
                            # Set 30s cooldown on failed signup attempt
                            st.session_state["signup_cooldown_until"] = time.time() + 30
                            # NOTE: Server-side rate limits remain Supabase's job (platform layer already enforced).
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

        else:
            st.subheader("Log In to Your Account")
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
            with st.form("login_form"):
                login_email = st.text_input(
                    "Email", placeholder="you@example.com", key="login_email"
                )
                login_password = st.text_input(
                    "Password", type="password", placeholder="", key="login_pw"
                )
                col_lf1, col_lf2 = st.columns(2)
                with col_lf1:
                    login_submitted = st.form_submit_button(
                        "Log In", key="login_submit_btn"
                    )
                with col_lf2:
                    forgot_submitted = st.form_submit_button(
                        "Forgot Password", key="forgot_submit_btn"
                    )

            if login_submitted:
                if not login_email.strip():
                    st.error("Email cannot be empty.")
                elif not login_password.strip():
                    st.error("Password cannot be empty.")
                else:
                    email_format_valid, email_format_err = validate_email(
                        login_email.strip()
                    )
                    if not email_format_valid:
                        st.error(email_format_err)
                    else:
                        try:
                            client = get_client()
                            res = client.auth.sign_in_with_password(
                                {
                                    "email": login_email.strip(),
                                    "password": login_password.strip(),
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
                                    login_email.strip()
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
                                st.session_state["user"] = {
                                    "id": user_obj.id,
                                    "email": user_obj.email,
                                    "display_name": display_name,
                                    "user_metadata": user_metadata,
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
                                st.success("Logged in successfully!")
                                st.rerun()
                        except Exception as e:
                            if (
                                type(e).__name__.startswith("Streamlit")
                                or "DuplicateElementKey" in type(e).__name__
                            ):
                                raise
                            err_str = str(e)
                            if (
                                "not confirmed" in err_str.lower()
                                or "email not confirmed" in err_str.lower()
                            ):
                                st.info("Check your email to confirm your account")
                                st.session_state["unconfirmed_email"] = (
                                    login_email.strip()
                                )
                                st.error(
                                    "Email not confirmed. Please check your email to confirm your account."
                                )
                            elif (
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

            elif forgot_submitted:
                if not login_email.strip():
                    st.error("Email cannot be empty.")
                else:
                    email_valid, email_err = validate_email(login_email.strip())
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
                                login_email.strip(),
                                options={"redirect_to": redirect_to},
                            )
                        except Exception:
                            pass

                        st.info(
                            "If an account exists for that email, a reset link is on its way."
                        )

    with col2:
        st.subheader("GitHub Authentication")
        st.write("Continue securely via GitHub OAuth. Supabase mediates the handshake.")
        st.markdown("")

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
                    "Continue with GitHub", oauth_url, use_container_width=True
                )
        except Exception as e:
            st.error(f"Could not generate GitHub OAuth link: {e}")

elif page == "About":
    st.title("About CodeBreaker")
    st.caption(
        "Plan Before You Code — Architecture, Engineering Logs, and Habit Formation"
    )
    st.markdown("---")

    st.subheader("🎯 Mission Statement")
    st.write(
        "CodeBreaker was built on a core software engineering philosophy: **Plan before you code.** "
        "Too many developers dive straight into writing code without an architecture blueprint, leading to spaghetti code, "
        "unhandled edge cases, and lost engineering context. CodeBreaker bridges the gap between idea and execution "
        "by combining AI-driven system architecture generation, multi-format exports, and isolated engineering logs."
    )

    st.subheader("🎓 How Lecturers Use CodeBreaker in Class")
    st.write(
        "Computer science and software engineering professors use CodeBreaker as a core instructional tool in class. "
        "A typical semester assignment formula is:\n\n"
        "$$\\text{Assignment Grade} = \\text{System Blueprint} + \\text{Engineering Log}$$ \n\n"
        "- **System Blueprint**: Students submit their initial architecture analysis (Tech Stack, Folder Structure, Edge Cases, Roadmap) exported as Markdown, HTML, or PDF.\n"
        "- **Engineering Log**: Students maintain an ongoing log of daily progress, encountered bugs, and technical insights, securely isolated by user accounts and Row Level Security (RLS)."
    )

    st.subheader("🚪 The Two Auth Doors")
    st.markdown(
        "1. **Email / Password Authentication**: Traditional signup and login powered by Supabase Auth with strict email confirmation verification (blocking unconfirmed logins and supporting resend confirmation workflows).\n"
        "2. **GitHub OAuth**: Secure, frictionless Single Sign-On (SSO) via GitHub OAuth with PKCE authorization code exchange mediated securely by Supabase."
    )

    st.subheader("📥 The Four Export Formats")
    st.markdown(
        "1. **Markdown (.md)**: Perfect for dropping into repository `README.md` files as an instant project front page.\n"
        "2. **Plain Text (.txt)**: Universal compatibility with any text editor or AI coding assistant specification.\n"
        "3. **HTML (.html)**: Self-contained, cleanly styled web page optimized for mobile browsers and offline reading.\n"
        "4. **PDF (.pdf)**: Professional architecture document rendering powered by pure-python `fpdf2`, ideal for printing and formal submissions."
    )

    st.subheader("🔗 Public Repository & Open Source")
    st.markdown(
        "CodeBreaker is an open-source project. Explore the source code, open issues, or contribute on GitHub: "
        "[CodeBreaker GitHub Repository](https://github.com)"
    )

    st.markdown("---")
    st.caption("CodeBreaker v1.1.4 • Built with Streamlit, Supabase, Groq & fpdf2")

elif page == "Home":
    st.title("CodeBreaker")
    st.caption(
        "Deconstruct, Analyze, and Architect Systems with AI-Driven Engineering Insights"
    )
    st.markdown("---")
    st.subheader("Welcome to CodeBreaker v1.1.4")
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
            "Project Name", placeholder="e.g., Real-time Chat App", max_chars=100
        )
        problem = st.text_area(
            "Problem Description / Requirements",
            placeholder="What problem are you solving and what are the core requirements?",
            max_chars=2000,
        )
        target_audience = st.text_input(
            "Target Audience",
            placeholder="e.g., Developers, Enterprise, Consumers",
            max_chars=200,
        )
        skill_level = st.selectbox(
            "Your Skill Level", ["Beginner", "Intermediate", "Advanced", "Expert"]
        )

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
        st.info(
            "**What do I do with this file?**\n\n"
            "- Drop it in your GitHub repo as README.md — it becomes your project's front page.\n"
            "- Hand it to any AI coding assistant as your spec.\n"
            "- .html opens in any browser, .txt in any editor, .pdf for human readers & printing, .md renders on GitHub."
        )

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
    st.caption(
        "Record technical design decisions, logs, and milestones isolated by user & RLS."
    )
    st.markdown("---")

    # Form to insert an entry for the current user
    st.subheader("New Engineering Log Entry")
    with st.form("engineering_log_form"):
        log_progress = st.text_area(
            "Progress / Milestone",
            placeholder="What did you accomplish?",
            max_chars=5000,
        )
        log_bugs = st.text_area(
            "Bugs / Challenges",
            placeholder="What issues did you encounter?",
            max_chars=5000,
        )
        log_learnings = st.text_area(
            "Learnings / Insights", placeholder="What did you learn?", max_chars=5000
        )
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
                        if st.button("🗑️ Delete", key=f"del_log_{entry_id}"):
                            try:
                                client = get_client()
                                if "access_token" in st.session_state:
                                    client.auth.set_session(
                                        st.session_state["access_token"],
                                        st.session_state.get("refresh_token", ""),
                                    )
                                # Delete matching entry id and user_id (RLS + application safeguard)
                                client.table("engineering_log").delete().eq(
                                    "id", entry_id
                                ).eq("user_id", user["id"]).execute()
                                st.success("Log entry deleted successfully.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to delete log entry: {e}")
        else:
            st.info(
                "No engineering log entries found yet. Submit your first entry above."
            )
    except Exception as e:
        st.warning(
            f"Could not load engineering log entries (Table or RLS setup required): {e}"
        )
