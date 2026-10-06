import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from app.ui.components import (
    apply_custom_theme, render_header, render_metric,
    render_html_table, status_badge
)
from app.core.db_metadata import metadata_db

st.set_page_config(page_title="Pipelines - DataOps Command Center", layout="wide")
apply_custom_theme()

render_header("Pipeline Operations", "Monitor, inspect, and manage enterprise data pipelines", "⚙️")

# ── Fix 8: Pipeline KPI Metrics ──
pipes = metadata_db.fetch_all("SELECT * FROM pipelines ORDER BY pipeline_id ASC")
total = len(pipes)
active = sum(1 for p in pipes if p.get("status") == "ACTIVE")
failed = sum(1 for p in pipes if p.get("status") == "FAILED")

col1, col2, col3 = st.columns(3)
with col1:
    render_metric("Total Pipelines", str(total), delta="Registered", delta_type="neutral")
with col2:
    render_metric("Active / Healthy", str(active), delta="Operational", delta_type="positive")
with col3:
    render_metric("Failed", str(failed),
                  delta=f"{failed} Need Attention" if failed else "None",
                  delta_type="critical" if failed else "positive")

st.markdown("")
st.markdown("### 📋 Pipeline Registry")
render_html_table(pipes,
                  columns=["pipeline_id", "name", "domain", "schedule", "status", "owner"],
                  badge_cols={"status"})

st.divider()
st.markdown("### 🔍 Pipeline Run History")
selected_pipe = st.selectbox("Select Pipeline to Inspect Runs:", [p["pipeline_id"] for p in pipes])

if selected_pipe:
    runs = metadata_db.fetch_all(
        "SELECT * FROM pipeline_runs WHERE pipeline_id = ? ORDER BY start_time DESC",
        (selected_pipe,)
    )
    if runs:
        render_html_table(runs,
                          columns=["run_id", "pipeline_id", "status", "start_time",
                                   "end_time", "records_processed", "error_message"],
                          badge_cols={"status"})
    else:
        st.info("No runs recorded for this pipeline.")
