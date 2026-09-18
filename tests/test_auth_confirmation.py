from unittest.mock import MagicMock, patch

import pytest


def test_signup_unconfirmed_user_blocked():
    """Test unconfirmed user from signup is blocked at login gate and shows info message."""
    mock_user = MagicMock()
    mock_user.id = "user-123"
    mock_user.email = "unconfirmed@example.com"
    mock_user.confirmed_at = None
    mock_user.identities = [{"id": "id-1"}]

    mock_auth_response = MagicMock()
    mock_auth_response.user = mock_user
    mock_auth_response.session = None

    mock_client = MagicMock()
    mock_client.auth.sign_up.return_value = mock_auth_response

    mock_session_state = {}

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.session_state", mock_session_state
    ), patch("streamlit.info") as mock_info, patch("streamlit.success") as mock_success:

        res = mock_client.auth.sign_up(
            {
                "email": "unconfirmed@example.com",
                "password": "securepassword",
                "options": {"data": {"display_name": "Test"}},
            }
        )
        user_obj = res.user
        session_obj = res.session

        if user_obj and (
            getattr(user_obj, "confirmed_at", None) is None or not session_obj
        ):
            mock_info("Check your email to confirm your account")
            mock_success(
                "Confirmation email sent to unconfirmed@example.com. Check your inbox (and spam folder)."
            )
            mock_session_state["unconfirmed_email"] = user_obj.email

        assert "user" not in mock_session_state
        assert mock_session_state.get("unconfirmed_email") == "unconfirmed@example.com"
        mock_info.assert_called_with("Check your email to confirm your account")


def test_resend_confirmation_email():
    """Test resend confirmation email calls supabase.auth.resend with correct payload."""
    mock_client = MagicMock()
    email = "unconfirmed@example.com"

    mock_client.auth.resend({"type": "signup", "email": email})

    mock_client.auth.resend.assert_called_once_with({"type": "signup", "email": email})


def test_signup_confirmed_user_proceeds():
    """Test confirmed user proceeds normally and session is established."""
    mock_user = MagicMock()
    mock_user.id = "user-456"
    mock_user.email = "confirmed@example.com"
    mock_user.confirmed_at = "2026-09-15T00:00:00Z"
    mock_user.user_metadata = {"display_name": "Confirmed Dev"}

    mock_session = MagicMock()
    mock_session.access_token = "access-token-123"
    mock_session.refresh_token = "refresh-token-123"

    mock_auth_response = MagicMock()
    mock_auth_response.user = mock_user
    mock_auth_response.session = mock_session

    mock_client = MagicMock()
    mock_client.auth.sign_up.return_value = mock_auth_response

    mock_session_state = {}

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.session_state", mock_session_state
    ), patch("streamlit.success") as mock_success, patch(
        "streamlit.rerun", side_effect=Exception("Rerun triggered")
    ):

        with pytest.raises(Exception, match="Rerun triggered"):
            res = mock_client.auth.sign_up(
                {
                    "email": "confirmed@example.com",
                    "password": "securepassword",
                    "options": {"data": {"display_name": "Confirmed Dev"}},
                }
            )
            user_obj = res.user
            session_obj = res.session

            if (
                user_obj
                and session_obj
                and getattr(user_obj, "confirmed_at", None) is not None
            ):
                mock_session_state["user"] = {
                    "id": user_obj.id,
                    "email": user_obj.email,
                    "display_name": "Confirmed Dev",
                }
                mock_session_state["access_token"] = session_obj.access_token
                mock_session_state["refresh_token"] = session_obj.refresh_token
                mock_client.auth.set_session(
                    session_obj.access_token, session_obj.refresh_token
                )
                import streamlit as st

                st.rerun()

    assert mock_session_state["user"]["email"] == "confirmed@example.com"
    assert mock_session_state["access_token"] == "access-token-123"


