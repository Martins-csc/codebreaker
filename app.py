import base64
import hashlib
import importlib as _importlib
import json
import os as _os
import re
import secrets
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import requests
import streamlit as st
from ai_engine import (BlueprintError, clean_roadmap_step, extend_blueprint,
                       generate_blueprint, render_blueprint_html,
                       render_blueprint_markdown, render_blueprint_pdf,
                       render_blueprint_text, sanitize_filename)

import ai_engine
_AE_MT = _os.path.getmtime(ai_engine.__file__)
if st.session_state.get("_ae_mt") != _AE_MT:
    _importlib.reload(ai_engine)
    for _n in (
        "BlueprintError",
        "clean_roadmap_step",
        "extend_blueprint",
        "generate_blueprint",
        "render_blueprint_html",
        "render_blueprint_markdown",
        "render_blueprint_pdf",
        "render_blueprint_text",
        "sanitize_filename",
    ):
        if hasattr(ai_engine, _n):
            globals()[_n] = getattr(ai_engine, _n)
    st.session_state["_ae_mt"] = _AE_MT
from config import ADMIN_EMAIL
from security import validate_email, validate_input_length, validate_password
from supabase_client import ConfigError, get_client


def format_display_title(title: str, version: int = 1) -> str:
    if not title:
        title = "Untitled"
    base = re.sub(r"\s*—\s*v\d+", "", title)
    base = re.sub(r"\s*\(v\d+\)", "", base).strip()
    if version > 1:
        return f"{base} (v{version})"
    return base


def get_config(key, default=None):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    import os as _os

    val = _os.environ.get(key)
    return val if val is not None else default


