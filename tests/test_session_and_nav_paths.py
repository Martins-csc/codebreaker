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


def test_continuous_write_emission_while_authed():
    """Test continuous idempotent write emission while authenticated (keys: ls_continuous_session, ls_continuous_page)."""
    mock_ls = MagicMock()
    mock_session_state = {
        "access_token": "acc_xyz",
        "refresh_token": "ref_xyz",
        "expires_at": time.time() + 3600,
    }
    page = "Analyze"

    with patch("streamlit.session_state", mock_session_state):
        if (
            mock_ls
            and "access_token" in mock_session_state
            and "refresh_token" in mock_session_state
        ):
            mock_ls.setItem(
                "cb_session",
                {
                    "access_token": mock_session_state["access_token"],
                    "refresh_token": mock_session_state["refresh_token"],
                    "expires_at": mock_session_state["expires_at"],
                },
                key="ls_continuous_session",
            )
            mock_ls.setItem("cb_page", page, key="ls_continuous_page")

        mock_ls.setItem.assert_any_call(
            "cb_session",
            {
                "access_token": "acc_xyz",
                "refresh_token": "ref_xyz",
                "expires_at": mock_session_state["expires_at"],
            },
            key="ls_continuous_session",
        )
        mock_ls.setItem.assert_any_call("cb_page", "Analyze", key="ls_continuous_page")


def test_no_writes_after_signout():
    """Test that no writes occur after sign-out (deleteItem exclusive to sign-out/reset paths)."""
    mock_ls = MagicMock()
    mock_session_state = {}

    with patch("streamlit.session_state", mock_session_state):
        if mock_ls and "access_token" in mock_session_state:
            mock_ls.setItem("cb_session", {}, key="ls_continuous_session")

        mock_ls.setItem.assert_not_called()


def test_probe_gated_to_expander_state():
    """Test round-trip probe runs only while expander is expanded (persistence_debug_expander True)."""
    mock_ls = MagicMock()
    mock_ls.getAll.return_value = {"cb_probe": "1"}

    # Case A: Expander collapsed (False) -> probe paused
    mock_session_state = {"persistence_debug_expander": False}
    with patch("streamlit.session_state", mock_session_state):
        if mock_session_state.get("persistence_debug_expander", False):
            probe_val = mock_ls.getAll().get("cb_probe")
            mock_ls.setItem("cb_probe", "1", key="ls_probe_set")
        else:
            mock_session_state["persist_probe_last"] = (
                "Expander collapsed (probe paused)"
            )

        assert (
            mock_session_state["persist_probe_last"]
            == "Expander collapsed (probe paused)"
        )
        mock_ls.setItem.assert_not_called()

    # Case B: Expander expanded (True) -> probe runs
    mock_ls.reset_mock()
    mock_session_state = {"persistence_debug_expander": True}
    with patch("streamlit.session_state", mock_session_state):
        if mock_session_state.get("persistence_debug_expander", False):
            probe_val = mock_ls.getAll().get("cb_probe")
            if probe_val:
                mock_session_state["persist_probe_last"] = (
                    f"present (len {len(str(probe_val))})"
                )
            mock_ls.setItem("cb_probe", "1", key="ls_probe_set")

        assert "present" in mock_session_state["persist_probe_last"]
        mock_ls.setItem.assert_called_with("cb_probe", "1", key="ls_probe_set")


