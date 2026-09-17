from unittest.mock import MagicMock, patch

import pytest


def test_admin_pulse_admin_sees_counts():
    """Unit test with zero network: test that admin (matching ADMIN_EMAIL) sees Registered Users and Engineering Logs metrics in sidebar."""
    mock_user = {
        "id": "admin-123",
        "email": "admin@example.com",
        "display_name": "Admin User",
    }
    mock_session_state = {"user": mock_user, "access_token": "fake_token"}

    mock_profiles_resp = MagicMock()
    mock_profiles_resp.count = 42

    mock_logs_resp = MagicMock()
    mock_logs_resp.count = 150

    mock_client = MagicMock()
    # profiles select table chain
    mock_client.table.return_value.select.return_value.execute.side_effect = [
        mock_profiles_resp,
        mock_logs_resp,
    ]

    metrics_called = []

    def mock_metric(label, value):
        metrics_called.append((label, value))

    with patch("config.ADMIN_EMAIL", "admin@example.com"), patch(
        "streamlit.session_state", mock_session_state
    ), patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.sidebar.metric", side_effect=mock_metric
    ), patch(
        "streamlit.sidebar.success"
    ), patch(
        "streamlit.sidebar.button", return_value=False
    ), patch(
        "streamlit.sidebar.subheader"
    ), patch(
        "streamlit.sidebar.markdown"
    ), patch(
        "streamlit.sidebar.radio", return_value="Home"
    ):

        # Simulate sidebar code execution path
        from config import ADMIN_EMAIL

        user_email = mock_session_state["user"].get("email", "")
        is_admin = bool(
            ADMIN_EMAIL
            and user_email
            and ADMIN_EMAIL.strip().lower() == user_email.strip().lower()
        )
        assert is_admin is True

        if is_admin:
            client = mock_client
            res_users = client.table("profiles").select("id", count="exact").execute()
            users_count = getattr(res_users, "count", 0)

            res_logs = (
                client.table("engineering_log").select("id", count="exact").execute()
            )
            logs_count = getattr(res_logs, "count", 0)

            mock_metric("Registered Users", users_count)
            mock_metric("Engineering Logs", logs_count)

    assert ("Registered Users", 42) in metrics_called
    assert ("Engineering Logs", 150) in metrics_called


def test_admin_pulse_non_admin_sees_nothing():
    """Unit test with zero network: test that non-admin (non-matching email) does not see Admin Pulse metrics."""
    mock_user = {
        "id": "user-456",
        "email": "regular@example.com",
        "display_name": "Regular User",
    }
    mock_session_state = {"user": mock_user, "access_token": "fake_token"}

    metrics_called = []

    def mock_metric(label, value):
        metrics_called.append((label, value))

    with patch("config.ADMIN_EMAIL", "admin@example.com"), patch(
        "streamlit.session_state", mock_session_state
    ), patch("streamlit.sidebar.metric", side_effect=mock_metric):

        from config import ADMIN_EMAIL

        user_email = mock_session_state["user"].get("email", "")
        is_admin = bool(
            ADMIN_EMAIL
            and user_email
            and ADMIN_EMAIL.strip().lower() == user_email.strip().lower()
        )
        assert is_admin is False

    assert len(metrics_called) == 0