st.set_page_config(
    page_title="CodeBreaker",
    page_icon=":material/terminal:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    div[data-testid="stWidgetTrailer"],
    div[data-testid="stCharCounter"],
    .stForm [data-testid="InputInstructions"],
    div[data-baseweb="input"] + div {
        display: none !important;
    }
    </style>
    <script>
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(input => input.setAttribute('autocomplete', 'off'));
    </script>
    """,
    unsafe_allow_html=True,
)


def format_lagos_timestamp(created_at_str):
    if not created_at_str or created_at_str == "N/A":
        return "N/A", "N/A"
    try:
        clean_str = str(created_at_str).replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        dt_lagos = dt.astimezone(ZoneInfo("Africa/Lagos"))
        d_disp = dt_lagos.strftime("%Y-%m-%d")
        t_disp = dt_lagos.strftime("%Y-%m-%d %H:%M:%S")
        return d_disp, t_disp
    except Exception:
        d = (
            str(created_at_str).split("T")[0]
            if "T" in str(created_at_str)
            else str(created_at_str)
        )
        return d, str(created_at_str)


def fmt_date(created_at_str):
    if not created_at_str or created_at_str == "N/A":
        return "N/A"
    try:
        clean_str = str(created_at_str).replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        dt_lagos = dt.astimezone(ZoneInfo("Africa/Lagos"))
        return dt_lagos.strftime("%d-%m-%Y")
    except Exception:
        s = str(created_at_str).split("T")[0]
        try:
            dt = datetime.strptime(s, "%Y-%m-%d")
            return dt.strftime("%d-%m-%Y")
        except Exception:
            return str(created_at_str)


def format_member_since(created_at_val):
    if not created_at_val or created_at_val == "N/A":
        return "N/A"
    try:
        s_val = str(created_at_val)
        if "T" in s_val:
            clean_str = s_val.replace("Z", "+00:00").split("+")[0].split(".")[0]
            dt = datetime.fromisoformat(clean_str)
            return dt.strftime("%d %b %Y")
        elif len(s_val) == 10 and s_val[4] == "-" and s_val[7] == "-":
            dt = datetime.strptime(s_val, "%Y-%m-%d")
            return dt.strftime("%d %b %Y")
        else:
            dt = datetime.fromisoformat(s_val.replace("Z", "+00:00"))
            return dt.strftime("%d %b %Y")
    except Exception:
        s = str(created_at_val).split("T")[0]
        try:
            dt = datetime.strptime(s, "%Y-%m-%d")
            return dt.strftime("%d %b %Y")
        except Exception:
            return str(created_at_val)


def handle_storage_error(e):
    err_msg = f"{type(e).__name__}: {str(e)[:80]}"
    st.session_state["persist_debug"] = err_msg


def mint_and_set_rt(client, user_id, refresh_token):
    try:
        try:
            client.table("profiles").update({"active_blueprint_id": None}).eq(
                "id", user_id
            ).execute()
        except Exception:
            pass
        st.session_state["active_blueprint_id"] = None
        st.session_state.pop("blueprint", None)
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
                                u_created = getattr(
                                    user_obj, "created_at", None
                                ) or user_metadata.get("created_at", "")
                                c_display = format_member_since(u_created)
                                st.session_state["user"] = {
                                    "id": user_obj.id,
                                    "email": user_obj.email,
                                    "display_name": display_name,
                                    "user_metadata": user_metadata,
                                    "member_since": c_display,
                                }
                                st.session_state["access_token"] = new_sess.access_token
                                st.session_state["refresh_token"] = (
                                    new_sess.refresh_token
                                )
                                st.session_state["expires_at"] = getattr(
                                    new_sess, "expires_at", time.time() + 3600
                                )
                                st.session_state["last_verify_result"] = (
                                    "Verified & Rotated"
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
                st.session_state["auth_flash"] = (
                    "success",
                    "Recovery session established. Please set your new password.",
                )
            elif type_param == "signup":
                st.session_state["auth_flash"] = (
                    "success",
                    "Email confirmed - please log in",
                )
                st.session_state["email_confirmed_success"] = True
        else:
            st.session_state["auth_flash"] = (
                "warning",
                "This link has expired or is invalid. Please request a new one.",
            )
            st.session_state["show_resend_link"] = True

        st.query_params.clear()
        st.rerun()

    # 2. Handle GitHub OAuth authorization code exchange (Manual PKCE flow - single-slot verifier)
    elif code_param:
        code = code_param
        try:
            supabase_url = get_config("SUPABASE_URL").rstrip("/")
            anon_key = get_config("SUPABASE_ANON_KEY")

            # Prune states older than 10 min
            ten_min_ago = (
                datetime.now(timezone.utc) - timedelta(minutes=10)
            ).isoformat()
            try:
                client.table("oauth_states").delete().lt(
                    "created_at", ten_min_ago
                ).execute()
            except Exception:
                pass

            # Lookup verifier by state='pending' order by created_at desc limit 1
            state_res = (
                client.table("oauth_states")
                .select("code_verifier")
                .eq("state", "pending")
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            state_rows = getattr(state_res, "data", [])
            if not state_rows:
                st.session_state["auth_flash"] = (
                    "error",
                    "Sign-in session expired — tap Continue with GitHub again.",
                )
                for p in ["code", "state"]:
                    st.query_params.pop(p, None)
                st.rerun()
            else:
                verifier = state_rows[0].get("code_verifier")

                token_url = f"{supabase_url}/auth/v1/token?grant_type=pkce"
                headers = {"apikey": anon_key, "Content-Type": "application/json"}
                payload = {"auth_code": code, "code_verifier": verifier}

                resp = requests.post(
                    token_url, headers=headers, json=payload, timeout=10
                )
                if resp.status_code == 200:
                    token_data = resp.json()
                    access_token = token_data.get("access_token")
                    refresh_token = token_data.get("refresh_token")

                    if access_token and refresh_token:
                        client.auth.set_session(access_token, refresh_token)
                        user_res = client.auth.get_user(access_token)
                        user_obj = getattr(user_res, "user", None)

                        if user_obj:
                            display_name = ""
                            if user_obj.user_metadata:
                                display_name = (
                                    user_obj.user_metadata.get("display_name", "")
                                    or user_obj.email.split("@")[0]
                                )
                            elif user_obj.email:
                                display_name = user_obj.email.split("@")[0]
                            user_metadata = getattr(user_obj, "user_metadata", {}) or {}
                            u_created = getattr(
                                user_obj, "created_at", None
                            ) or user_metadata.get("created_at", "")
                            c_display = format_member_since(u_created)
                            st.session_state["user"] = {
                                "id": user_obj.id,
                                "email": user_obj.email,
                                "display_name": display_name,
                                "user_metadata": user_metadata,
                                "member_since": c_display,
                            }
                            st.session_state["access_token"] = access_token
                            st.session_state["refresh_token"] = refresh_token
                            st.session_state["expires_at"] = token_data.get(
                                "expires_at", time.time() + 3600
                            )
                            mint_and_set_rt(client, user_obj.id, refresh_token)

                            # Delete the pending state row
                            client.table("oauth_states").delete().eq(
                                "state", "pending"
                            ).execute()

                            st.session_state["auth_flash"] = (
                                "success",
                                "Successfully logged in with GitHub!",
                            )
                            st.query_params["pg"] = "Home"
                            for p in [
                                "code",
                                "state",
                                "type",
                                "token",
                                "token_hash",
                                "error",
                                "error_description",
                                "oauth_state",
                                "mode",
                                "auth_view",
                            ]:
                                st.query_params.pop(p, None)
                            st.rerun()
                        else:
                            st.session_state["auth_flash"] = (
                                "error",
                                "Failed to retrieve user profile after OAuth exchange.",
                            )
                    else:
                        st.session_state["auth_flash"] = (
                            "error",
                            "Invalid token response received from authentication server.",
                        )
                else:
                    st.session_state["auth_flash"] = (
                        "error",
                        resp.text if resp else "OAuth token exchange failed",
                    )
        except Exception as e:
            st.session_state["auth_flash"] = (
                "error",
                f"GitHub OAuth exchange failed: {e}",
            )

        for p in ["code", "state"]:
            st.query_params.pop(p, None)

    if "access_token" in st.session_state and "refresh_token" in st.session_state:
        try:
            client.auth.set_session(
                st.session_state["access_token"], st.session_state["refresh_token"]
            )
        except Exception:
            pass
except ConfigError as ce:
    st.session_state["config_error"] = str(ce)

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
    if st.session_state.get("config_error"):
        st.error(f"Configuration Error: {st.session_state.pop('config_error')}")
    if st.session_state.get("auth_flash"):
        ftype, fmsg = st.session_state.pop("auth_flash")
        if ftype == "success":
            st.success(fmsg)
        elif ftype == "warning":
            st.warning(fmsg)
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                if st.button("Resend confirmation email", key="resend_conf_btn"):
                    st.session_state["show_resend_link"] = True
            with col_res2:
                if st.button("Forgot password?", key="forgot_pwd_btn"):
                    st.session_state["show_forgot_password"] = True
        elif ftype == "error":
            st.error(fmsg)
    if st.session_state.get("auth_view"):
        if st.button("← Back to overview", key="auth_back_to_overview"):
            del st.session_state["auth_view"]
            st.rerun()

        st.markdown("---")
        with st.container():
            auth_mode = st.query_params.get(
                "mode", st.session_state.get("auth_view", "login")
            )
            if auth_mode not in ["login", "signup"]:
                auth_mode = "login"

            st.markdown(
                """
                <style>
                .stForm [data-testid="InputInstructions"], div[data-baseweb="input"] + div {
                    display: none !important;
                }
                div[data-testid="stButton"] button[kind="tertiary"] {
                    color: #1a73e8;
                    font-weight: 600;
                    font-size: 1.05em;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            auth_email = st.text_input("Email", placeholder="", key="auth_card_email")
            auth_password = st.text_input(
                "Password", type="password", placeholder="", key="auth_card_password"
            )

            auth_display_name = ""
            if auth_mode == "signup":
                auth_display_name = st.text_input(
                    "Display Name", placeholder="", key="auth_card_display_name"
                )

            if auth_mode == "login":
                col_b1, col_b2 = st.columns(2)
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
                                c_display = format_member_since(u_created)
                                st.session_state["user"] = {
                                    "id": user_obj.id,
                                    "email": user_obj.email,
                                    "display_name": display_name,
                                    "user_metadata": user_metadata,
                                    "member_since": c_display,
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
                                    c_display = format_member_since(u_created)
                                    st.session_state["user"] = {
                                        "id": user_obj.id,
                                        "email": user_obj.email,
                                        "display_name": display_name,
                                        "user_metadata": user_metadata,
                                        "member_since": c_display,
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

            st.markdown(
                """
                <div style="display: flex; align-items: center; text-align: center; color: #888; margin: 1em 0;">
                    <hr style="flex: 1; border: none; border-top: 1px solid #ccc;">
                    <span style="padding: 0 10px;">or</span>
                    <hr style="flex: 1; border: none; border-top: 1px solid #ccc;">
                </div>
                """,
                unsafe_allow_html=True,
            )

            redirect_to = getattr(st.context, "url", None)
            if redirect_to:
                redirect_to = redirect_to.split("?")[0]
            else:
                redirect_to = "http://localhost:8501"

            try:
                client = get_client()
                supabase_url = get_config("SUPABASE_URL").rstrip("/")
                anon_key = get_config("SUPABASE_ANON_KEY")

                verifier = secrets.token_urlsafe(43)
                digest = hashlib.sha256(verifier.encode("utf-8")).digest()
                challenge = (
                    base64.urlsafe_b64encode(digest).rstrip(b"=").decode("utf-8")
                )
                state = secrets.token_urlsafe(16)

                try:
                    client.table("oauth_states").delete().eq(
                        "state", "pending"
                    ).execute()
                    client.table("oauth_states").insert(
                        {"state": "pending", "code_verifier": verifier}
                    ).execute()
                except Exception:
                    pass

                # Supabase Redirect URLs whitelist required in Dashboard:
                # 1. App domain (e.g. https://your-app.replit.app / https://your-project.streamlit.app)
                # 2. Streamlit public URL + /streamlit (e.g. https://.../streamlit)
                encoded_redirect = urllib.parse.quote(redirect_to, safe="")
                authorize_url = f"{supabase_url}/auth/v1/authorize?provider=github&apikey={anon_key}&redirect_to={encoded_redirect}&state={state}&code_challenge={challenge}&code_challenge_method=s256"

                st.link_button(
                    "Continue with GitHub",
                    authorize_url,
                    use_container_width=True,
                    key="card_github_link_btn",
                )

                col_ac1, col_ac2, col_ac3 = st.columns([0.25, 0.5, 0.25])
                with col_ac2:
                    if auth_mode == "login":
                        if st.button(
                            "Don't have an account? Sign up",
                            type="tertiary",
                            use_container_width=True,
                            key="auth_switch_to_signup",
                        ):
                            st.session_state["auth_view"] = "signup"
                            st.query_params["mode"] = "signup"
                            st.rerun()
                    else:
                        if st.button(
                            "Already have an account? Log in",
                            type="tertiary",
                            use_container_width=True,
                            key="auth_switch_to_login",
                        ):
                            st.session_state["auth_view"] = "login"
                            st.query_params["mode"] = "login"
                            st.rerun()
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
                ":material/analytics: **Analyze**\n\nTransform project requirements into structured technical specs."
            )
        with col_m2:
            st.info(
                ":material/description: **Blueprint**\n\nExplore multi-tab system architecture, tech stacks, and exportable documentation."
            )
        with col_m3:
            st.info(
                ":material/journal: **Engineering Log**\n\nMaintain a secure, chronological record of daily progress and technical insights."
            )

        st.markdown("---")
        col_cta1, col_cta2 = st.columns(2)
        with col_cta1:
            if st.button(
                "Log In", key="cta_login", type="primary", use_container_width=True
            ):
                st.session_state["auth_view"] = "login"
                st.session_state["nav_pending"] = "Auth"
                st.rerun()
        with col_cta2:
            if st.button("Create Account", key="cta_signup", use_container_width=True):
                st.session_state["auth_view"] = "signup"
                st.session_state["nav_pending"] = "Auth"
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
        st.sidebar.subheader(":material/shield: Admin Pulse")
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

    options = ["Home", "Analyze", "Blueprint", "Engineering Log", "Contact", "About"]
    _pg = st.query_params.get("pg")
    if isinstance(_pg, list):
        _pg = _pg[0] if _pg else None

    if "nav_pending" in st.session_state:
        _nav_val = st.session_state.pop("nav_pending")
        st.session_state["nav_radio"] = _nav_val
        st.query_params["pg"] = _nav_val
        _pg = _nav_val
    elif "nav_radio" not in st.session_state:
        st.session_state["nav_radio"] = _pg if _pg in options else "Home"

    page = st.sidebar.radio(
        "Section", options, label_visibility="collapsed", key="nav_radio"
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

            st.markdown("**Provider Keys Status:**")
            for pkey in [
                "GROQ_API_KEY",
                "GEMINI_API_KEY",
                "SUPABASE_URL",
                "SUPABASE_ANON_KEY",
            ]:
                p_status = "PRESENT" if bool(get_config(pkey)) else "MISSING"
                st.write(f"- `{pkey}`: **{p_status}**")

    st.sidebar.markdown("---")
    if st.sidebar.button("Log Out", key="sidebar_sign_out_btn"):
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
        auth_params = [
            "rt",
            "pg",
            "code",
            "state",
            "type",
            "token",
            "token_hash",
            "error",
            "error_description",
            "oauth_state",
            "mode",
            "auth_view",
        ]
        for p in auth_params:
            st.query_params.pop(p, None)
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Signed out successfully.")
        st.rerun()

# First-run onboarding tour for authenticated sessions
user_meta = user.get("user_metadata", {}) if user else {}
if user and not user_meta.get("tour_seen", False):
    with st.expander(
        "Welcome to CodeBreaker - First-Run Onboarding Tour", expanded=True
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

    st.subheader("FAQ")
    with st.expander("Privacy: Are my logs private?"):
        st.write("Yes, strictly isolated to your authenticated account.")
    with st.expander("Forgot Password: How do I reset my password?"):
        st.write("Use the password reset link on the login screen.")
    with st.expander("Reload Login Note: Do I stay logged in across reloads?"):
        st.write("Yes, via secure session tokens.")
    with st.expander("Where is my exported file: Where do exports go?"):
        st.write("Straight to your browser's default download location.")

    st.subheader("For Lecturers & Supervisors")
    st.write(
        "Computer science and software engineering professors use CodeBreaker as a core instructional tool in class. "
        "A typical semester assignment formula is:\n\n"
        "$$\\text{Assignment Grade} = \\text{System Blueprint} + \\text{Engineering Log}$$ \n\n"
        "- **System Blueprint**: Students submit their initial architecture analysis (Tech Stack, Folder Structure, Edge Cases, Roadmap) exported as Markdown, HTML, or PDF.\n"
        "- **Engineering Log**: Students maintain an ongoing log of daily progress, encountered bugs, and technical insights, securely isolated by user accounts."
    )

    st.markdown("---")
    col_ab1, col_ab2 = st.columns([3, 1])
    with col_ab1:
        st.markdown("**Built by CodeBreaker Dev**")
    with col_ab2:
        if st.button("Contact us", key="about_contact_btn", use_container_width=True):
            st.session_state["nav_pending"] = "Contact"
            st.rerun()

elif page == "Contact":
    if st.session_state.get("contact_clear_pending"):
        st.session_state["contact_name_input"] = ""
        st.session_state["contact_email_input"] = ""
        st.session_state["contact_message_input"] = ""
        st.session_state["contact_clear_pending"] = False

    if st.session_state.get("contact_success"):
        st.success("Message sent. We'll respond within 24 hours.")
        st.session_state["contact_success"] = False

    st.title("Contact Us")
    st.markdown("---")
    st.write("Have questions, feedback, or need support? Send us a message.")

    contact_name = st.text_input("Name", key="contact_name_input")
    contact_email = st.text_input("Email", key="contact_email_input")
    contact_message = st.text_area("Message", height=125, key="contact_message_input")

    if st.button("Send Message", type="primary", key="contact_send_btn"):
        last_sub = st.session_state.get("contact_last_submitted", 0)
        now = time.time()
        if now - last_sub < 60:
            remaining = int(60 - (now - last_sub))
            st.error(
                f"Please wait {remaining} seconds before submitting another message (60s cooldown)."
            )
        elif (
            not contact_name.strip()
            or not contact_email.strip()
            or not contact_message.strip()
        ):
            st.error("All fields (Name, Email, Message) are required.")
        else:
            email_ok, email_err = validate_email(contact_email.strip())
            if not email_ok:
                st.error(email_err)
            else:
                missing_smtp = any(
                    not get_config(k)
                    for k in ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD"]
                )
                if missing_smtp:
                    st.error("Contact form unavailable — email service not configured")
                    st.stop()

                smtp_host = get_config("SMTP_HOST")
                smtp_port_str = get_config("SMTP_PORT")
                smtp_user = get_config("SMTP_USER")
                smtp_password = get_config("SMTP_PASSWORD")
                to_email = get_config(
                    "CONTACT_TO_EMAIL",
                    "codebreakerbuild@gmail.com",
                )
                if not to_email:
                    to_email = "codebreakerbuild@gmail.com"

                success = False
                try:
                    import smtplib
                    from email.mime.text import MIMEText

                    port = int(smtp_port_str)
                    if port == 465:
                        server = smtplib.SMTP_SSL(smtp_host, port)
                    else:
                        server = smtplib.SMTP(smtp_host, port)
                        server.starttls()

                    server.login(smtp_user, smtp_password)
                    msg_text = f"From: {contact_name} <{contact_email}>\n\nMessage:\n{contact_message}"
                    msg = MIMEText(msg_text)
                    msg["Subject"] = f"CodeBreaker Contact: {contact_name}"
                    msg["From"] = smtp_user
                    msg["To"] = to_email

                    server.sendmail(msg["From"], [msg["To"]], msg.as_string())
                    server.quit()
                    success = True
                except smtplib.SMTPException as e:
                    st.error(f"Email send failed: {e}")
                except Exception as e:
                    st.error(f"Email send failed: {e}")

                if success:
                    st.session_state["contact_last_submitted"] = time.time()
                    st.session_state["contact_clear_pending"] = True
                    st.session_state["contact_success"] = True
                    print(f"Contact email sent to {to_email}")
                    st.rerun()

elif page == "Home":
    st.title("Dashboard")
    st.markdown("---")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        with st.container(border=True):
            st.subheader("My Blueprints")
            try:
                client = get_client()
                if "access_token" in st.session_state:
                    client.auth.set_session(
                        st.session_state["access_token"],
                        st.session_state.get("refresh_token", ""),
                    )
                bp_res = (
                    client.table("blueprints")
                    .select("id, title, created_at, version")
                    .eq("user_id", user["id"])
                    .order("created_at", desc=True)
                    .limit(5)
                    .execute()
                )
                bp_rows = getattr(bp_res, "data", [])
                if bp_rows:
                    st.markdown("**Recent Blueprints:**")
                    for bp_item in bp_rows:
                        bp_id = bp_item.get("id")
                        bp_title = bp_item.get("title") or "Untitled Project"
                        bp_ver = bp_item.get("version", 1)
                        display_title = format_display_title(bp_title, bp_ver)
                        b_created = bp_item.get("created_at", "N/A")
                        date_str = fmt_date(b_created)

                        col_bl1, col_bl2 = st.columns([3, 1])
                        with col_bl1:
                            st.markdown(f"- **{display_title}** `({date_str})`")
                        with col_bl2:
                            if st.button(
                                "Open",
                                key=f"home_open_bp_{bp_id}",
                                use_container_width=True,
                            ):
                                st.session_state["active_blueprint_id"] = bp_id
                                try:
                                    client.table("profiles").update(
                                        {"active_blueprint_id": bp_id}
                                    ).eq("id", user["id"]).execute()
                                except Exception:
                                    pass
                                st.session_state["nav_pending"] = "Blueprint"
                                st.rerun()
                    if st.button(
                        "View all blueprints",
                        key="home_view_all_blueprints_btn",
                        use_container_width=True,
                    ):
                        st.session_state["active_blueprint_id"] = None
                        st.session_state.pop("blueprint", None)
                        try:
                            client.table("profiles").update(
                                {"active_blueprint_id": None}
                            ).eq("id", user["id"]).execute()
                        except Exception:
                            pass
                        st.session_state["nav_pending"] = "Blueprint"
                        st.rerun()
                else:
                    st.write("No saved blueprints yet.")
            except Exception:
                bp_count = st.session_state.get(
                    "blueprint_count", 1 if st.session_state.get("blueprint") else 0
                )
                st.metric("Generated This Session", bp_count)
                st.write("No saved blueprints yet.")

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
                    .select("project_name, title, progress, created_at")
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
                        proj = row.get("project_name") or "General"
                        ttl = (
                            row.get("title")
                            or str(row.get("progress", "Milestone"))[:40]
                        )
                        d_str = fmt_date(row.get("created_at"))
                        st.markdown(f"- `({d_str})` **{proj}** — {ttl}")
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
                    st.session_state["nav_pending"] = "Analyze"
                    st.rerun()
            with qs_c2:
                if st.button("Blueprint", use_container_width=True, key="qs_blueprint"):
                    st.session_state["nav_pending"] = "Blueprint"
                    st.rerun()
            with qs_c3:
                if st.button("Eng. Log", use_container_width=True, key="qs_log"):
                    st.session_state["nav_pending"] = "Engineering Log"
                    st.rerun()

    with col_t4:
        with st.container(border=True):
            st.subheader("Account")
            st.markdown(f"**Display Name:** {user.get('display_name', 'N/A')}")
            st.markdown(f"**Email:** {user.get('email', 'N/A')}")
            st.markdown(f"**Member Since:** {user.get('member_since', 'N/A')}")

elif page == "Analyze":
    st.title("Analyze & Architecture Generation")

    project_name = st.text_input(
        "Project Name", placeholder="e.g. Chat App", key="analyze_project_name_input"
    )
    problem = st.text_area(
        "Problem Description / Requirements",
        placeholder="What problem are you solving and what are the core requirements?",
        key="analyze_problem_area",
    )
    target_audience = st.text_input(
        "Target Audience",
        placeholder="e.g. Students, Enterprise, Consumers",
        key="analyze_target_audience_input",
    )

    submitted = st.button(
        "Generate Blueprint", type="primary", key="btn_submit_analyze"
    )

    if submitted:
        p_val = st.session_state.get("analyze_project_name_input", "")
        prob_val = st.session_state.get("analyze_problem_area", "")
        ta_val = st.session_state.get("analyze_target_audience_input", "")

        pn_valid, pn_err = validate_input_length("project_name", p_val)
        prob_valid, prob_err = validate_input_length("problem", prob_val)
        ta_valid, ta_err = validate_input_length("target_audience", ta_val)

        if not pn_valid or not prob_valid or not ta_valid:
            st.error("Input exceeds maximum allowed length. Please shorten your input.")
        elif not p_val.strip() or not prob_val.strip():
            st.error("Please provide at least a Project Name and Problem Description.")
        else:
            analysis_payload = {
                "project_name": p_val,
                "problem": prob_val,
                "target_audience": ta_val,
                "skill_level": "Intermediate",
            }
            with st.spinner("Generating blueprint…"):
                try:
                    blueprint = generate_blueprint(analysis_payload)
                    st.session_state["blueprint"] = blueprint
                    st.session_state["current_project_name"] = p_val.strip()
                    st.session_state["blueprint_count"] = (
                        st.session_state.get("blueprint_count", 0) + 1
                    )
                    try:
                        client = get_client()
                        if "access_token" in st.session_state:
                            client.auth.set_session(
                                st.session_state["access_token"],
                                st.session_state.get("refresh_token", ""),
                            )
                        blueprint["project_description"] = prob_val
                        blueprint["target_audience"] = ta_val
                        blueprint["project_name"] = p_val.strip()
                        bp_payload = {
                            "user_id": user["id"],
                            "title": p_val.strip(),
                            "blueprint_json": blueprint,
                            "version": 1,
                            "parent_id": None,
                        }
                        ins_res = (
                            client.table("blueprints").insert(bp_payload).execute()
                        )
                        ins_data = getattr(ins_res, "data", [])
                        if ins_data and isinstance(ins_data, list):
                            new_bp_id = ins_data[0].get("id")
                            if new_bp_id:
                                st.session_state["active_blueprint_id"] = new_bp_id
                                try:
                                    client.table("profiles").update(
                                        {"active_blueprint_id": new_bp_id}
                                    ).eq("id", user["id"]).execute()
                                except Exception:
                                    pass
                    except Exception as e:
                        st.warning(
                            f"Blueprint generated but could not be saved to your library: {e}"
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

    active_bp_id = st.session_state.get("active_blueprint_id")
    client = get_client()
    if "access_token" in st.session_state:
        client.auth.set_session(
            st.session_state["access_token"],
            st.session_state.get("refresh_token", ""),
        )

    if not active_bp_id:
        try:
            res_prof = (
                client.table("profiles")
                .select("active_blueprint_id")
                .eq("id", user["id"])
                .execute()
            )
            p_rows = getattr(res_prof, "data", [])
            if p_rows and p_rows[0].get("active_blueprint_id"):
                active_bp_id = p_rows[0].get("active_blueprint_id")
                st.session_state["active_blueprint_id"] = active_bp_id
        except Exception:
            pass

    if active_bp_id and not st.session_state.get("blueprint"):
        try:
            res_bp = (
                client.table("blueprints")
                .select("blueprint_json")
                .eq("id", active_bp_id)
                .eq("user_id", user["id"])
                .execute()
            )
            rows = getattr(res_bp, "data", [])
            if rows:
                b_json = rows[0].get("blueprint_json")
                if isinstance(b_json, str):
                    import json

                    blueprint = json.loads(b_json)
                elif isinstance(b_json, dict):
                    blueprint = b_json
                st.session_state["blueprint"] = blueprint
        except Exception:
            pass

    blueprint = st.session_state.get("blueprint")

    if not active_bp_id or not blueprint:
        st.markdown(
            """
            <style>
            div[data-testid="stContainer"] div.stButton > button[kind="primary"] {
                background-color: #d33;
                color: #fff;
                border-color: #d33;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.subheader("Blueprint Library")
        st.write("Select a blueprint to open, extend, or manage.")
        try:
            now_t = time.time()
            for k in list(st.session_state.keys()):
                if k.startswith("arm_time_bp_"):
                    b_id_k = k.replace("arm_time_bp_", "")
                    if now_t - st.session_state.get(k, 0) > 10:
                        st.session_state[f"arm_del_bp_{b_id_k}"] = False
                        st.session_state.pop(k, None)

            all_bp_res = (
                client.table("blueprints")
                .select("id, title, created_at, version, blueprint_json")
                .eq("user_id", user["id"])
                .order("created_at", desc=True)
                .execute()
            )
            all_bps = getattr(all_bp_res, "data", [])
            if all_bps:
                for item in all_bps:
                    b_id = item.get("id")
                    b_title = item.get("title") or "Untitled"
                    b_ver = item.get("version", 1)
                    display_title = format_display_title(b_title, b_ver)
                    b_created = item.get("created_at", "N/A")
                    date_str = fmt_date(b_created)

                    with st.container(border=True):
                        st.markdown(f"**{display_title}** — `({date_str})`")
                        del_armed_key = f"arm_del_bp_{b_id}"
                        del_time_key = f"arm_time_bp_{b_id}"
                        is_armed = st.session_state.get(del_armed_key, False)

                        rc1, rc2 = st.columns(2)
                        with rc1:
                            if st.button(
                                "Open", key=f"bp_open_{b_id}", use_container_width=True
                            ):
                                st.session_state["active_blueprint_id"] = b_id
                                b_json = item.get("blueprint_json")
                                if isinstance(b_json, str):
                                    st.session_state["blueprint"] = json.loads(b_json)
                                else:
                                    st.session_state["blueprint"] = b_json
                                try:
                                    client.table("profiles").update(
                                        {"active_blueprint_id": b_id}
                                    ).eq("id", user["id"]).execute()
                                except Exception:
                                    pass
                                st.session_state["nav_pending"] = "Blueprint"
                                st.rerun()
                        with rc2:
                            if st.button(
                                "Extend",
                                key=f"bp_extend_{b_id}",
                                use_container_width=True,
                            ):
                                st.session_state[f"extending_{b_id}"] = (
                                    not st.session_state.get(f"extending_{b_id}", False)
                                )
                                st.rerun()

                        if not is_armed:
                            if st.button(
                                "Delete",
                                key=f"bp_del_{b_id}",
                                use_container_width=True,
                            ):
                                st.session_state[del_armed_key] = True
                                st.session_state[del_time_key] = time.time()
                                st.rerun()
                        else:

                            def do_delete(rid):
                                client.table("blueprints").delete().eq(
                                    "id", rid
                                ).execute()
                                if st.session_state.get("active_blueprint_id") == rid:
                                    st.session_state["active_blueprint_id"] = None
                                    st.session_state.pop("blueprint", None)
                                    try:
                                        client.table("profiles").update(
                                            {"active_blueprint_id": None}
                                        ).eq("id", user["id"]).execute()
                                    except Exception:
                                        pass
                                st.session_state.pop(del_armed_key, None)
                                st.session_state.pop(del_time_key, None)
                                st.rerun()

                            def disarm(rid):
                                st.session_state[del_armed_key] = False
                                st.session_state.pop(del_time_key, None)
                                st.rerun()

                            row_id = b_id
                            ca, cb = st.columns(2)
                            with ca:
                                if st.button(
                                    "Confirm",
                                    key=f"arm_confirm_{row_id}",
                                    type="primary",
                                    use_container_width=True,
                                ):
                                    do_delete(row_id)
                            with cb:
                                if st.button(
                                    "Cancel",
                                    key=f"arm_cancel_{row_id}",
                                    use_container_width=True,
                                ):
                                    disarm(row_id)

                        if st.session_state.get(f"extending_{b_id}", False):
                            with st.container(border=True):
                                st.markdown(f"**Extend: {display_title}**")
                                ext_new = st.text_area(
                                    "What is new / changed?", key=f"ext_new_{b_id}"
                                )
                                ext_notes = st.text_area(
                                    "Optional notes", key=f"ext_notes_{b_id}"
                                )
                                if st.button(
                                    "Submit Extension",
                                    key=f"ext_submit_{b_id}",
                                    type="primary",
                                    use_container_width=True,
                                ):
                                    if not ext_new.strip():
                                        st.error(
                                            "Please describe what is new or changed."
                                        )
                                    else:
                                        with st.spinner("Extending blueprint..."):
                                            try:
                                                old_json = item.get("blueprint_json")
                                                if isinstance(old_json, str):
                                                    old_dict = json.loads(old_json)
                                                else:
                                                    old_dict = old_json
                                                new_dict = extend_blueprint(
                                                    old_dict, ext_new, ext_notes
                                                )
                                                new_ver = int(b_ver) + 1
                                                base_t = re.sub(
                                                    r"\s*—\s*v\d+$", "", b_title
                                                ).strip()
                                                new_t = base_t  # NEVER append "— vN" to stored title!
                                                new_dict["project_name"] = new_t
                                                new_payload = {
                                                    "user_id": user["id"],
                                                    "title": new_t,
                                                    "blueprint_json": new_dict,
                                                    "version": new_ver,
                                                    "parent_id": b_id,
                                                }
                                                ins_res = (
                                                    client.table("blueprints")
                                                    .insert(new_payload)
                                                    .execute()
                                                )
                                                ins_data = getattr(ins_res, "data", [])
                                                if ins_data and isinstance(
                                                    ins_data, list
                                                ):
                                                    new_id = ins_data[0].get("id")
                                                    st.session_state[
                                                        "active_blueprint_id"
                                                    ] = new_id
                                                    st.session_state["blueprint"] = (
                                                        new_dict
                                                    )
                                                    try:
                                                        client.table("profiles").update(
                                                            {
                                                                "active_blueprint_id": new_id
                                                            }
                                                        ).eq("id", user["id"]).execute()
                                                    except Exception:
                                                        pass
                                                st.session_state[
                                                    f"extending_{b_id}"
                                                ] = False
                                                st.success(
                                                    "Blueprint extended successfully!"
                                                )
                                                st.rerun()
                                            except Exception as e:
                                                st.error(
                                                    f"Failed to extend blueprint: {e}"
                                                )
            else:
                st.info("Open a blueprint from your library or generate a new one.")
        except Exception:
            st.error("LIBRARY-WITNESS:\n" + __import__("traceback").format_exc()[-900:])
    else:
        if st.button(
            "← Back to All Blueprints", use_container_width=False, key="back_to_all_bps"
        ):
            st.session_state["active_blueprint_id"] = None
            st.session_state.pop("blueprint", None)
            try:
                client.table("profiles").update({"active_blueprint_id": None}).eq(
                    "id", user["id"]
                ).execute()
            except Exception:
                pass
            st.rerun()

        col_title, col_export = st.columns([2, 2])
        with col_title:
            b_ver = blueprint.get("version", 1) if isinstance(blueprint, dict) else 1
            p_name = (
                blueprint.get("project_name")
                or blueprint.get("title")
                or "Untitled Project"
            )
            display_title = format_display_title(p_name, b_ver)
            st.subheader(f"Blueprint for: {display_title}")
        with col_export:
            base_fname = sanitize_filename(blueprint.get("project_name", "blueprint"))
            if base_fname.endswith(".md"):
                txt_fname = base_fname[:-3] + ".txt"
                html_fname = base_fname[:-3] + ".html"
                pdf_fname = base_fname[:-3] + ".pdf"
            else:
                txt_fname = base_fname + ".txt"
                html_fname = base_fname + ".html"
                pdf_fname = base_fname + ".pdf"

            formats_info = [
                (
                    "Export as Markdown (.md)",
                    render_blueprint_markdown(blueprint),
                    base_fname,
                    "text/markdown",
                    "editable spec for repos & AI assistants",
                    "export_md_btn",
                ),
                (
                    "Export as Plain text (.txt)",
                    render_blueprint_text(blueprint),
                    txt_fname,
                    "text/plain",
                    "universal, opens anywhere",
                    "export_txt_btn",
                ),
                (
                    "Export as HTML (.html)",
                    render_blueprint_html(blueprint),
                    html_fname,
                    "text/html",
                    "styled page for browser/offline",
                    "export_html_btn",
                ),
                (
                    "Export as PDF (.pdf)",
                    bytes(render_blueprint_pdf(blueprint)),
                    pdf_fname,
                    "application/pdf",
                    "fixed-layout for print & share",
                    "export_pdf_btn",
                ),
            ]

            for lbl, dat, fn, mime_type, expl, k in formats_info:
                rc1, rc2 = st.columns([0.82, 0.18])
                with rc1:
                    export_data = (
                        dat.encode("utf-8-sig") if fn.endswith(".txt") else dat
                    )
                    st.download_button(
                        label=lbl,
                        data=export_data,
                        file_name=fn,
                        mime=(
                            "text/plain; charset=utf-8"
                            if fn.endswith(".txt")
                            else mime_type
                        ),
                        use_container_width=True,
                        key=k,
                    )
                with rc2:
                    try:
                        with st.popover(":material/info:"):
                            st.write(expl)
                    except Exception:
                        with st.expander("ⓘ"):
                            st.write(expl)

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
            if isinstance(folder_tree, str):
                folder_tree = folder_tree.replace("\\n", "\n")
            st.code(folder_tree, language=None)

        with tab_edges:
            st.markdown("### Potential Edge Cases & Risks")
            edge_cases = blueprint.get("edge_cases", [])
            if edge_cases:
                for edge in edge_cases:
                    st.markdown(f"- {edge}")
            else:
                st.write("No edge cases specified.")

        with tab_roadmap:
            roadmap = blueprint.get("roadmap", [])
            valid_roadmap = [
                r for r in roadmap if r is not None and str(r).lower() != "none"
            ]
            cleaned_roadmap = [clean_roadmap_step(s) for s in valid_roadmap]
            st.markdown("### Implementation Roadmap")
            if cleaned_roadmap:
                for i, step in enumerate(cleaned_roadmap, 1):
                    st.markdown(f"**Step {i}:** {step}")
            else:
                st.write("No roadmap specified.")

        with tab_summary:
            st.markdown("### Executive Summary")
            st.write(blueprint.get("summary", "No summary provided."))

elif page == "Engineering Log":
    st.markdown(
        """
        <style>
        div[data-testid="stExpander"] div.stButton > button[kind="primary"] {
            background-color: #d33;
            color: #fff;
            border-color: #d33;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("Engineering Log")
    st.markdown("---")

    # Plain widgets to insert an entry for the current user
    st.subheader("New Engineering Log Entry")
    default_proj = (
        st.session_state.get("current_project_name")
        or st.session_state.get("blueprint", {}).get("project_name")
        or "General"
    )
    log_project_name = st.text_input(
        "Project Name", value=default_proj, key="log_project_name_input"
    )
    log_milestone_title = st.text_input(
        "Milestone Title (optional)", max_chars=40, key="log_title_input"
    )
    log_progress = st.text_area("Progress / Milestone", key="log_progress_area")
    log_bugs = st.text_area("Bugs / Challenges", key="log_bugs_area")
    log_learnings = st.text_area("Learnings / Insights", key="log_learnings_area")
    log_submitted = st.button("Submit Log Entry", key="btn_submit_log_entry")

    if log_submitted:
        lp_valid, _ = validate_input_length("progress", log_progress)
        lb_valid, _ = validate_input_length("bugs", log_bugs)
        ll_valid, _ = validate_input_length("learnings", log_learnings)
        pn_valid, _ = validate_input_length("project_name", log_project_name)
        title_val = log_milestone_title.strip()[:40]
        if not title_val:
            prog_clean = log_progress.strip()
            title_val = prog_clean[:40] if prog_clean else "N/A"

        if not lp_valid or not lb_valid or not ll_valid or not pn_valid:
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
                    "project_name": log_project_name.strip() or "General",
                    "title": title_val,
                    "progress": log_progress.strip() if log_progress.strip() else "N/A",
                    "bugs": log_bugs.strip() if log_bugs.strip() else "N/A",
                    "learnings": (
                        log_learnings.strip() if log_learnings.strip() else "N/A"
                    ),
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
        now_t = time.time()
        for k in list(st.session_state.keys()):
            if k.startswith("arm_time_log_"):
                log_id_k = k.replace("arm_time_log_", "")
                if now_t - st.session_state.get(k, 0) > 10:
                    st.session_state[f"confirm_del_{log_id_k}"] = False
                    st.session_state.pop(k, None)

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
            # Group entries by project
            grouped = {}
            for entry in entries:
                p_name = entry.get("project_name") or "General"
                if p_name not in grouped:
                    grouped[p_name] = []
                grouped[p_name].append(entry)

            for proj_name, proj_entries in grouped.items():
                st.markdown(f"### Project: {proj_name}")
                for entry in proj_entries:
                    entry_id = entry.get("id")
                    created_at = entry.get("created_at", "N/A")
                    date_display = fmt_date(created_at)
                    try:
                        clean_str = str(created_at).replace("Z", "+00:00")
                        dt = datetime.fromisoformat(clean_str)
                        dt_lagos = dt.astimezone(ZoneInfo("Africa/Lagos"))
                        time_display = dt_lagos.strftime("%H:%M:%S")
                    except Exception:
                        time_display = "00:00:00"
                    timestamp_display = f"{date_display} {time_display}"
                    log_title = (
                        entry.get("title")
                        or str(entry.get("progress", "Milestone"))[:40]
                    )
                    expander_label = f"[{date_display}] {proj_name} — {log_title}"
                    with st.expander(expander_label, expanded=False):
                        st.markdown(f"**Timestamp:** `{timestamp_display}`")
                        st.markdown(
                            f"**Progress / Milestone:**\n{entry.get('progress') or 'N/A'}"
                        )
                        st.markdown(
                            f"**Bugs / Challenges:**\n{entry.get('bugs') or 'N/A'}"
                        )
                        st.markdown(
                            f"**Learnings / Insights:**\n{entry.get('learnings') or 'N/A'}"
                        )

                        confirm_del_key = f"confirm_del_{entry_id}"
                        arm_time_key = f"arm_time_log_{entry_id}"
                        is_log_armed = st.session_state.get(confirm_del_key, False)
                        if not is_log_armed:
                            if st.button(
                                "Delete",
                                key=f"del_log_{entry_id}",
                                use_container_width=True,
                            ):
                                st.session_state[confirm_del_key] = True
                                st.session_state[arm_time_key] = time.time()
                                st.rerun()
                        else:

                            def do_delete(rid):
                                try:
                                    client = get_client()
                                    if "access_token" in st.session_state:
                                        client.auth.set_session(
                                            st.session_state["access_token"],
                                            st.session_state.get("refresh_token", ""),
                                        )
                                    client.table("engineering_log").delete().eq(
                                        "id", rid
                                    ).eq("user_id", user["id"]).execute()
                                    st.session_state[confirm_del_key] = False
                                    st.session_state.pop(arm_time_key, None)
                                    st.success("Log entry deleted successfully.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to delete log entry: {e}")

                            def disarm(rid):
                                st.session_state[confirm_del_key] = False
                                st.session_state.pop(arm_time_key, None)
                                st.rerun()

                            row_id = entry_id
                            ca, cb = st.columns(2)
                            with ca:
                                if st.button(
                                    "Confirm",
                                    key=f"arm_confirm_{row_id}",
                                    type="primary",
                                    use_container_width=True,
                                ):
                                    do_delete(row_id)
                            with cb:
                                if st.button(
                                    "Cancel",
                                    key=f"arm_cancel_{row_id}",
                                    use_container_width=True,
                                ):
                                    disarm(row_id)

            st.markdown("---")
            all_confirm_key = "confirm_delete_all_logs"
            if not st.session_state.get(all_confirm_key, False):
                if st.button("Delete ALL my logs", key="btn_delete_all_logs"):
                    st.session_state[all_confirm_key] = True
                    st.rerun()
            else:
                with st.expander("Confirm delete all", expanded=True):
                    st.warning(
                        "Are you sure you want to delete ALL your engineering logs? This cannot be undone."
                    )
                    col_all1, col_all2 = st.columns(2)
                    with col_all1:
                        if st.button(
                            "Delete",
                            key="btn_conf_delete_all",
                            type="primary",
                            use_container_width=True,
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
                        if st.button(
                            "Cancel",
                            key="btn_canc_delete_all",
                            use_container_width=True,
                        ):
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
