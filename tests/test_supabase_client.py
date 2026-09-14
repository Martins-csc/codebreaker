import os
from unittest.mock import patch

import pytest
from supabase_client import ConfigError, get_client


@patch.dict(os.environ, {}, clear=True)
def test_get_client_missing_env_raises_config_error():
    """Ensure ConfigError is raised when Supabase environment variables are missing (zero network calls)."""
    import supabase_client

    supabase_client._supabase_client = None

    with pytest.raises(
        ConfigError, match="Missing required Supabase environment variable"
    ):
        get_client()


@patch.dict(
    os.environ,
    {
        "SUPABASE_URL": "https://example.supabase.co",
        "SUPABASE_ANON_KEY": "fake_anon_key",
    },
    clear=True,
)
@patch("supabase_client.create_client")
def test_get_client_singleton_and_success(mock_create_client):
    """Ensure get_client initializes client correctly and returns singleton."""
    import supabase_client

    supabase_client._supabase_client = None

    mock_client_instance = object()
    mock_create_client.return_value = mock_client_instance

    client1 = get_client()
    client2 = get_client()

    assert client1 is mock_client_instance
    assert client1 is client2
    mock_create_client.assert_called_once_with(
        "https://example.supabase.co", "fake_anon_key"
    )
