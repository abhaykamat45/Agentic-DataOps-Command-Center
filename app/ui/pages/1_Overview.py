import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from app.ui.components import (
    apply_custom_theme, render_header, render_metric,
    status_badge, render_html_table
)
from app.core.db_metadata import metadata_db

st.set_page_config(page_title="Overview - DataOps Command Center", layout="wide")
apply_custom_theme()

render_header("Executive Overview", "Real-time pipeline health, active incidents, and platform status", "📊")

# ── KPI Metrics Row ──
pipes = metadata_db.fetch_all("SELECT * FROM pipelines")
failed = metadata_db.fetch_all("SELECT * FROM pipelines WHERE status = 'FAILED'")
incidents = metadata_db.fetch_all("SELECT * FROM incidents WHERE status = 'OPEN'")
plans = metadata_db.fetch_all("SELECT * FROM remediation_plans WHERE status = 'PENDING_APPROVAL'")

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric("Total Pipelines", str(len(pipes)), delta="Active Monitoring", delta_type="positive")
with col2:
    render_metric("Failed Pipelines", str(len(failed)),
                  delta=f"{len(failed)} Needs Attention" if failed else "All Passing",
                  delta_type="critical" if failed else "positive")
with col3:
    render_metric("Open Incidents", str(len(incidents)),
                  delta=f"{len(incidents)} Active" if incidents else "Resolved",
                  delta_type="critical" if incidents else "positive")
with col4:
    render_metric("Pending Approvals", str(len(plans)),
                  delta="Action Needed" if plans else "None",
                  delta_type="warning" if plans else "neutral")

st.markdown("")

# ── Two-Column: Incident Feed + System Status ──
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("### 🚨 Active Incident Alert Feed")
    inc_data = metadata_db.fetch_all(
        "SELECT incident_id, pipeline_id, severity, status, title, created_at "
        "FROM incidents ORDER BY created_at DESC"
    )
    if inc_data:
        render_html_table(
            inc_data,
            columns=["incident_id", "pipeline_id", "severity", "status", "title"],
            badge_cols={"severity", "status"}
        )
    else:
        st.success("All pipelines operational. Zero active incidents!")

with col_right:
    st.markdown("### ⚙️ System Status")
    status_items = [
        ("🟢", "LLM Engine", "Mock (Offline)"),
        ("🟢", "Analytical Store", "DuckDB + Parquet"),
        ("🟢", "Metadata DB", "SQLite"),
        ("🛡️", "Safety Mode", "Strict Approval"),
        ("📝", "Audit Log", "Active"),
    ]
    rows_html = ""
    for icon, label, val in status_items:
        rows_html += f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
             padding:10px 0;border-bottom:1px solid rgba(51,65,85,0.4);">
            <span style="color:var(--text-secondary);font-size:14px;">{icon} <b>{label}</b></span>
            <code style="font-size:12px;color:var(--accent-teal);background:rgba(20,184,166,0.1);
                  padding:3px 8px;border-radius:4px;">{val}</code>
        </div>"""
    st.markdown(f"""
    <div class="section-card" style="padding:16px 20px;">
        {rows_html}
    </div>
    """, unsafe_allow_html=True)
