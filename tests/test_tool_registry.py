import pytest
from app.tools import tool_registry

def test_tool_registry_registration(seeded_env):
    tools = tool_registry.list_tools()
    assert len(tools) == 17
    
    # Check specific tool availability
    assert tool_registry.get_tool("inspect_pipeline") is not None
    assert tool_registry.get_tool("execute_sql") is not None
    assert tool_registry.get_tool("simulate_impact") is not None

def test_inspect_pipeline_tool(seeded_env):
    res = tool_registry.invoke("inspect_pipeline", {"pipeline_id": "PIPE-001"})
    assert res.success is True
    assert res.output["pipeline"]["name"] == "pipe_claims_integrity"

def test_search_logs_tool(seeded_env):
    res = tool_registry.invoke("search_logs", {"run_id": "RUN-001-A", "keyword": "IntegrityValidationError"})
    assert res.success is True
    assert len(res.output["results"]) > 0

def test_profile_dataset_tool(seeded_env):
    res = tool_registry.invoke("profile_dataset", {"table_name": "plans"})
    assert res.success is True
    assert res.output["total_rows"] == 5

def test_run_sql_read_only_restriction(seeded_env):
    # Valid SELECT query
    res = tool_registry.invoke("run_sql", {"sql": "SELECT * FROM plans"})
    assert res.success is True
    
    # Attempting destructive query via run_sql must fail
    res_invalid = tool_registry.invoke("run_sql", {"sql": "DELETE FROM plans WHERE status = 'TERMINATED'"})
    assert res_invalid.success is False
    assert "SECURITY ERROR" in res_invalid.error

def test_simulate_impact_tool(seeded_env):
    res = tool_registry.invoke("simulate_impact", {"target_table": "claims", "filter_condition": "plan_id = 'PLAN-104'"})
    assert res.success is True
    assert res.output["affected_rows_count"] == 45
