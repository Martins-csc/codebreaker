import os

from config import ConfigError, get_config
from supabase import Client, create_client

_global_supabase_client: Client = None


def get_client() -> Client:
    """
    Get or create the Supabase client.
    Stores a per-session singleton in st.session_state if Streamlit context is active,
    preventing cross-user session leakage across concurrent Streamlit sessions (Branch H2).
    """
    try:
        import streamlit as st

        if hasattr(st, "session_state"):
            if "supabase_client_instance" not in st.session_state:
                url = get_config("SUPABASE_URL")
                anon_key = get_config("SUPABASE_ANON_KEY")

                missing = []
                if not url:
                    missing.append("SUPABASE_URL")
                if not anon_key:
                    missing.append("SUPABASE_ANON_KEY")

                if missing:
                    raise ConfigError(
                        f"Missing required Supabase environment variable(s) or secret(s): {', '.join(missing)}"
                    )

                try:
                    st.session_state["supabase_client_instance"] = create_client(
                        url, anon_key
                    )
                except Exception as e:
                    err_msg = str(e)
                    if url:
                        err_msg = err_msg.replace(url, "[REDACTED]")
                    if anon_key:
                        err_msg = err_msg.replace(anon_key, "[REDACTED]")
                    raise ConfigError(
                        f"Failed to initialize Supabase client: {err_msg}"
                    )

            return st.session_state["supabase_client_instance"]
    except Exception:
        pass

    global _global_supabase_client
    if _global_supabase_client is not None:
        return _global_supabase_client

    url = get_config("SUPABASE_URL")
    anon_key = get_config("SUPABASE_ANON_KEY")

    missing = []
    if not url:
        missing.append("SUPABASE_URL")
    if not anon_key:
        missing.append("SUPABASE_ANON_KEY")

    if missing:
        raise ConfigError(
            f"Missing required Supabase environment variable(s) or secret(s): {', '.join(missing)}"
        )

    try:
        _global_supabase_client = create_client(url, anon_key)
    except Exception as e:
        err_msg = str(e)
        if url:
            err_msg = err_msg.replace(url, "[REDACTED]")
        if anon_key:
            err_msg = err_msg.replace(anon_key, "[REDACTED]")
        raise ConfigError(f"Failed to initialize Supabase client: {err_msg}")

    return _global_supabase_client
