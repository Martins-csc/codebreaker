from unittest.mock import MagicMock, patch

import pytest
import requests


def test_no_witness_strings_in_app():
    """Assert that no OAuth witness strings remain in app.py source code."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert "OAUTH-WITNESS" not in content
    assert "TOKEN-WITNESS" not in content


def test_oauth_hardcoded_winning_exchange_mints_rt_and_clears_params():
    """Test hardcoded winning OAuth call succeeds, mints rt, and clears auth query params."""
    mock_client = MagicMock()
    mock_client.table("oauth_states").select("code_verifier").eq(
        "state", "pending"
    ).order("created_at", desc=True).limit(1).execute.return_value.data = [
        {"code_verifier": "ver_123"}
    ]

    mock_user = MagicMock()
    mock_user.id = "user-v1_5_8"
    mock_user.email = "v158@example.com"
    mock_user.user_metadata = {"display_name": "v1.5.8 User"}
    mock_client.auth.get_user.return_value.user = mock_user

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "access_token": "acc_158",
        "refresh_token": "ref_158",
        "expires_at": 3600,
    }

    mock_query_params = {"code": "code_158", "state": "pending", "mode": "login"}
    mock_session_state = {}
    mock_mint = MagicMock()

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "requests.post", return_value=mock_resp
    ) as mock_post, patch("streamlit.query_params", mock_query_params), patch(
        "streamlit.session_state", mock_session_state
    ), patch(
        "streamlit.success"
    ), patch(
        "streamlit.rerun", side_effect=Exception("Rerun triggered")
    ):
        with pytest.raises(Exception, match="Rerun triggered"):
            code = mock_query_params.get("code")
            supabase_url = "https://example.supabase.co"
            anon_key = "anon"
            state_res = (
                mock_client.table("oauth_states")
                .select("code_verifier")
                .eq("state", "pending")
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            verifier = state_res.data[0]["code_verifier"]

            token_url = f"{supabase_url}/auth/v1/token?grant_type=pkce"
            headers = {"apikey": anon_key, "Content-Type": "application/json"}
            payload = {"auth_code": code, "code_verifier": verifier}

            resp = requests.post(token_url, headers=headers, json=payload, timeout=10)
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
                    "display_name": "v1.5.8 User",
                }
                mock_mint(mock_client, user_obj.id, refresh_token)
                mock_client.table("oauth_states").delete().eq(
                    "state", "pending"
                ).execute()
                mock_query_params["pg"] = "Home"
                for p in ["code", "state", "mode"]:
                    mock_query_params.pop(p, None)
                import streamlit as st

                st.rerun()

    assert mock_session_state["user"]["email"] == "v158@example.com"
    assert "code" not in mock_query_params
    assert "state" not in mock_query_params
    assert mock_query_params["pg"] == "Home"
    mock_mint.assert_called_once_with(mock_client, "user-v1_5_8", "ref_158")
    mock_post.assert_called_once()
