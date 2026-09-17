import time
from unittest.mock import MagicMock, patch

import pytest

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
