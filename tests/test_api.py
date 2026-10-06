import pytest
from app.api.main import root
from app.api.router_pipelines import list_pipelines, get_pipeline
from app.api.router_incidents import list_incidents, get_incident
from app.api.router_agent import investigate_incident, InvestigateRequest
from app.api.router_remediation import approve_and_execute_remediation, ApprovePlanRequest

def test_root_endpoint(seeded_env):
    res = root()
    assert res["status"] == "ONLINE"
    assert "Command Center" in res["service"]

def test_list_pipelines_api(seeded_env):
    pipelines = list_pipelines()
    assert len(pipelines) >= 5

def test_get_pipeline_detail_api(seeded_env):
    pipe = get_pipeline("PIPE-001")
    assert pipe["pipeline"]["pipeline_id"] == "PIPE-001"
    assert len(pipe["runs"]) > 0

def test_list_incidents_api(seeded_env):
    incidents = list_incidents()
    assert len(incidents) >= 3

def test_get_incident_detail_api(seeded_env):
    inc = get_incident("INC-101")
    assert inc["incident"]["incident_id"] == "INC-101"

def test_agent_investigate_api(seeded_env):
    res = investigate_incident(InvestigateRequest(incident_id="INC-101"))
    assert res["incident_id"] == "INC-101"
    assert res["investigation_status"] == "COMPLETED"

def test_remediation_approval_flow_api(seeded_env):
    inv_res = investigate_incident(InvestigateRequest(incident_id="INC-101"))
    plan_id = inv_res["recommended_remediation_plan_id"]
    res = approve_and_execute_remediation(ApprovePlanRequest(plan_id=plan_id, approved_by="API_USER"))
    assert res["status"] == "SUCCESS"
