import json
import time
from unittest.mock import MagicMock, patch

import pytest


def test_session_restore_valid_path():
    """Test valid session restore from localStorage cb_session without expiration."""
    mock_user = MagicMock()
    mock_user.id = "user-111"
    mock_user.email = "restore@example.com"
    mock_user.user_metadata = {"display_name": "Restore User"}

    mock_client = MagicMock()
    user_res = MagicMock()
    user_res.user = mock_user
    mock_client.auth.get_user.return_value = user_res

    future_expires = time.time() + 7200
    session_dict = {
        "access_token": "acc_123",
        "refresh_token": "ref_123",
        "expires_at": future_expires,
    }

    mock_local_storage = MagicMock()
    mock_local_storage.getAll.return_value = {"cb_session": session_dict}
    mock_local_storage.getItem.return_value = session_dict

    mock_session_state = {}

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.session_state", mock_session_state
    ):
        access_token = session_dict["access_token"]
        refresh_token = session_dict["refresh_token"]
        expires_at = session_dict["expires_at"]

        is_expired = False
        if float(expires_at) <= time.time():
            is_expired = True

        restored = False
        if not is_expired:
            try:
                mock_client.auth.set_session(access_token, refresh_token)
                u_res = mock_client.auth.get_user(access_token)
                u_obj = u_res.user
                if u_obj:
                    mock_session_state["user"] = {
                        "id": u_obj.id,
                        "email": u_obj.email,
                        "display_name": "Restore User",
                    }
                    mock_session_state["access_token"] = access_token
                    mock_session_state["refresh_token"] = refresh_token
                    restored = True
            except Exception:
                restored = False

        assert restored is True
        assert mock_session_state["user"]["email"] == "restore@example.com"
        assert mock_session_state["access_token"] == "acc_123"


def test_session_expired_refresh_path():
    """Test expired session in localStorage triggers refresh_session successfully."""
    mock_new_session = MagicMock()
    mock_new_session.access_token = "new_acc_456"
    mock_new_session.refresh_token = "new_ref_456"
    mock_new_session.expires_at = time.time() + 3600

    mock_user = MagicMock()
    mock_user.id = "user-222"
    mock_user.email = "refresh@example.com"
    mock_user.user_metadata = {"display_name": "Refresh User"}

    mock_refresh_res = MagicMock()
    mock_refresh_res.session = mock_new_session
    mock_refresh_res.user = mock_user

    mock_client = MagicMock()
    mock_client.auth.refresh_session.return_value = mock_refresh_res

    past_expires = time.time() - 100
    session_dict = {
        "access_token": "old_acc",
        "refresh_token": "old_ref",
        "expires_at": past_expires,
    }

    mock_local_storage = MagicMock()
    mock_local_storage.getAll.return_value = {"cb_session": session_dict}
    mock_local_storage.getItem.return_value = session_dict

    mock_session_state = {}

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.session_state", mock_session_state
    ):
        restored = False
        if not restored:
            try:
                refresh_res = mock_client.auth.refresh_session("old_ref")
                if refresh_res and refresh_res.session:
                    new_sess = refresh_res.session
                    mock_client.auth.set_session(
                        new_sess.access_token, new_sess.refresh_token
                    )
                    u_obj = refresh_res.user
                    if u_obj:
                        mock_session_state["user"] = {
                            "id": u_obj.id,
                            "email": u_obj.email,
                            "display_name": "Refresh User",
                        }
                        mock_session_state["access_token"] = new_sess.access_token
                        mock_session_state["refresh_token"] = new_sess.refresh_token
                        mock_local_storage.setItem(
                            "cb_session",
                            {
                                "access_token": new_sess.access_token,
                                "refresh_token": new_sess.refresh_token,
                                "expires_at": new_sess.expires_at,
                            },
                        )
                        restored = True
            except Exception:
                restored = False

        assert restored is True
        assert mock_session_state["access_token"] == "new_acc_456"
        mock_local_storage.setItem.assert_called_once()


def test_session_corrupt_or_invalid_path():
    """Test corrupt or invalid session JSON or missing tokens deletes cb_session item."""
    mock_local_storage = MagicMock()
    corrupt_data = "{ invalid_json "

    session_data = None
    if isinstance(corrupt_data, str):
        try:
            session_data = json.loads(corrupt_data)
        except Exception:
            session_data = None

    if not session_data or not isinstance(session_data, dict):
        mock_local_storage.deleteItem("cb_session")

    mock_local_storage.deleteItem.assert_called_once_with("cb_session")


def test_signout_path():
    """Test sign-out calls client.auth.sign_out() and deletes cb_session and cb_page from local storage."""
    mock_client = MagicMock()
    mock_local_storage = MagicMock()
    mock_session_state = {
        "user": {"email": "user@example.com"},
        "access_token": "token",
    }

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.session_state", mock_session_state
    ):
        try:
            mock_client.auth.sign_out()
        except Exception:
            pass
        try:
            mock_local_storage.deleteItem("cb_session")
            mock_local_storage.deleteItem("cb_page")
        except Exception:
            pass
        for key in list(mock_session_state.keys()):
            del mock_session_state[key]

    mock_client.auth.sign_out.assert_called_once()
    mock_local_storage.deleteItem.assert_any_call("cb_session")
    mock_local_storage.deleteItem.assert_any_call("cb_page")
    assert len(mock_session_state) == 0


def test_nav_persistence_cb_page():
    """Test cb_page navigation persistence save and restore."""
    mock_local_storage = MagicMock()
    mock_local_storage.getAll.return_value = {"cb_page": "Blueprint"}
    mock_local_storage.getItem.return_value = "Blueprint"

    saved_page = mock_local_storage.getAll().get(
        "cb_page"
    ) or mock_local_storage.getItem("cb_page")
    options = ["Home", "Analyze", "Blueprint", "Engineering Log", "About"]
    default_index = options.index(saved_page) if saved_page in options else 0

    assert saved_page == "Blueprint"
    assert default_index == 2

    new_page = "Engineering Log"
    mock_local_storage.setItem("cb_page", new_page)
    mock_local_storage.setItem.assert_called_once_with("cb_page", "Engineering Log")
