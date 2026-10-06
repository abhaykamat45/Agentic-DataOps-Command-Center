import pytest

def test_metadata_tables_creation(test_meta_db):
    conn = test_meta_db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = [
        "pipelines", "pipeline_runs", "schemas", "data_quality_rules",
        "lineage", "incidents", "remediation_plans", "audit_events", "evaluations"
    ]
    for table in expected_tables:
        assert table in tables

def test_pipeline_insert_fetch(test_meta_db):
    test_meta_db.execute(
        "INSERT INTO pipelines VALUES (?,?,?,?,?,?,?)",
        ("TEST-P1", "test_pipe", "TestDomain", "0 * * * *", "SUCCESS", "Tester", "2026-09-20 00:00:00")
    )
    res = test_meta_db.fetch_one("SELECT * FROM pipelines WHERE pipeline_id = ?", ("TEST-P1",))
    assert res is not None
    assert res["name"] == "test_pipe"
    assert res["domain"] == "TestDomain"
