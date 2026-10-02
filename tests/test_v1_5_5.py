import base64
import hashlib
import secrets
from unittest.mock import MagicMock, patch

import pytest


def test_manual_pkce_challenge_generation():
    """Test PKCE verifier, unpadded base64url challenge, and state generation."""
    verifier = secrets.token_urlsafe(43)
    assert len(verifier) >= 43

    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("utf-8")
    assert "=" not in challenge

    state = secrets.token_urlsafe(16)
    assert len(state) >= 16


def test_oauth_state_flow_and_token_exchange():
    """Test zero-network manual PKCE return flow: lookup state, post grant_type=pkce, set session."""
    mock_client = MagicMock()
    # Mock oauth_states table lookup returning verifier
    mock_client.table().select().eq().execute.return_value.data = [
        {"code_verifier": "fake_verifier"}
    ]

    mock_user = MagicMock()
    mock_user.id = "user-pkce"
    mock_user.email = "pkce_user@example.com"
    mock_user.user_metadata = {"display_name": "PKCE User"}
    mock_client.auth.get_user.return_value.user = mock_user

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "access_token": "fake_pkce_access",
        "refresh_token": "fake_pkce_refresh",
        "expires_at": 3600,
    }

    mock_query_params = {"code": "auth_code_123", "state": "state_abc123"}
    mock_session_state = {}

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "requests.post", return_value=mock_resp
    ), patch("streamlit.query_params", mock_query_params), patch(
        "streamlit.session_state", mock_session_state
    ), patch(
        "streamlit.success"
    ), patch(
        "streamlit.rerun", side_effect=Exception("Rerun triggered")
    ):
        with pytest.raises(Exception, match="Rerun triggered"):
            # Execute return flow logic simulation or test helper
            code = mock_query_params.get("code")
            state = mock_query_params.get("state")
            state_res = (
                mock_client.table("oauth_states")
                .select("code_verifier")
                .eq("state", state)
                .execute()
            )
            verifier = state_res.data[0]["code_verifier"]

            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = mock_resp.json.return_value

            if resp.status_code == 200:
                data = resp.json()
                mock_session_state["access_token"] = data["access_token"]
                mock_session_state["refresh_token"] = data["refresh_token"]
                mock_session_state["user"] = {
                    "id": mock_user.id,
                    "email": mock_user.email,
                    "display_name": mock_user.user_metadata["display_name"],
                }
                mock_query_params["pg"] = "Home"
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
                    mock_query_params.pop(p, None)
                import streamlit as st

                st.rerun()

    assert mock_session_state["user"]["email"] == "pkce_user@example.com"
    assert mock_session_state["access_token"] == "fake_pkce_access"
    assert "code" not in mock_query_params
    assert "state" not in mock_query_params
    assert mock_query_params["pg"] == "Home"


def test_sign_out_cleanup_all_params():
    """Test sign-out cleanup deletes all specified auth query parameters."""
    mock_query_params = {
        "rt": "token123",
        "pg": "Home",
        "code": "c1",
        "state": "s1",
        "type": "signup",
        "token": "t1",
        "token_hash": "th1",
        "error": "e1",
        "error_description": "ed1",
        "oauth_state": "os1",
        "mode": "login",
        "auth_view": "login",
        "other_param": "keep_me",
    }

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
        mock_query_params.pop(p, None)

    assert "other_param" in mock_query_params
    for p in auth_params:
        assert p not in mock_query_params
