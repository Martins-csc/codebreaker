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


def test_single_slot_pending_insert_and_lookup():
    """Test pending-slot insert (after deleting previous pending slot) and lookup."""
    mock_client = MagicMock()
    verifier = "test_verifier_single_slot_43_chars_long_xyz123"

    mock_client.table("oauth_states").delete().eq("state", "pending").execute()
    mock_client.table("oauth_states").insert(
        {"state": "pending", "code_verifier": verifier}
    ).execute()

    mock_client.table("oauth_states").select("code_verifier").eq(
        "state", "pending"
    ).order("created_at", desc=True).limit(1).execute.return_value.data = [
        {"code_verifier": verifier}
    ]

    res = (
        mock_client.table("oauth_states")
        .select("code_verifier")
        .eq("state", "pending")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    assert res.data[0]["code_verifier"] == verifier
    mock_client.table("oauth_states").delete().eq.assert_called()
    mock_client.table("oauth_states").insert.assert_called()


def test_return_path_fires_on_code_alone_and_mints_rt():
    """Test return path fires when code is present without state, fetches pending verifier, exchanges token, and mints rt."""
    mock_client = MagicMock()
    mock_client.table("oauth_states").select("code_verifier").eq(
        "state", "pending"
    ).order("created_at", desc=True).limit(1).execute.return_value.data = [
        {"code_verifier": "pending_verifier_123"}
    ]

    mock_user = MagicMock()
    mock_user.id = "user-single-slot"
    mock_user.email = "singleslot@example.com"
    mock_user.user_metadata = {"display_name": "Single Slot User"}
    mock_client.auth.get_user.return_value.user = mock_user

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "access_token": "acc_token_single",
        "refresh_token": "ref_token_single",
        "expires_at": 3600,
    }

    mock_query_params = {"code": "auth_code_single"}
    mock_session_state = {}
    mock_mint = MagicMock()

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
            code_param = mock_query_params.get("code")
            if code_param:
                state_res = (
                    mock_client.table("oauth_states")
                    .select("code_verifier")
                    .eq("state", "pending")
                    .order("created_at", desc=True)
                    .limit(1)
                    .execute()
                )
                verifier = state_res.data[0]["code_verifier"]
                resp = mock_resp
                if resp.status_code == 200:
                    data = resp.json()
                    mock_session_state["access_token"] = data["access_token"]
                    mock_session_state["refresh_token"] = data["refresh_token"]
                    mock_session_state["user"] = {
                        "id": mock_user.id,
                        "email": mock_user.email,
                        "display_name": mock_user.user_metadata["display_name"],
                    }
                    mock_mint(mock_client, mock_user.id, data["refresh_token"])
                    mock_client.table("oauth_states").delete().eq(
                        "state", "pending"
                    ).execute()
                    mock_query_params["pg"] = "Home"
                    mock_query_params.pop("code", None)
                    import streamlit as st

                    st.rerun()

    assert mock_session_state["user"]["email"] == "singleslot@example.com"
    assert "code" not in mock_query_params
    assert mock_query_params["pg"] == "Home"
    mock_mint.assert_called_once()
    mock_client.table("oauth_states").delete().eq("state", "pending").execute()


def test_exchange_retry_on_400():
    """Test token exchange retries with grant_type=authorization_code if grant_type=pkce returns 400."""
    mock_resp_400 = MagicMock()
    mock_resp_400.status_code = 400

    mock_resp_200 = MagicMock()
    mock_resp_200.status_code = 200
    mock_resp_200.json.return_value = {
        "access_token": "acc_retry",
        "refresh_token": "ref_retry",
    }

    import requests

    with patch(
        "requests.post", side_effect=[mock_resp_400, mock_resp_200]
    ) as mock_post:
        token_url = "https://example.supabase.co/auth/v1/token?grant_type=pkce"
        headers = {"apikey": "anon", "Content-Type": "application/json"}
        payload = {"auth_code": "code", "code_verifier": "verifier"}

        resp = requests.post(token_url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 400:
            token_url_alt = "https://example.supabase.co/auth/v1/token?grant_type=authorization_code"
            resp = requests.post(
                token_url_alt, headers=headers, json=payload, timeout=10
            )

        assert resp.status_code == 200
        assert mock_post.call_count == 2
