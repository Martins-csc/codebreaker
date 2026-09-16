import os

import streamlit as st


class ConfigError(Exception):
    """Custom exception for missing or invalid configuration without exposing secrets."""

    pass


def get_config(key: str, default: str = None, required: bool = False) -> str:
    """
    Get configuration or secret value with fallback order:
    1. os.environ
    2. st.secrets (guarded for Streamlit Cloud runtime / non-Streamlit execution)
    3. default

    If required=True and value is missing, raises ConfigError.
    """
    val = os.environ.get(key)
    if val is not None and str(val).strip() != "":
        return val

    try:
        if hasattr(st, "secrets") and st.secrets is not None:
            if key in st.secrets:
                secret_val = st.secrets[key]
                if secret_val is not None and str(secret_val).strip() != "":
                    return secret_val
    except Exception:
        pass

    if required and (default is None or str(default).strip() == ""):
        raise ConfigError(f"Missing required configuration: {key}")

    return default


ADMIN_EMAIL = get_config("ADMIN_EMAIL", default="")
