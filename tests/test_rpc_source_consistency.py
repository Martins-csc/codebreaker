import ast
import py_compile
import re
from pathlib import Path

import pytest


def parse_sql_functions(sql_content):
    func_pattern = re.compile(
        r"create\s+or\s+replace\s+function\s+public\.([a-zA-Z0-9_]+)\s*\((.*?)\)\s*returns",
        re.DOTALL | re.IGNORECASE,
    )
    funcs = {}
    for match in func_pattern.finditer(sql_content):
        func_name = match.group(1)
        params_str = match.group(2)
        param_names = re.findall(r"\b(p_[a-zA-Z0-9_]+)\b", params_str)
        funcs[func_name] = set(param_names)
    return funcs


def test_py_compile_app():
    """Ensure app.py compiles cleanly without syntax or indentation errors."""
    app_path = Path(__file__).parent.parent / "app.py"
    py_compile.compile(str(app_path), doraise=True)


def test_rpc_parameter_name_consistency():
    """Zero-network source-consistency test: parse migration function signatures and assert every RPC params dict key in app.py matches its target function."""
    sql_path = Path(__file__).parent.parent / "resume_sessions_migration.sql"
    sql_content = sql_path.read_text(encoding="utf-8")
    sql_funcs = parse_sql_functions(sql_content)

    assert "create_resume_token" in sql_funcs
    assert "verify_resume_token" in sql_funcs
    assert "revoke_resume_token" in sql_funcs

    app_path = Path(__file__).parent.parent / "app.py"
    app_code = app_path.read_text(encoding="utf-8")
    tree = ast.parse(app_code)

    rpc_calls_found = 0

    class RPCVisitor(ast.NodeVisitor):

        def visit_Call(self, node):
            nonlocal rpc_calls_found
            self.generic_visit(node)
            is_rpc = False
            if isinstance(node.func, ast.Attribute) and node.func.attr == "rpc":
                is_rpc = True
            elif isinstance(node.func, ast.Name) and node.func.id == "rpc":
                is_rpc = True

            if is_rpc and len(node.args) >= 2:
                func_arg = node.args[0]
                params_arg = node.args[1]
                if isinstance(func_arg, ast.Constant) and isinstance(
                    func_arg.value, str
                ):
                    func_name = func_arg.value
                    if func_name in sql_funcs:
                        rpc_calls_found += 1
                        if isinstance(params_arg, ast.Dict):
                            dict_keys = []
                            for k in params_arg.keys:
                                if isinstance(k, ast.Constant) and isinstance(
                                    k.value, str
                                ):
                                    dict_keys.append(k.value)
                            expected_params = sql_funcs[func_name]
                            for key in dict_keys:
                                assert (
                                    key in expected_params
                                ), f"RPC call to {func_name} passes parameter '{key}', which is not defined in resume_sessions_migration.sql (expected one of {expected_params})"

    visitor = RPCVisitor()
    visitor.visit(tree)
    assert rpc_calls_found > 0, "Expected to find resume session RPC calls in app.py"
