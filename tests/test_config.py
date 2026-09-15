import os
from unittest.mock import patch

import pytest
from config import ConfigError, get_config


@patch.dict(os.environ, {"TEST_KEY": "env_value"}, clear=True)
def test_config_env_wins():
    """Ensure os.environ takes precedence over st.secrets (zero network)."""
    mock_secrets = {"TEST_KEY": "secrets_value"}
    with patch("streamlit.secrets", mock_secrets):
        val = get_config("TEST_KEY")
        assert val == "env_value"


@patch.dict(os.environ, {}, clear=True)
def test_config_st_secrets_fallback():
    """Ensure fallback to st.secrets when os.environ lacks the key (zero network)."""
    mock_secrets = {"TEST_KEY": "secrets_fallback_value"}
    with patch("streamlit.secrets", mock_secrets):
        val = get_config("TEST_KEY")
        assert val == "secrets_fallback_value"


@patch.dict(os.environ, {}, clear=True)
def test_config_missing_required_raises_error():
    """Ensure required=True raises ConfigError when neither env nor st.secrets has the key (zero network)."""
    with patch("streamlit.secrets", {}):
        with pytest.raises(ConfigError, match="Missing required configuration"):
            get_config("MISSING_KEY", required=True)


@patch.dict(os.environ, {}, clear=True)
def test_config_missing_optional_returns_default():
    """Ensure optional missing key returns default value without raising ConfigError (zero network)."""
    with patch("streamlit.secrets", {}):
        val = get_config("MISSING_KEY", default="default_val", required=False)
        assert val == "default_val"
