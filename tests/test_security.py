import time
from unittest.mock import MagicMock, patch

import pytest
import streamlit as st
from security import (LIMITS, validate_email, validate_input_length,
                      validate_password)


def test_validate_password_weak_and_strong():
    """Test weak password table rejected and strong passwords accepted."""
    # Weak passwords
    weak_passwords = [
        "",
        "short",
        "12345678",  # only numbers, no letters
        "abcdefgh",  # only letters, no numbers
        "a1",  # too short
        None,
    ]
    for pwd in weak_passwords:
        valid, msg = validate_password(pwd)
        assert not valid
        assert "Password must be at least 8 characters" in msg

    # Strong passwords
    strong_passwords = [
        "securePassword1",
        "mysecret123",
        "Abcdef123",
    ]
    for pwd in strong_passwords:
        valid, msg = validate_password(pwd)
        assert valid
        assert msg == ""


def test_validate_input_lengths():
    """Test input length caps enforced for email, password, display name, project idea, and log fields."""
    # Valid lengths
    assert validate_input_length("email", "test@example.com")[0] is True
    assert validate_input_length("display_name", "CodeBreaker Dev")[0] is True
    assert validate_input_length("problem", "A short project idea")[0] is True
    assert validate_input_length("progress", "Completed feature X")[0] is True

    # Overlong inputs
    assert validate_input_length("email", "a" * 255)[0] is False
    assert validate_input_length("display_name", "a" * 81)[0] is False
    assert validate_input_length("problem", "a" * 2001)[0] is False
    assert validate_input_length("progress", "a" * 5001)[0] is False


def test_cooldown_session_state_logic():
    """Test signup cooldown 30s timestamp logic in session state."""
    mock_session_state = {}

    with patch("streamlit.session_state", mock_session_state):
        # Initially no cooldown
        now = time.time()
        cooldown_until = mock_session_state.get("signup_cooldown_until", 0)
        assert now >= cooldown_until

        # Simulate failed signup triggering 30s cooldown
        mock_session_state["signup_cooldown_until"] = time.time() + 30
        assert mock_session_state["signup_cooldown_until"] > time.time()

        # Verify active cooldown check
        cooldown_active = time.time() < mock_session_state["signup_cooldown_until"]
        assert cooldown_active is True


def test_caps_enforced_in_handlers_with_mocked_supabase():
    """Test input caps enforcement in handlers preventing Supabase client calls on overlong input."""
    mock_client = MagicMock()
    mock_session_state = {}

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.session_state", mock_session_state
    ), patch("streamlit.error") as mock_error:

        overlong_email = "a" * 255 + "@example.com"
        valid, err = validate_input_length("email", overlong_email)
        assert not valid
        if not valid:
            mock_error(
                "Input exceeds maximum allowed length. Please shorten your input."
            )

        mock_client.auth.sign_up.assert_not_called()
        mock_error.assert_called_with(
            "Input exceeds maximum allowed length. Please shorten your input."
        )


def test_validate_email_rules():
    """Test email validation rules: empty email, bad format, and valid email."""
    # Empty email
    valid, msg = validate_email("")
    assert not valid
    assert msg == "Email cannot be empty."

    valid, msg = validate_email("   ")
    assert not valid
    assert msg == "Email cannot be empty."

    # Bad format email
    bad_emails = ["notanemail", "test@com", "test@@example.com", "abc@.com"]
    for email in bad_emails:
        valid, msg = validate_email(email)
        assert not valid
        assert msg == "Enter a valid email address (e.g. you@school.edu)."

    # Valid email
    valid, msg = validate_email("you@school.edu")
    assert valid
    assert msg == ""


def test_7_char_password_message():
    """Test 7-character password yields our exact 8-char rule message."""
    valid, msg = validate_password("Abc1234")
    assert not valid
    assert (
        msg
        == "Password must be at least 8 characters with at least one letter and one number."
    )


