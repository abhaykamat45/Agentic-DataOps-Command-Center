import pytest
from app.ai.orchestrator import DataOpsOrchestrator
from app.core.audit import audit_logger

def test_orchestrator_investigate_inc_101(seeded_env):
    orchestrator = DataOpsOrchestrator()
    res = orchestrator.investigate_incident("INC-101")
    
    assert res.incident_id == "INC-101"
    assert res.pipeline_id == "PIPE-001"
    assert res.investigation_status == "COMPLETED"
    assert "PLAN-104" in res.root_cause_summary
    assert res.recommended_remediation_plan_id is not None
    assert len(res.tool_calls_executed) >= 5

def test_orchestrator_full_remediation_flow(seeded_env):
    orchestrator = DataOpsOrchestrator()
    inv_res = orchestrator.investigate_incident("INC-101")
    plan_id = inv_res.recommended_remediation_plan_id
    
    # Generate human approval token
    token = audit_logger.generate_approval_token(plan_id, "DATA_ENGINEER_LEAD")
    
    # Execute approved remediation
    exec_res = orchestrator.execute_remediation(plan_id, "DATA_ENGINEER_LEAD", approval_token=token)
    
    assert exec_res["status"] == "SUCCESS"
    assert exec_res["verification"]["verification_status"] == "VERIFIED_RESOLVED"
    assert exec_res["verification"]["passed_all_dq_checks"] is True