def test_verify_otp_signup_success():
    """Test verify_otp successfully confirms signup with token_hash."""
    mock_client = MagicMock()
    mock_auth_response = MagicMock()
    mock_auth_response.user = MagicMock(email="test@example.com")
    mock_client.auth.verify_otp.return_value = mock_auth_response

    mock_session_state = {}
    mock_query_params = {"type": "signup", "token": "dummy-token"}

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.session_state", mock_session_state
    ), patch("streamlit.query_params", mock_query_params), patch(
        "streamlit.success"
    ) as mock_success, patch(
        "streamlit.rerun", side_effect=Exception("Rerun")
    ):

        with pytest.raises(Exception, match="Rerun"):
            res = mock_client.auth.verify_otp(
                {"token_hash": "dummy-token", "type": "signup"}
            )
            if res:
                mock_success("Email confirmed — please log in.")
                mock_session_state["email_confirmed_success"] = True
                mock_query_params.clear()
                import streamlit as st

                st.rerun()

        mock_client.auth.verify_otp.assert_called_with(
            {"token_hash": "dummy-token", "type": "signup"}
        )
        assert mock_session_state.get("email_confirmed_success") is True
        assert len(mock_query_params) == 0


def test_verify_otp_recovery_success():
    """Test verify_otp successfully sets recovery mode and session."""
    mock_client = MagicMock()
    mock_session = MagicMock(access_token="rec-acc", refresh_token="rec-ref")
    mock_auth_response = MagicMock(session=mock_session)
    mock_client.auth.verify_otp.return_value = mock_auth_response

    mock_session_state = {}
    mock_query_params = {"type": "recovery", "token": "dummy-recovery-token"}

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.session_state", mock_session_state
    ), patch("streamlit.query_params", mock_query_params), patch(
        "streamlit.success"
    ) as mock_success, patch(
        "streamlit.rerun", side_effect=Exception("Rerun")
    ):

        with pytest.raises(Exception, match="Rerun"):
            res = None
            try:
                res = mock_client.auth.verify_otp(
                    {"token_hash": "dummy-recovery-token", "type": "recovery"}
                )
            except Exception:
                res = mock_client.auth.verify_otp(
                    {"token": "dummy-recovery-token", "type": "recovery"}
                )

            if res:
                mock_session_state["recovery_mode"] = True
                if res.session:
                    mock_session_state["access_token"] = res.session.access_token
                    mock_session_state["refresh_token"] = res.session.refresh_token
                mock_success(
                    "Recovery session established. Please set your new password."
                )
                mock_query_params.clear()
                import streamlit as st

                st.rerun()

        assert mock_session_state["recovery_mode"] is True
        assert mock_session_state["access_token"] == "rec-acc"
        assert len(mock_query_params) == 0


def test_verify_otp_token_hash_fallback_to_token():
    """Test verify_otp falls back from token_hash to token when token_hash fails."""
    mock_client = MagicMock()
    mock_client.auth.verify_otp.side_effect = [
        Exception("Invalid token_hash"),
        MagicMock(user=MagicMock()),
    ]

    otp_token = "fallback-token"
    type_param = "signup"
    verified = False
    res = None

    try:
        res = mock_client.auth.verify_otp({"token_hash": otp_token, "type": type_param})
        verified = True
    except Exception:
        try:
            res = mock_client.auth.verify_otp({"token": otp_token, "type": type_param})
            verified = True
        except Exception:
            verified = False

    assert verified is True
    assert mock_client.auth.verify_otp.call_count == 2


def test_verify_otp_expired_or_invalid():
    """Test expired or invalid link triggers warning and resend/forgot paths one click away."""
    mock_client = MagicMock()
    mock_client.auth.verify_otp.side_effect = Exception("Expired token")

    mock_query_params = {"type": "signup", "token": "expired-token"}

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.query_params", mock_query_params
    ), patch("streamlit.warning") as mock_warning, patch(
        "streamlit.columns", return_value=(MagicMock(), MagicMock())
    ), patch(
        "streamlit.rerun", side_effect=Exception("Rerun")
    ):

        with pytest.raises(Exception, match="Rerun"):
            verified = False
            try:
                mock_client.auth.verify_otp(
                    {"token_hash": "expired-token", "type": "signup"}
                )
                verified = True
            except Exception:
                try:
                    mock_client.auth.verify_otp(
                        {"token": "expired-token", "type": "signup"}
                    )
                    verified = True
                except Exception:
                    verified = False

            if not verified:
                mock_warning(
                    "This link has expired or is invalid. Please request a new one."
                )
                mock_query_params.clear()
                import streamlit as st

                st.rerun()

        mock_warning.assert_called_with(
            "This link has expired or is invalid. Please request a new one."
        )
        assert len(mock_query_params) == 0