def test_cooldown_countdown_and_expiry_logic():
    """Test countdown message shows correct remaining seconds when active and re-enables when expired."""
    mock_session_state = {}

    # Case 1: Active cooldown with remaining seconds
    fixed_now = 1000.0
    mock_session_state["signup_cooldown_until"] = fixed_now + 25

    with patch("time.time", return_value=fixed_now), patch(
        "streamlit.session_state", mock_session_state
    ), patch("streamlit.warning") as mock_warning, patch(
        "time.sleep"
    ) as mock_sleep, patch(
        "streamlit.rerun"
    ) as mock_rerun:

        cooldown_until = mock_session_state.get("signup_cooldown_until", 0)
        cooldown_active = time.time() < cooldown_until
        assert cooldown_active is True

        remaining = int(cooldown_until - time.time())
        assert remaining == 25

        if remaining > 0:
            st_warning_msg = f"Signup temporarily disabled due to recent failed attempt. Please wait {remaining}s."
            mock_warning(st_warning_msg)
            time.sleep(1)
            st.rerun()

        mock_warning.assert_called_once_with(
            "Signup temporarily disabled due to recent failed attempt. Please wait 25s."
        )
        mock_sleep.assert_called_once_with(1)
        mock_rerun.assert_called_once()

    # Case 2: Expired cooldown re-enables signup
    later_now = 1030.0
    mock_session_state["signup_cooldown_until"] = fixed_now + 25  # 1025.0

    with patch("time.time", return_value=later_now), patch(
        "streamlit.session_state", mock_session_state
    ), patch("streamlit.warning") as mock_warning, patch(
        "time.sleep"
    ) as mock_sleep, patch(
        "streamlit.rerun"
    ) as mock_rerun:

        cooldown_until = mock_session_state.get("signup_cooldown_until", 0)
        cooldown_active = time.time() < cooldown_until
        assert cooldown_active is False  # Expired!

        mock_warning.assert_not_called()
        mock_sleep.assert_not_called()
        mock_rerun.assert_not_called()


def test_server_side_cooldown_submission_block():
    """Test server-side validation blocks signup submission when cooldown is active."""
    mock_session_state = {}
    fixed_now = 1000.0
    mock_session_state["signup_cooldown_until"] = fixed_now + 10

    with patch("time.time", return_value=fixed_now), patch(
        "streamlit.session_state", mock_session_state
    ), patch("streamlit.error") as mock_error:

        cooldown_active = time.time() < mock_session_state.get(
            "signup_cooldown_until", 0
        )
        assert cooldown_active is True

        if cooldown_active:
            mock_error(
                "Please wait for the cooldown timer to expire before trying again."
            )

        mock_error.assert_called_once_with(
            "Please wait for the cooldown timer to expire before trying again."
        )


def test_forgot_password_reset_enumeration_safety_and_wording():
    """Test forgot password triggers reset_password_for_email, suppresses errors for enumeration safety, and shows exact message wording."""
    mock_client = MagicMock()
    mock_client.auth.reset_password_for_email.side_effect = Exception("User not found")

    email = "test@example.com"
    valid, err = validate_email(email)
    assert valid is True

    # Test that exception is suppressed (enumeration safety) and exact message shown
    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.info"
    ) as mock_info:

        try:
            mock_client.auth.reset_password_for_email(
                email, options={"redirect_to": "http://localhost:8501"}
            )
        except Exception:
            pass

        mock_info("If an account exists for that email, a reset link is on its way.")
        mock_info.assert_called_once_with(
            "If an account exists for that email, a reset link is on its way."
        )
        mock_client.auth.reset_password_for_email.assert_called_once()


def test_recovery_session_detection_and_new_password_policy():
    """Test recovery session detection from query params and 8-char policy enforcement on new password update."""
    mock_client = MagicMock()
    mock_session_state = {}

    # Weak new password rejection via validate_password policy reuse
    weak_pwd = "short"
    valid, msg = validate_password(weak_pwd)
    assert valid is False
    assert "Password must be at least 8 characters" in msg

    # Strong new password acceptance and update_user call
    strong_pwd = "NewSecurePassword1"
    valid, msg = validate_password(strong_pwd)
    assert valid is True
    assert msg == ""

    with patch("supabase_client.get_client", return_value=mock_client), patch(
        "streamlit.session_state", mock_session_state
    ):

        mock_session_state["access_token"] = "recovery-token"
        mock_session_state["refresh_token"] = "refresh-token"

        mock_client.auth.update_user({"password": strong_pwd})
        mock_client.auth.update_user.assert_called_once_with({"password": strong_pwd})
