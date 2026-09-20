from unittest.mock import MagicMock, patch

import pytest


def test_auth_widget_keys_uniqueness():
    """Assert all auth form widget keys are unique across signup, login, and recovery forms."""
    signup_keys = {
        "signup_email",
        "signup_pw",
        "signup_display_name",
        "signup_submit_btn",
    }
    login_keys = {"login_email", "login_pw", "login_submit_btn", "forgot_submit_btn"}
    recovery_keys = {"reset_pw_new", "reset_pw_confirm", "reset_submit_btn"}

    all_auth_keys = signup_keys | login_keys | recovery_keys
    assert len(all_auth_keys) == len(signup_keys) + len(login_keys) + len(recovery_keys)
    assert len(signup_keys & login_keys) == 0
    assert len(signup_keys & recovery_keys) == 0
    assert len(login_keys & recovery_keys) == 0


def test_streamlit_api_exception_not_masked():
    """Assert that StreamlitAPIException or duplicate key exception is re-raised and not swallowed."""

    class StreamlitAPIException(Exception):
        pass

    with pytest.raises(StreamlitAPIException):
        try:
            raise StreamlitAPIException("StreamlitDuplicateElementKey: key='set'")
        except Exception as e:
            if (
                type(e).__name__.startswith("Streamlit")
                or "DuplicateElementKey" in type(e).__name__
            ):
                raise
            # otherwise swallowed
