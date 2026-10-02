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
    assert mock_create_client.call_count == 1
    args, kwargs = mock_create_client.call_args
    assert args == ("https://example.supabase.co", "fake_anon_key")
    assert "options" in kwargs


def test_pkce_cookie_storage_roundtrip():
    """Test PkceCookieStorage set_item, get_item, remove_item round-trip for sb-pkce keys."""
    from pkce_storage import PkceCookieStorage

    storage = PkceCookieStorage()
    storage.set_item("other-key", "val1")
    assert storage.get_item("other-key") == "val1"
    storage.remove_item("other-key")
    assert storage.get_item("other-key") is None

    storage.set_item("sb-pkce-code-verifier", "verifier123")
    assert storage.get_item("sb-pkce-code-verifier") == "verifier123"
    storage.remove_item("sb-pkce-code-verifier")
    assert storage.get_item("sb-pkce-code-verifier") is None


def test_github_button_present():
    """Test 'Continue with GitHub' button is present in app.py."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert "Continue with GitHub" in content
