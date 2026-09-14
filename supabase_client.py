import os

from supabase import Client, create_client


class ConfigError(Exception):
    """Custom exception for missing or invalid Supabase configuration without exposing secrets."""

    pass


_supabase_client: Client = None


def get_client() -> Client:
    """
    Get or create the Supabase client singleton using environment variables only.
    Raises ConfigError if SUPABASE_URL or SUPABASE_ANON_KEY are missing.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    url = os.environ.get("SUPABASE_URL")
    anon_key = os.environ.get("SUPABASE_ANON_KEY")

    missing = []
    if not url:
        missing.append("SUPABASE_URL")
    if not anon_key:
        missing.append("SUPABASE_ANON_KEY")

    if missing:
        raise ConfigError(
            f"Missing required Supabase environment variable(s): {', '.join(missing)}"
        )

    try:
        _supabase_client = create_client(url, anon_key)
    except Exception as e:
        err_msg = str(e)
        if url:
            err_msg = err_msg.replace(url, "[REDACTED]")
        if anon_key:
            err_msg = err_msg.replace(anon_key, "[REDACTED]")
        raise ConfigError(f"Failed to initialize Supabase client: {err_msg}")

    return _supabase_client
