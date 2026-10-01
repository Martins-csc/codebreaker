import py_compile

import pytest


def test_py_compile_gate():
    """Test pre-seal compile gate across core python modules for v1.4.7."""
    for mod in [
        "app.py",
        "ai_engine.py",
        "security.py",
        "config.py",
        "supabase_client.py",
    ]:
        res = py_compile.compile(mod, doraise=True)
        assert res is not None


def test_v1_4_7_contact_widget_flag_pattern():
    """Test that contact submit uses contact_clear_pending and contact_success flags + rerun without WidgetAlreadyInstantiatedError."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert 'st.session_state["contact_clear_pending"] = True' in content
    assert 'st.session_state["contact_success"] = True' in content
    assert 'if st.session_state.get("contact_clear_pending"):' in content
    assert 'if st.session_state.get("contact_success"):' in content
    assert "st.rerun()" in content
    assert (
        'st.session_state["contact_name_input"] = ""\n                    st.session_state["contact_email_input"] = ""\n                    st.session_state["contact_message_input"] = ""\n                    st.success'
        not in content
    )