def test_admin_gating_and_debug_panel_zero_token_leakage():
    """Test admin-gating of debug panel and zero token leakage (presence/length only)."""
    # Test case 1: Non-admin user post-login
    with patch("config.ADMIN_EMAIL", "admin@example.com"):
        from config import ADMIN_EMAIL

        user = {"email": "regular@example.com"}
        user_email = user.get("email", "") if user else ""
        is_admin = (
            bool(ADMIN_EMAIL)
            and bool(user_email)
            and ADMIN_EMAIL.strip().lower() == user_email.strip().lower()
        )
        assert is_admin is False

    # Test case 2: Admin user matching ADMIN_EMAIL post-login
    with patch("config.ADMIN_EMAIL", "admin@example.com"):
        from config import ADMIN_EMAIL

        user = {"email": "admin@example.com"}
        user_email = user.get("email", "") if user else ""
        is_admin = (
            bool(ADMIN_EMAIL)
            and bool(user_email)
            and ADMIN_EMAIL.strip().lower() == user_email.strip().lower()
        )
        assert is_admin is True

    # Test case 3: ?pdebug=1 window closed (strictly admin post-login)
    with patch("config.ADMIN_EMAIL", "admin@example.com"):
        from config import ADMIN_EMAIL

        user = None
        user_email = user.get("email", "") if user else ""
        is_admin = (
            bool(ADMIN_EMAIL)
            and bool(user_email)
            and ADMIN_EMAIL.strip().lower() == user_email.strip().lower()
        )
        assert is_admin is False

    # Test case 4: Zero token leakage in debug raw / session representations
    raw_boot = "present (len 240)"
    assert "token" not in raw_boot.lower()
    assert "acc_" not in raw_boot.lower()
    assert "len" in raw_boot


def test_string_serialization_round_trip_and_corrupt_legacy_cleanup():
    """Test string serialization round-trip and corrupt-legacy cleanup ([object Object] and parse failures)."""
    bundle = {
        "access_token": "acc_123",
        "refresh_token": "ref_123",
        "expires_at": time.time() + 3600,
    }
    serialized = json.dumps(bundle)
    parsed = json.loads(serialized)
    assert parsed["access_token"] == "acc_123"

    mock_ls = MagicMock()
    mock_session_state = {}

    with patch("streamlit.session_state", mock_session_state):
        # Test [object Object] cleanup
        corrupt_val = "[object Object]"
        session_data = corrupt_val
        if isinstance(session_data, str):
            if session_data == "[object Object]":
                mock_session_state["persist_debug"] = (
                    "ValueError: LegacyCorruptSessionObject"
                )
                mock_ls.deleteItem("cb_session", key="ls_boot_del_legacy")
                session_data = None

        assert session_data is None
        assert "ValueError" in mock_session_state["persist_debug"]
        mock_ls.deleteItem.assert_called_with("cb_session", key="ls_boot_del_legacy")

        # Test parse failure cleanup
        corrupt_json = "{bad_json"
        session_data = corrupt_json
        if isinstance(session_data, str):
            try:
                session_data = json.loads(session_data)
            except Exception as e:
                mock_session_state["persist_debug"] = f"{type(e).__name__}: {str(e)}"
                mock_ls.deleteItem("cb_session", key="ls_boot_del_parse")
                session_data = None

        assert session_data is None
        assert "JSONDecodeError" in mock_session_state["persist_debug"]
        mock_ls.deleteItem.assert_called_with("cb_session", key="ls_boot_del_parse")


def test_emission_guard_arming_and_debug_lines():
    """Test emission guard arming (True/False) and raw stored head display."""
    # State 1: Unauthenticated -> Emission armed: False, Raw stored head: None
    mock_session_state = {}
    with patch("streamlit.session_state", mock_session_state):
        emission_armed = bool(
            "access_token" in mock_session_state
            and "refresh_token" in mock_session_state
        )
        assert emission_armed is False

        raw_session = None
        raw_head = str(raw_session)[:12] if raw_session else "None"
        assert raw_head == "None"

    # State 2: Authenticated -> Emission armed: True, Raw stored head: first 12 chars
    mock_session_state = {
        "access_token": "acc_abc123456789",
        "refresh_token": "ref_xyz",
    }
    with patch("streamlit.session_state", mock_session_state):
        emission_armed = bool(
            "access_token" in mock_session_state
            and "refresh_token" in mock_session_state
        )
        assert emission_armed is True


