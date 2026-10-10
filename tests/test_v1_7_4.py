import os
import py_compile

import pytest


def test_v1_7_4_py_compile():
    """Assert app.py and ai_engine.py compile successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    engine_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ai_engine.py")
    )
    assert py_compile.compile(app_path, doraise=True)
    assert py_compile.compile(engine_path, doraise=True)


def test_v1_7_4_source_scan():
    """Source scan: zero sidebar Log Out button definitions, Account card contains Log Out button with type='secondary', use_container_width=True."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Zero sidebar Log Out button definitions remain
    assert 'st.sidebar.button("Log Out"' not in content
    assert "sidebar_sign_out_btn" not in content

    # 2. Account card contains Log Out button with type="secondary" and use_container_width=True
    assert '"Log Out"' in content
    assert 'type="secondary"' in content
    assert "use_container_width=True" in content
    assert 'key="home_log_out_btn"' in content

    # 3. Sign-out handler sequence present (revoke resume token, client.auth.sign_out, pop query params, clear session state, rerun)
    assert "revoke_resume_token" in content
    assert "client.auth.sign_out()" in content
    assert "st.rerun()" in content
