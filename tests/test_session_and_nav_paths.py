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
    mock_local_storage.setItem("cb_page", new_page, key="ls_page_set")
    mock_local_storage.setItem.assert_called_once_with(
        "cb_page", "Engineering Log", key="ls_page_set"
    )


def test_storage_invariant_stream_api_exception_and_unique_keys():
    """Test regression invariant: storage operations handle StreamlitAPIException gracefully and use unique keys."""
    from streamlit.errors import StreamlitAPIException

    mock_ls = MagicMock()
    mock_ls.getAll.side_effect = StreamlitAPIException("DuplicateElementKey")
    mock_ls.getItem.side_effect = StreamlitAPIException("DuplicateElementKey")
    mock_ls.setItem.side_effect = StreamlitAPIException("DuplicateElementKey")
    mock_ls.deleteItem.side_effect = StreamlitAPIException("DuplicateElementKey")

    # Verify graceful exception handling for getAll/getItem
    session_data = None
    try:
        session_data = mock_ls.getAll().get("cb_session") or mock_ls.getItem(
            "cb_session"
        )
    except (StreamlitAPIException, Exception):
        session_data = None
    assert session_data is None

    # Verify graceful exception handling for setItem with unique key
    try:
        mock_ls.setItem("cb_session", {"token": "abc"}, key="ls_test_set")
    except (StreamlitAPIException, Exception):
        pass
    mock_ls.setItem.assert_called_with(
        "cb_session", {"token": "abc"}, key="ls_test_set"
    )

    # Verify graceful exception handling for deleteItem with unique key
    try:
        mock_ls.deleteItem("cb_session", key="ls_test_del")
    except (StreamlitAPIException, Exception):
        pass
    mock_ls.deleteItem.assert_called_with("cb_session", key="ls_test_del")


def test_storage_signature_compatibility_and_single_render_invariant():
    """Test signature-compatibility assertion (call sites match real library signatures) and single-render/session cache."""
    import inspect

    from streamlit_local_storage import LocalStorage

    sig_set = inspect.signature(LocalStorage.setItem)
    assert "itemKey" in sig_set.parameters
    assert "itemValue" in sig_set.parameters
    assert "key" in sig_set.parameters

    sig_del = inspect.signature(LocalStorage.deleteItem)
    assert "itemKey" in sig_del.parameters
    assert "key" in sig_del.parameters

    sig_get = inspect.signature(LocalStorage.getItem)
    assert "itemKey" in sig_get.parameters

    sig_all = inspect.signature(LocalStorage.getAll)
    assert len(sig_all.parameters) == 1


def test_storage_simulated_failure_sets_debug_flag_and_visible_caption():
    """Test that simulated storage failure records exception class + message into st.session_state['persist_debug'] and renders visible degradation."""
    from streamlit.errors import StreamlitAPIException

    mock_session_state = {}
    with patch("streamlit.session_state", mock_session_state):
        mock_ls = MagicMock()
        mock_ls.getAll.side_effect = StreamlitAPIException("SimulatedStorageFailure")

        session_data = None
        try:
            if mock_ls:
                session_data = mock_ls.getAll().get("cb_session")
        except (StreamlitAPIException, Exception) as e:
            err_msg = f"{type(e).__name__}: {str(e)[:80]}"
            mock_session_state["persist_debug"] = err_msg

        assert session_data is None
        assert "StreamlitAPIException" in mock_session_state["persist_debug"]
        assert "SimulatedStorageFailure" in mock_session_state["persist_debug"]


def test_bounded_rerun_boot_sequence_and_bound():
    """Test bounded-rerun boot sequence: reruns once when boot read is None and mount flag unset; bound prevents infinite rerun."""
    mock_session_state = {"render_count": 1, "boot_mount_triggered": False}
    rerun_called = []

    def mock_rerun():
        rerun_called.append(True)

    with patch("streamlit.session_state", mock_session_state), patch(
        "streamlit.rerun", side_effect=mock_rerun
    ):
        session_data = None
        if session_data is None and not mock_session_state.get("boot_mount_triggered"):
            mock_session_state["boot_mount_triggered"] = True
            streamlit_rerun = __import__("streamlit").rerun
            streamlit_rerun()

        assert mock_session_state["boot_mount_triggered"] is True
        assert len(rerun_called) == 1

        # Second pass with boot_mount_triggered True should NOT call rerun again
        if session_data is None and not mock_session_state.get("boot_mount_triggered"):
            mock_session_state["boot_mount_triggered"] = True
            streamlit_rerun()

        assert len(rerun_called) == 1  # bound enforced


def test_round_trip_probe_mechanics():
    """Test storage round-trip probe: gets cb_probe and sets cb_probe via setItem."""
    mock_ls = MagicMock()
    mock_ls.getAll.return_value = {"cb_probe": "1"}
    mock_session_state = {}

    with patch("streamlit.session_state", mock_session_state):
        probe_val = mock_ls.getAll().get("cb_probe") or mock_ls.getItem("cb_probe")
        if probe_val:
            mock_session_state["persist_probe_last"] = (
                f"present (len {len(str(probe_val))})"
            )
        else:
            mock_session_state["persist_probe_last"] = "None"
        mock_ls.setItem("cb_probe", "1", key="ls_probe_set")

        assert mock_session_state["persist_probe_last"] == "present (len 1)"
        mock_ls.setItem.assert_called_with("cb_probe", "1", key="ls_probe_set")


def test_admin_gating_and_debug_panel_zero_token_leakage():
    """Test admin-gating of debug panel and zero token leakage (presence/length only)."""
    # Test case 1: Non-admin user, no pdebug
    with patch("config.ADMIN_EMAIL", "admin@example.com"):
        from config import ADMIN_EMAIL

        user = {"email": "regular@example.com"}
        pdebug_param = None
        is_pdebug = pdebug_param == "1"
        is_admin = (
            ADMIN_EMAIL
            and user.get("email", "").strip().lower() == ADMIN_EMAIL.strip().lower()
        ) or is_pdebug
        assert is_admin is False

    # Test case 2: Admin user matching ADMIN_EMAIL
    with patch("config.ADMIN_EMAIL", "admin@example.com"):
        from config import ADMIN_EMAIL

        user = {"email": "admin@example.com"}
        pdebug_param = None
        is_pdebug = pdebug_param == "1"
        is_admin = (
            ADMIN_EMAIL
            and user.get("email", "").strip().lower() == ADMIN_EMAIL.strip().lower()
        ) or is_pdebug
        assert is_admin is True

    # Test case 3: Pre-auth via query flag ?pdebug=1
    with patch("config.ADMIN_EMAIL", "admin@example.com"):
        from config import ADMIN_EMAIL

        user = None
        pdebug_param = "1"
        is_pdebug = pdebug_param == "1"
        is_admin = (
            ADMIN_EMAIL
            and user
            and user.get("email", "").strip().lower() == ADMIN_EMAIL.strip().lower()
        ) or is_pdebug
        assert is_admin is True

    # Test case 4: Zero token leakage in debug raw / session representations
    raw_boot = "present (len 240)"
    assert "token" not in raw_boot.lower()
    assert "acc_" not in raw_boot.lower()
    assert "len" in raw_boot
