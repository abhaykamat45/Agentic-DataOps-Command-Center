import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import json
from app.ui.components import (
    apply_custom_theme, render_header, status_badge,
    render_html_table, render_metric
)
from app.core.db_metadata import metadata_db
from app.ai.orchestrator import orchestrator
from app.core.audit import audit_logger

st.set_page_config(page_title="Incidents - DataOps Command Center", layout="wide")
apply_custom_theme()

render_header("Incident Management & Remediation",
              "Deep-dive incident investigation, root causes, evidence, and actions", "🚨")

incidents = metadata_db.fetch_all("SELECT * FROM incidents ORDER BY created_at DESC")
if not incidents:
    st.info("No incidents found.")
    st.stop()

# ── Fix 5: Incident Summary Table ──
st.markdown("### 📋 Incident Queue")
render_html_table(
    incidents,
    columns=["incident_id", "pipeline_id", "severity", "status", "title", "created_at"],
    badge_cols={"severity", "status"}
)

st.divider()

# ── Incident Selector ──
incident_ids = [f"{inc['incident_id']} — {inc['title']}" for inc in incidents]
selected_option = st.selectbox("Select Incident to Investigate:", incident_ids)
selected_inc_id = selected_option.split(" — ")[0]

inc = metadata_db.fetch_one("SELECT * FROM incidents WHERE incident_id = ?", (selected_inc_id,))

# ── Incident Detail Banner ──
st.markdown(f"""
<div class="section-card" style="margin-bottom:20px;">
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;">
        <div>
            <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;
                 letter-spacing:0.06em;font-weight:600;margin-bottom:4px;">Pipeline</div>
            <div style="font-size:15px;font-weight:600;color:var(--text-primary);">{inc['pipeline_id']}</div>
        </div>
        <div>
            <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;
                 letter-spacing:0.06em;font-weight:600;margin-bottom:4px;">Severity</div>
            <div>{status_badge(inc['severity'])}</div>
        </div>
        <div>
            <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;
                 letter-spacing:0.06em;font-weight:600;margin-bottom:4px;">Status</div>
            <div>{status_badge(inc['status'])}</div>
        </div>
        <div>
            <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;
                 letter-spacing:0.06em;font-weight:600;margin-bottom:4px;">Detected</div>
            <div style="font-size:14px;color:var(--text-secondary);">{inc['created_at']}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Two-column Layout ──
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("### 📌 Incident Summary")
    st.write(inc["description"])

    st.markdown("### 🔍 Root Cause Analysis")
    if inc.get("root_cause"):
        st.error(inc["root_cause"])
    else:
        st.warning("Root cause not yet investigated. Click 'Launch AI Investigation' →")

    st.markdown("### 📂 Evidence")
    if inc.get("evidence"):
        try:
            ev_data = json.loads(inc["evidence"])
            st.json(ev_data)
        except Exception:
            st.write(inc["evidence"])
    else:
        st.info("No evidence gathered yet.")

with col_right:
    # ── Fix 4: Chat-style AI interaction ──
    st.markdown("### 🤖 AI Agent Action Center")

    with st.chat_message("assistant"):
        st.write(f"I'm ready to investigate incident **{inc['pipeline_id']}**. "
                 f"Click below or type a custom question.")

    user_query = st.chat_input(f"Ask about {inc['pipeline_id']}...")

    if user_query or st.button("🤖 Launch AI Tool Investigation", type="primary"):
        query = user_query or f"Why did pipeline {inc['pipeline_id']} fail and what should I do?"
        with st.chat_message("user"):
            st.write(query)
        with st.spinner("AI Agent executing Plan → Tools → Evidence → Root Cause → Remediation..."):
            res = orchestrator.investigate_incident(selected_inc_id, query)
            st.success("AI Investigation Completed!")
            st.rerun()

st.divider()

# ── Remediation Plans ──
st.markdown("### 🛠️ Remediation Plans & Approval Gate")
plans = metadata_db.fetch_all("SELECT * FROM remediation_plans WHERE incident_id = ?", (selected_inc_id,))

if plans:
    for p in plans:
        with st.expander(f"Plan `{p['plan_id']}` — {status_badge(p['status'])}", expanded=True):
            st.markdown(f"**Impact Summary**: {p['impact_summary']}", unsafe_allow_html=True)
            st.markdown("**Generated SQL Cleanup Fix:**")
            st.code(p["sql_fix"], language="sql")

            if p.get("pyspark_fix"):
                st.markdown("**Generated PySpark ETL Fix:**")
                st.code(p["pyspark_fix"], language="python")

            if p["status"] == "PENDING_APPROVAL":
                st.warning("⚠️ Action Requires Human Approval Token before Execution.")
                # Fix 10: Two-step approval
                c_app, c_rej = st.columns(2)
                with c_app:
                    if st.button("✅ Approve & Execute Fix", key=f"app_{p['plan_id']}", type="primary"):
                        token = audit_logger.generate_approval_token(p["plan_id"], "DASHBOARD_ENGINEER")
                        with st.spinner("Executing approved fix & verifying DQ..."):
                            exec_res = orchestrator.execute_remediation(p["plan_id"], "DASHBOARD_ENGINEER", token)
                            if exec_res["status"] == "SUCCESS":
                                st.success("Remediation Executed & Incident Resolved!")
                                st.rerun()
                            else:
                                st.error(f"Execution failed: {exec_res.get('error')}")
                with c_rej:
                    if st.button("❌ Reject Plan", key=f"rej_{p['plan_id']}"):
                        metadata_db.execute(
                            "UPDATE remediation_plans SET status = 'REJECTED' WHERE plan_id = ?",
                            (p["plan_id"],)
                        )
                        st.info("Plan rejected.")
                        st.rerun()
            elif p["status"] == "EXECUTED":
                st.success(f"✅ Plan Executed & Verified by {p['approved_by']} at {p['approved_at']}")
else:
    st.info("No remediation plans generated yet for this incident.")
