import pytest
import pandas as pd

def test_analytical_db_save_and_query(test_ana_db):
    df = pd.DataFrame([
        {"id": 1, "val": "A"},
        {"id": 2, "val": "B"}
    ])
    test_ana_db.save_dataframe_as_table(df, "test_table")
    
    res = test_ana_db.query("SELECT * FROM test_table WHERE id = 1")
    assert len(res) == 1
    assert res[0]["val"] == "A"
