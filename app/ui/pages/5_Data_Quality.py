import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from app.ui.components import (
    apply_custom_theme, render_header, render_metric,
    render_html_table
)
from app.core.db_metadata import metadata_db
from app.tools.dq_tools import RunDataQualityCheckTool

st.set_page_config(page_title="Data Quality - DataOps Command Center", layout="wide")
apply_custom_theme()

render_header("Data Quality Engine",
              "Configurable quality rules, automated evaluations, and anomaly detection", "🎯")

# ── Fix 7: DQ KPI Metrics ──
rules = metadata_db.fetch_all("SELECT * FROM data_quality_rules")
enabled_rules = [r for r in rules if r.get("enabled", 1)]
evals = metadata_db.fetch_all("SELECT * FROM evaluations")

col1, col2, col3 = st.columns(3)
with col1:
    render_metric("Active Rules", str(len(enabled_rules)), delta="Monitoring", delta_type="positive")
with col2:
    tables_covered = len(set(r.get("table_name", "") for r in rules))
    render_metric("Tables Covered", str(tables_covered), delta="Datasets", delta_type="neutral")
with col3:
    render_metric("Total Evaluations", str(len(evals)), delta="Historical Runs", delta_type="neutral")

st.markdown("")

# ── Rules Table ──
st.markdown("### 📋 Active Data Quality Rules")
render_html_table(rules,
                  columns=["rule_id", "table_name", "column_name", "rule_type", "threshold", "enabled"],
                  badge_cols=set())

st.divider()
st.markdown("### 🧪 Evaluate Data Quality Rules")
table_name = st.selectbox("Select Target Parquet Table to Run DQ Checks:",
                           ["claims", "transactions", "customers", "benefits", "plans"])

if st.button("▶️ Run Data Quality Checks", type="primary"):
    tool = RunDataQualityCheckTool()
    res = tool.execute(table_name=table_name)

    st.write(f"**Rules Evaluated**: {res.output['rules_evaluated']}")
    if res.output["has_violations"]:
        st.error(f"Found {res.output['violations_count']} Data Quality Violations!")
        for v in res.output["violations"]:
            st.warning(f"Rule `{v['rule_id']}` ({v['rule_type']}) on column `{v['column']}`: {v['description']}")
    else:
        st.success("All Data Quality rules passed successfully!")
