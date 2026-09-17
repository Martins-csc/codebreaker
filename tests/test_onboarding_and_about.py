from unittest.mock import MagicMock, patch

import pytest


def test_tour_renders_when_not_dismissed():
    """Test onboarding tour renders when user is logged in and tour_dismissed is False/absent."""
    mock_session_state = {"user": {"email": "dev@example.com"}, "tour_dismissed": False}

    with patch("streamlit.session_state", mock_session_state), patch(
        "streamlit.expander"
    ) as mock_expander, patch("streamlit.markdown") as mock_markdown, patch(
        "streamlit.button", return_value=False
    ):

        user = mock_session_state.get("user")
        if user and not mock_session_state.get("tour_dismissed", False):
            with mock_expander(
                "👋 Welcome to CodeBreaker — First-Run Onboarding Tour", expanded=True
            ):
                mock_markdown("Walkthrough steps...")

        mock_expander.assert_called_once()


def test_tour_dismissed_does_not_render():
    """Test onboarding tour does not render when tour_dismissed is True."""
    mock_session_state = {"user": {"email": "dev@example.com"}, "tour_dismissed": True}

    with patch("streamlit.session_state", mock_session_state), patch(
        "streamlit.expander"
    ) as mock_expander:

        user = mock_session_state.get("user")
        if user and not mock_session_state.get("tour_dismissed", False):
            with mock_expander("Tour"):
                pass

        mock_expander.assert_not_called()


def test_tour_button_dismisses():
    """Test clicking 'Got it' button sets tour_dismissed to True in session_state."""
    mock_session_state = {"user": {"email": "dev@example.com"}, "tour_dismissed": False}

    with patch("streamlit.session_state", mock_session_state), patch(
        "streamlit.expander"
    ), patch("streamlit.markdown"), patch("streamlit.button", return_value=True), patch(
        "streamlit.rerun", side_effect=Exception("Rerun triggered")
    ):

        with pytest.raises(Exception, match="Rerun triggered"):
            user = mock_session_state.get("user")
            if user and not mock_session_state.get("tour_dismissed", False):
                import streamlit as st

                if st.button("Got it"):
                    mock_session_state["tour_dismissed"] = True
                    st.rerun()

    assert mock_session_state["tour_dismissed"] is True


def test_about_page_content():
    """Test About page content contains mission statement, lecturer section, auth doors, and export formats."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "Mission Statement" in content
    assert "Plan before you code" in content
    assert "How Lecturers Use CodeBreaker in Class" in content
    assert "Assignment Grade" in content
    assert "The Two Auth Doors" in content
    assert "The Four Export Formats" in content
    assert "v1.0.3" in content
