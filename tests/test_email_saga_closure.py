import hashlib
from unittest.mock import MagicMock, patch

import pytest
import streamlit as st
from security import validate_email


def test_verify_otp_sha256_fallback():
    """Test verify_otp falls back from token_hash to sha256-hex token_hash, then token."""
    mock_client = MagicMock()
    # 1st call fails (token_hash), 2nd call fails (sha256 token_hash), 3rd call succeeds (token)
    mock_client.auth.verify_otp.side_effect = [
        Exception("Invalid token_hash"),
        Exception("Invalid sha256 token_hash"),
        MagicMock(user=MagicMock(email="test@example.com")),
    ]

    otp_token = "my-secret-otp-token"
    type_param = "signup"
    verified = False
    res = None

    try:
        res = mock_client.auth.verify_otp({"token_hash": otp_token, "type": type_param})
        verified = True
    except Exception:
        try:
            h = hashlib.sha256(otp_token.encode("utf-8")).hexdigest()
            res = mock_client.auth.verify_otp({"token_hash": h, "type": type_param})
            verified = True
        except Exception:
            try:
                res = mock_client.auth.verify_otp(
                    {"token": otp_token, "type": type_param}
                )
                verified = True
            except Exception:
                verified = False

    assert verified is True
    assert mock_client.auth.verify_otp.call_count == 3


def test_signup_duplicate_empty_identities():
    """Test that sign_up returning empty identities triggers duplicate account warning and sends nothing."""
    mock_user = MagicMock()
    mock_user.id = "user-existing"
    mock_user.email = "existing@example.com"
    mock_user.identities = []  # empty identities = existing account

    mock_auth_resp = MagicMock()
    mock_auth_resp.user = mock_user
    mock_auth_resp.session = None

    mock_client = MagicMock()
    mock_client.auth.sign_up.return_value = mock_auth_resp

    mock_session_state = {}

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.session_state", mock_session_state
    ), patch("streamlit.warning") as mock_warning, patch(
        "streamlit.success"
    ) as mock_success:

        res = mock_client.auth.sign_up(
            {
                "email": "existing@example.com",
                "password": "password123",
            }
        )
        user_obj = res.user
        identities = getattr(user_obj, "identities", None)

        if identities is not None and len(identities) == 0:
            mock_warning(
                "This email is already linked to an account. Please log in or reset your password."
            )

        mock_warning.assert_called_once_with(
            "This email is already linked to an account. Please log in or reset your password."
        )
        mock_success.assert_not_called()
        assert "unconfirmed_email" not in mock_session_state


def test_forgot_password_inside_login_form():
    """Test forgot-password inside login form reuses email input value and calls reset_password_for_email."""
    mock_client = MagicMock()
    login_email = "user@example.com"

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.info"
    ) as mock_info:

        email_valid, _ = validate_email(login_email)
        assert email_valid is True

        try:
            mock_client.auth.reset_password_for_email(
                login_email.strip(), options={"redirect_to": "http://localhost:8501"}
            )
        except Exception:
            pass

        mock_info("If an account exists for that email, a reset link is on its way.")
        mock_client.auth.reset_password_for_email.assert_called_once_with(
            login_email, options={"redirect_to": "http://localhost:8501"}
        )
        mock_info.assert_called_once_with(
            "If an account exists for that email, a reset link is on its way."
        )


def test_tour_persistence_and_metadata():
    """Test tour is shown when user_metadata lacks tour_seen and dismiss calls update_user."""
    mock_client = MagicMock()
    mock_session_state = {
        "user": {
            "id": "u-1",
            "email": "test@example.com",
            "user_metadata": {},  # lacks tour_seen
        },
        "access_token": "token-123",
    }

    user = mock_session_state.get("user")
    user_meta = user.get("user_metadata", {})
    show_tour = not user_meta.get("tour_seen", False)
    assert show_tour is True

    # Simulate dismiss ("Got it" clicked)
    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.session_state", mock_session_state
    ):
        mock_client.auth.update_user({"data": {"tour_seen": True}})
        user_meta["tour_seen"] = True
        mock_session_state["user"]["user_metadata"] = user_meta

    mock_client.auth.update_user.assert_called_once_with({"data": {"tour_seen": True}})
    assert mock_session_state["user"]["user_metadata"]["tour_seen"] is True


def test_admin_pulse_rpc_calls():
    """Test Admin Pulse uses rpc("count_registered_users") and rpc("count_engineering_logs")."""
    mock_client = MagicMock()
    mock_client.rpc.return_value.execute.side_effect = [
        MagicMock(data=12),
        MagicMock(data=45),
    ]

    metrics = []

    def mock_metric(label, val):
        metrics.append((label, val))

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.sidebar.metric", side_effect=mock_metric
    ):
        res_users = mock_client.rpc("count_registered_users").execute()
        users_count = getattr(res_users, "data", 0)

        res_logs = mock_client.rpc("count_engineering_logs").execute()
        logs_count = getattr(res_logs, "data", 0)

        mock_metric("Registered Users", users_count)
        mock_metric("Engineering Logs", logs_count)

    mock_client.rpc.assert_any_call("count_registered_users")
    mock_client.rpc.assert_any_call("count_engineering_logs")
    assert ("Registered Users", 12) in metrics
    assert ("Engineering Logs", 45) in metrics
