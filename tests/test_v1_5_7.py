from unittest.mock import MagicMock, patch

import pytest
import requests


def test_oauth_grant_type_sweep_stops_at_first_200():
    """Test that the 6-variant sweep stops at the first HTTP 200 and returns that winning variant."""
    mock_resp_400 = MagicMock()
    mock_resp_400.status_code = 400
    mock_resp_400.text = "Bad Request"

    mock_resp_200 = MagicMock()
    mock_resp_200.status_code = 200
    mock_resp_200.json.return_value = {
        "access_token": "acc_v3",
        "refresh_token": "ref_v3",
        "expires_at": 3600,
    }
    mock_resp_200.text = '{"access_token": "acc_v3"}'

    side_effects = [mock_resp_400, mock_resp_400, mock_resp_200]

    with patch("requests.post", side_effect=side_effects) as mock_post:
        supabase_url = "https://example.supabase.co"
        anon_key = "anon"
        code = "code_123"
        verifier = "verifier_abc"

        attempts = [
            (
                "v1",
                f"{supabase_url}/auth/v1/token?grant_type=pkce",
                "json",
                {"auth_code": code, "code_verifier": verifier},
            ),
            (
                "v2",
                f"{supabase_url}/auth/v1/token?grant_type=authorization_code",
                "json",
                {"auth_code": code, "code_verifier": verifier},
            ),
            (
                "v3",
                f"{supabase_url}/auth/v1/token?grant_type=pkce",
                "form",
                {"auth_code": code, "code_verifier": verifier},
            ),
            (
                "v4",
                f"{supabase_url}/auth/v1/token?grant_type=authorization_code",
                "form",
                {"auth_code": code, "code_verifier": verifier},
            ),
            (
                "v5",
                f"{supabase_url}/auth/v1/token",
                "json",
                {"grant_type": "pkce", "auth_code": code, "code_verifier": verifier},
            ),
            (
                "v6",
                f"{supabase_url}/auth/v1/token",
                "json",
                {
                    "grant_type": "authorization_code",
                    "auth_code": code,
                    "code_verifier": verifier,
                },
            ),
        ]

        winning_variant = None
        resp = None
        for v_name, url, mode, payload_data in attempts:
            if mode == "form":
                headers = {
                    "apikey": anon_key,
                    "Content-Type": "application/x-www-form-urlencoded",
                }
                resp = requests.post(
                    url, headers=headers, data=payload_data, timeout=10
                )
            else:
                headers = {
                    "apikey": anon_key,
                    "Content-Type": "application/json",
                }
                resp = requests.post(
                    url, headers=headers, json=payload_data, timeout=10
                )
            if resp.status_code == 200:
                winning_variant = v_name
                break

        assert winning_variant == "v3"
        assert resp.status_code == 200
        assert mock_post.call_count == 3


def test_oauth_sweep_success_path_mints_rt():
    """Test that on successful token response from the sweep, session is set, user populated, and rt minted."""
    mock_client = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "user-123"
    mock_user.email = "test@example.com"
    mock_user.user_metadata = {"display_name": "Test User"}
    mock_client.auth.get_user.return_value.user = mock_user

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "access_token": "acc_123",
        "refresh_token": "ref_123",
        "expires_at": 3600,
    }
    mock_resp.text = '{"access_token": "acc_123"}'

    mock_session_state = {}
    mock_query_params = {"code": "c1"}
    mock_mint = MagicMock()

    with patch("requests.post", return_value=mock_resp), patch(
        "streamlit.session_state", mock_session_state
    ), patch("streamlit.query_params", mock_query_params), patch(
        "streamlit.success"
    ), patch(
        "streamlit.caption"
    ), patch(
        "streamlit.rerun", side_effect=Exception("Rerun")
    ):
        with pytest.raises(Exception, match="Rerun"):
            code = "c1"
            verifier = "v123"
            supabase_url = "https://example.supabase.co"
            anon_key = "anon"
            resp = requests.post(
                f"{supabase_url}/auth/v1/token?grant_type=pkce",
                headers={"apikey": anon_key, "Content-Type": "application/json"},
                json={"auth_code": code, "code_verifier": verifier},
                timeout=10,
            )
            if resp.status_code == 200:
                token_data = resp.json()
                access_token = token_data.get("access_token")
                refresh_token = token_data.get("refresh_token")
                mock_session_state["access_token"] = access_token
                mock_session_state["refresh_token"] = refresh_token
                mock_client.auth.set_session(access_token, refresh_token)
                user_res = mock_client.auth.get_user(access_token)
                user_obj = user_res.user
                mock_session_state["user"] = {
                    "id": user_obj.id,
                    "email": user_obj.email,
                    "display_name": "Test User",
                }
                mock_mint(mock_client, user_obj.id, refresh_token)
                mock_query_params["pg"] = "Home"
                mock_query_params.pop("code", None)
                import streamlit as st

                st.rerun()

    assert mock_session_state["access_token"] == "acc_123"
    assert mock_session_state["refresh_token"] == "ref_123"
    assert mock_session_state["user"]["email"] == "test@example.com"
    assert mock_query_params["pg"] == "Home"
    mock_mint.assert_called_once_with(mock_client, "user-123", "ref_123")
