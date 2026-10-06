import pytest
from app.tools import tool_registry
from app.core.audit import audit_logger

def test_destructive_tool_requires_approval_token(seeded_env):
    # Invoking execute_sql without approval token MUST FAIL
    res_no_token = tool_registry.invoke(
        "execute_sql",
        {
            "sql": "SELECT * FROM claims",
            "target_table": "claims",
            "plan_id": "PLAN-REM-001"
        }
    )
    assert res_no_token.success is False
    assert "SECURITY ERROR" in res_no_token.error

def test_destructive_tool_with_invalid_token(seeded_env):
    res_bad_token = tool_registry.invoke(
        "execute_sql",
        {
            "sql": "SELECT * FROM claims",
            "target_table": "claims",
            "plan_id": "PLAN-REM-001"
        },
        approval_token="INVALID_TOKEN_123"
    )
    assert res_bad_token.success is False
    assert "SECURITY ERROR" in res_bad_token.error

def test_destructive_tool_with_valid_token(seeded_env):
    plan_id = "PLAN-REM-TEST"
    token = audit_logger.generate_approval_token(plan_id, "DATA_ENGINEER_ALICE")
    
    # Execute state-changing SQL with valid token
    res_success = tool_registry.invoke(
        "execute_sql",
        {
            "sql": "SELECT * FROM claims WHERE plan_id != 'PLAN-104'",
            "target_table": "claims",
            "plan_id": plan_id
        },
        approval_token=token
    )
    assert res_success.success is True
    assert res_success.output["rows_before"] == 600
    assert res_success.output["rows_after"] == 555  # 600 - 45