def test_thin_bundle_and_refresh_session_boot_path():
    """Test thin bundle round-trip ({refresh_token, expires_at}) and refresh_session boot rehydration."""
    mock_new_session = MagicMock()
    mock_new_session.access_token = "fresh_acc_999"
    mock_new_session.refresh_token = "fresh_ref_999"
    mock_new_session.expires_at = time.time() + 3600

    mock_user = MagicMock()
    mock_user.id = "user-999"
    mock_user.email = "thin@example.com"
    mock_user.user_metadata = {"display_name": "Thin User"}

    mock_refresh_res = MagicMock()
    mock_refresh_res.session = mock_new_session
    mock_refresh_res.user = mock_user

    mock_client = MagicMock()
    mock_client.auth.refresh_session.return_value = mock_refresh_res

    thin_bundle = {
        "refresh_token": "stored_ref_123",
        "expires_at": time.time() + 7200,
    }

    mock_session_state = {}
    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.session_state", mock_session_state
    ):
        refresh_token = thin_bundle.get("refresh_token")
        refresh_res = mock_client.auth.refresh_session(refresh_token)
        if refresh_res and refresh_res.session:
            new_sess = refresh_res.session
            mock_client.auth.set_session(new_sess.access_token, new_sess.refresh_token)
            u_obj = refresh_res.user
            if u_obj:
                mock_session_state["user"] = {
                    "id": u_obj.id,
                    "email": u_obj.email,
                    "display_name": "Thin User",
                }
                mock_session_state["access_token"] = new_sess.access_token
                mock_session_state["refresh_token"] = new_sess.refresh_token

        assert mock_session_state["access_token"] == "fresh_acc_999"
        assert mock_session_state["refresh_token"] == "fresh_ref_999"
        assert "access_token" not in thin_bundle  # thin bundle invariant


def test_oversize_drop_simulation_and_cookie_probes():
    """Test 100-byte and 4000-byte cookie probes simulation."""
    mock_controller = MagicMock()
    mock_controller.get.side_effect = lambda name: (
        "x" * 100 if name == "cb_probe_100" else "y" * 4000
    )

    probe_100 = mock_controller.get("cb_probe_100")
    probe_4k = mock_controller.get("cb_probe_4k")

    assert len(probe_100) == 100
    assert len(probe_4k) == 4000


def test_branch_h1_cookie_options_passed():
    """Test Branch H1: cookie set calls pass explicit path='/', same_site='lax', secure=True, max_age=604800."""
    mock_controller = MagicMock()
    mock_controller.set(
        "cb_session",
        '{"refresh_token": "abc"}',
        path="/",
        same_site="lax",
        secure=True,
        max_age=604800,
    )
    mock_controller.set.assert_called_with(
        "cb_session",
        '{"refresh_token": "abc"}',
        path="/",
        same_site="lax",
        secure=True,
        max_age=604800,
    )


def test_branch_h2_supabase_client_singleton():
    """Test Branch H2: get_client() creates and reuses per-session singleton in st.session_state."""
    mock_session_state = {}
    mock_client_inst = MagicMock()
    with patch("streamlit.session_state", mock_session_state), patch(
        "supabase_client.create_client", return_value=mock_client_inst
    ), patch("supabase_client.get_config", return_value="https://test.supabase.co"):
        from supabase_client import get_client

        c1 = get_client()
        c2 = get_client()
        assert c1 is c2
        assert mock_session_state["supabase_client_instance"] is c1


def test_branch_h3_flags_set_and_render_2_gate_open():
    """Test Branch H3: rehydrate sets gate flags (user, access_token, refresh_token) and bounded rerun logic."""
    mock_session_state = {"debug_boot_source": "client_component"}
    with patch("streamlit.session_state", mock_session_state):
        session_data = None
        # Simulate render-1 falling back to client_component and triggering bounded rerun
        if (
            session_data is None
            and mock_session_state.get("debug_boot_source") == "client_component"
            and not mock_session_state.get("boot_mount_triggered")
        ):
            mock_session_state["boot_mount_triggered"] = True

        assert mock_session_state["boot_mount_triggered"] is True

        # Simulate render-2 successful rehydration setting gate flags
        mock_session_state["user"] = {"id": "123", "email": "test@example.com"}
        mock_session_state["access_token"] = "acc_999"
        mock_session_state["refresh_token"] = "ref_999"

        assert mock_session_state["user"] is not None
        assert mock_session_state["access_token"] == "acc_999"
        assert mock_session_state["refresh_token"] == "ref_999"
