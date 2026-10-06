import pytest

def test_synthetic_data_seeding(seeded_env):
    meta_db = seeded_env["meta_db"]
    ana_db = seeded_env["ana_db"]

    # Verify pipelines seeded
    pipelines = meta_db.fetch_all("SELECT * FROM pipelines")
    assert len(pipelines) >= 5

    # Verify incidents seeded
    incidents = meta_db.fetch_all("SELECT * FROM incidents")
    assert len(incidents) >= 3
    
    # Check Plan & GAID Integrity Scenario
    inc_101 = meta_db.fetch_one("SELECT * FROM incidents WHERE incident_id = 'INC-101'")
    assert inc_101 is not None
    assert "Terminated Plan" in inc_101["title"]

    # Verify analytical datasets (plans, claims, benefits)
    plans = ana_db.query("SELECT * FROM plans WHERE status = 'TERMINATED'")
    assert len(plans) == 1
    assert plans[0]["plan_id"] == "PLAN-104"

    # Verify claims referencing PLAN-104
    invalid_claims = ana_db.query("SELECT * FROM claims WHERE plan_id = 'PLAN-104'")
    assert len(invalid_claims) == 45

    # Verify benefits referencing PLAN-104
    invalid_benefits = ana_db.query("SELECT * FROM benefits WHERE plan_id = 'PLAN-104'")
    assert len(invalid_benefits) == 28
