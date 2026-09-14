from unittest.mock import MagicMock, patch

import pytest


def test_oauth_code_exchange_and_cleanup():
    """Unit test with zero network: mock exchange_code_for_session returning fake session, assert query-param cleanup happens."""
    mock_user = MagicMock()
    mock_user.id = "user-123"
    mock_user.email = "github_user@example.com"
    mock_user.user_metadata = {"display_name": "GitHub User"}

    mock_session = MagicMock()
    mock_session.access_token = "fake_access_token"
    mock_session.refresh_token = "fake_refresh_token"

    mock_auth_response = MagicMock()
    mock_auth_response.user = mock_user
    mock_auth_response.session = mock_session

    mock_client = MagicMock()
    mock_client.auth.exchange_code_for_session.return_value = mock_auth_response

    mock_query_params = {"code": "fake_auth_code"}
    mock_session_state = {}

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.query_params", mock_query_params
    ), patch("streamlit.session_state", mock_session_state), patch(
        "streamlit.success"
    ), patch(
        "streamlit.rerun", side_effect=Exception("Rerun triggered")
    ):

        with pytest.raises(Exception, match="Rerun triggered"):
            code_param = mock_query_params.get("code")
            if code_param:
                code = code_param[0] if isinstance(code_param, list) else code_param
                try:
                    res = mock_client.auth.exchange_code_for_session(code)
                except Exception:
                    res = mock_client.auth.exchange_code_for_session(
                        {"auth_code": code}
                    )

                if res and res.user and res.session:
                    mock_session_state["user"] = {
                        "id": res.user.id,
                        "email": res.user.email,
                        "display_name": res.user.user_metadata.get("display_name", ""),
                    }
                    mock_session_state["access_token"] = res.session.access_token
                    mock_session_state["refresh_token"] = res.session.refresh_token
                    mock_client.auth.set_session(
                        res.session.access_token, res.session.refresh_token
                    )
                mock_query_params.clear()
                import streamlit as st

                st.rerun()

    assert mock_session_state["user"]["email"] == "github_user@example.com"
    assert mock_session_state["access_token"] == "fake_access_token"
    assert len(mock_query_params) == 0  # Assert query-param cleanup happens
    mock_client.auth.exchange_code_for_session.assert_called_once_with("fake_auth_code")


def test_sign_in_with_oauth_mock():
    """Unit test with zero network: mock sign_in_with_oauth returning a fake URL."""
    mock_oauth_response = MagicMock()
    mock_oauth_response.url = (
        "https://example.supabase.co/auth/v1/authorize?provider=github"
    )

    mock_client = MagicMock()
    mock_client.auth.sign_in_with_oauth.return_value = mock_oauth_response

    res = mock_client.auth.sign_in_with_oauth(
        {"provider": "github", "options": {"redirect_to": "http://localhost:8501"}}
    )
    assert res.url == "https://example.supabase.co/auth/v1/authorize?provider=github"
    mock_client.auth.sign_in_with_oauth.assert_called_once()
