import os
import py_compile

import pytest


def test_v1_9_26_py_compile():
    """Assert app.py compiles successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    assert py_compile.compile(app_path, doraise=True)


def test_v1_9_26_redirect_to_state():
    """Source scan: redirect_to includes state parameter and callback reads state from query_params."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert 'redirect_to = f"{base_url}?state={state}"' in content
    assert 'state = st.query_params.get("state")' in content
    assert 'client.rpc("consume_oauth_state", {"p_state": state})' in content
