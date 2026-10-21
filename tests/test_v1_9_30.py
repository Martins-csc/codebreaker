import os
import py_compile

import pytest


def test_v1_9_30_py_compile():
    """Assert app.py compiles successfully."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    assert py_compile.compile(app_path, doraise=True)


def test_v1_9_30_oauth_rpc_insert_and_cleanup():
    """Source scan: oauth_states insert uses insert_oauth_state RPC and [OAUTH-DEBUG] logs are removed."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "insert_oauth_state" in content
    assert "[OAUTH-DEBUG]" not in content

    migration_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../oauth_states_migration.sql")
    )
    with open(migration_path, "r", encoding="utf-8") as f:
        migration_content = f.read()

    assert "insert_oauth_state" in migration_content
