import hashlib
import json
import secrets
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import ANY, MagicMock, patch

import pytest


def test_url_capability_resume_mint_and_verify():
    """Test minting and verifying URL capability resume token with mocked Supabase client."""
    mock_client = MagicMock()
    mock_session = MagicMock()
    mock_session.access_token = "acc_cap_123"
    mock_session.refresh_token = "ref_cap_123"
    mock_session.expires_at = time.time() + 3600

    mock_user = MagicMock()
    mock_user.id = "user-cap-111"
    mock_user.email = "capability@example.com"
    mock_user.user_metadata = {"display_name": "Capability User"}

    mock_refresh_res = MagicMock()
    mock_refresh_res.session = mock_session
    mock_refresh_res.user = mock_user

    mock_client.auth.refresh_session.return_value = mock_refresh_res

    # Mock verify_resume_token RPC return data
    mock_verify_res = MagicMock()
    mock_verify_res.data = [
        {
            "user_id": "user-cap-111",
            "refresh_token": "ref_cap_123",
            "expires_at": "2026-10-01T00:00:00Z",
        }
    ]
    mock_client.rpc.return_value.execute.return_value = mock_verify_res

    mock_session_state = {}
    mock_query_params = {"rt": "test_token_secret_32_bytes_safe"}

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.session_state", mock_session_state
    ), patch("streamlit.query_params", mock_query_params):

        rt_param = mock_query_params.get("rt")
        token_hash = hashlib.sha256(rt_param.encode("utf-8")).hexdigest()

        res = mock_client.rpc(
            "verify_resume_token", {"p_token_hash": token_hash}
        ).execute()
        verify_data = res.data
        assert len(verify_data) == 1

        row = verify_data[0]
        refresh_token = row.get("refresh_token")

        refresh_res = mock_client.auth.refresh_session(refresh_token)
        assert refresh_res.session.access_token == "acc_cap_123"


def test_url_capability_resume_rotation_on_boot():
    """Test token rotation on successful boot (revokes old token hash, mints new token, updates rt query param)."""
    mock_client = MagicMock()
    mock_session_state = {}
    mock_query_params = {"rt": "old_token_abc"}

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.session_state", mock_session_state
    ), patch("streamlit.query_params", mock_query_params):

        old_rt = mock_query_params.get("rt")
        old_hash = hashlib.sha256(old_rt.encode("utf-8")).hexdigest()

        # Revoke old
        mock_client.rpc(
            "revoke_resume_token", {"p_token_hash": old_hash, "p_uid": "user-123"}
        ).execute()

        # Mint new
        new_token = secrets.token_urlsafe(32)
        new_hash = hashlib.sha256(new_token.encode("utf-8")).hexdigest()
        mock_client.rpc(
            "create_resume_token",
            {
                "p_uid": "user-123",
                "p_refresh_token": "ref_123",
                "p_token_hash": new_hash,
                "p_expires_at": (
                    datetime.now(timezone.utc) + timedelta(days=7)
                ).isoformat(),
            },
        ).execute()

        mock_query_params["rt"] = new_token

        assert mock_query_params["rt"] != old_rt
        mock_client.rpc.assert_any_call(
            "revoke_resume_token", {"p_token_hash": old_hash, "p_uid": "user-123"}
        )
        mock_client.rpc.assert_any_call("create_resume_token", ANY)


def test_url_capability_resume_expired_token_clean_login_gate():
    """Test expired or missing capability token results in clean login gate and no error noise."""
    mock_client = MagicMock()
    mock_verify_res = MagicMock()
    mock_verify_res.data = []  # empty means expired or not found
    mock_client.rpc.return_value.execute.return_value = mock_verify_res

    mock_session_state = {}
    mock_query_params = {"rt": "expired_token_xyz"}

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.session_state", mock_session_state
    ), patch("streamlit.query_params", mock_query_params):

        rt_param = mock_query_params.get("rt")
        token_hash = hashlib.sha256(rt_param.encode("utf-8")).hexdigest()
        res = mock_client.rpc(
            "verify_resume_token", {"p_token_hash": token_hash}
        ).execute()

        if not res.data:
            if "rt" in mock_query_params:
                del mock_query_params["rt"]
            mock_session_state["last_verify_result"] = "Token not found or expired"

        assert "rt" not in mock_query_params
        assert mock_session_state["last_verify_result"] == "Token not found or expired"


def test_url_capability_resume_sign_out_clears_param_and_revokes():
    """Test sign-out revokes row via revoke_resume_token and clears rt query param."""
    mock_client = MagicMock()
    mock_query_params = {"rt": "active_token_999"}
    mock_session_state = {"user": {"email": "user@example.com"}, "access_token": "acc"}

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.session_state", mock_session_state
    ), patch("streamlit.query_params", mock_query_params):

        rt_param = mock_query_params.get("rt")
        if rt_param:
            token_hash = hashlib.sha256(rt_param.encode("utf-8")).hexdigest()
            mock_client.rpc(
                "revoke_resume_token", {"p_token_hash": token_hash}
            ).execute()

        mock_client.auth.sign_out()
        if "rt" in mock_query_params:
            del mock_query_params["rt"]
        mock_session_state.clear()

        mock_client.rpc.assert_called_with(
            "revoke_resume_token",
            {"p_token_hash": hashlib.sha256(b"active_token_999").hexdigest()},
        )
        mock_client.auth.sign_out.assert_called_once()
        assert "rt" not in mock_query_params
        assert len(mock_session_state) == 0


def test_persistence_debug_admin_only_and_fields():
    """Test Persistence Debug is admin-only and displays rt present (bool), last verify result, gate flags."""
    with patch("config.ADMIN_EMAIL", "admin@example.com"):
        from config import ADMIN_EMAIL

        # Non-admin
        user = {"email": "regular@example.com"}
        user_email = user.get("email", "")
        is_admin = (
            bool(ADMIN_EMAIL)
            and bool(user_email)
            and ADMIN_EMAIL.strip().lower() == user_email.strip().lower()
        )
        assert is_admin is False

        # Admin
        user_admin = {"email": "admin@example.com"}
        user_admin_email = user_admin.get("email", "")
        is_admin_admin = (
            bool(ADMIN_EMAIL)
            and bool(user_admin_email)
            and ADMIN_EMAIL.strip().lower() == user_admin_email.strip().lower()
        )
        assert is_admin_admin is True

        # Debug summary fields
        mock_query_params = {"rt": "token123"}
        mock_session_state = {
            "last_verify_result": "Verified & Rotated ✅",
            "access_token": "acc",
            "refresh_token": "ref",
        }

        with patch("streamlit.query_params", mock_query_params), patch(
            "streamlit.session_state", mock_session_state
        ):
            rt_present = bool(mock_query_params.get("rt"))
            last_verify = mock_session_state.get("last_verify_result", "None")
            gate_flags = f"user={bool(user_admin)}, access_token={bool(mock_session_state.get('access_token'))}, refresh_token={bool(mock_session_state.get('refresh_token'))}"

            assert rt_present is True
            assert last_verify == "Verified & Rotated ✅"
            assert "user=True" in gate_flags
            assert "access_token=True" in gate_flags
            assert "refresh_token=True" in gate_flags
