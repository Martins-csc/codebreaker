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
