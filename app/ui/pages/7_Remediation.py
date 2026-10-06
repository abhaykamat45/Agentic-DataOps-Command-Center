import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from app.ui.components import (
    apply_custom_theme, render_header, render_metric,
    render_html_table, status_badge
)
from app.core.db_metadata import metadata_db
from app.core.audit import audit_logger
from app.ai.orchestrator import orchestrator

st.set_page_config(page_title="Remediation - DataOps Command Center", layout="wide")
apply_custom_theme()

render_header("Remediation Approval Center",
              "Review proposed SQL/PySpark fixes, simulate impact, approve or reject", "🛡️")

plans = metadata_db.fetch_all("SELECT * FROM remediation_plans ORDER BY plan_id DESC")
if not plans:
    st.info("No remediation plans generated yet.")
    st.stop()

# ── KPI row ──
pending = [p for p in plans if p["status"] == "PENDING_APPROVAL"]
executed = [p for p in plans if p["status"] == "EXECUTED"]

col1, col2, col3 = st.columns(3)
with col1:
    render_metric("Total Plans", str(len(plans)), delta="Generated", delta_type="neutral")
with col2:
    render_metric("Pending Approval", str(len(pending)),
                  delta="Action Needed" if pending else "None",
                  delta_type="warning" if pending else "positive")
with col3:
    render_metric("Executed", str(len(executed)), delta="Remediated", delta_type="positive")

st.markdown("")

# ── All plans table ──
st.markdown("### 📋 All Remediation Plans")
render_html_table(plans,
                  columns=["plan_id", "incident_id", "status", "impact_summary"],
                  badge_cols={"status"})

st.divider()

# ── Fix 9+10: Pending Approval Cards ──
st.markdown("### ⏳ Pending Approvals")

if pending:
    for p in pending:
        # Determine risk level from impact_summary
        impact = (p.get("impact_summary") or "").lower()
        if "critical" in impact or "fail" in impact:
            risk_badge = '<span class="premium-badge badge-critical">HIGH RISK</span>'
        elif "warning" in impact or "moderate" in impact:
            risk_badge = '<span class="premium-badge badge-warning">MEDIUM RISK</span>'
        else:
            risk_badge = '<span class="premium-badge badge-success">LOW RISK</span>'

        st.markdown(f"""
        <div class="section-card" style="margin-bottom:16px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <div style="font-size:16px;font-weight:600;color:var(--text-primary);">
                    Plan <code>{p['plan_id']}</code> → Incident <code>{p['incident_id']}</code>
                </div>
                <div style="display:flex;gap:8px;">
                    {risk_badge}
                    {status_badge(p['status'])}
                </div>
            </div>
            <div style="font-size:13px;color:var(--text-secondary);margin-bottom:10px;">
                <b>Impact:</b> {p['impact_summary']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**SQL Cleanup Fix:**")
        st.code(p["sql_fix"], language="sql")

        if p.get("pyspark_fix"):
            st.markdown("**PySpark ETL Fix:**")
            st.code(p["pyspark_fix"], language="python")

        # Fix 10: Confirmation gate
        c1, c2, _ = st.columns([1, 1, 2])
        with c1:
            if st.button(f"✅ Approve `{p['plan_id']}`", key=f"btn_app_{p['plan_id']}", type="primary"):
                token = audit_logger.generate_approval_token(p["plan_id"], "REMEDIATION_ADMIN")
                with st.spinner("Executing approved fix & verifying remediation..."):
                    res = orchestrator.execute_remediation(p["plan_id"], "REMEDIATION_ADMIN", token)
                    if res["status"] == "SUCCESS":
                        st.success("Successfully remediated!")
                        st.rerun()
        with c2:
            if st.button(f"❌ Reject `{p['plan_id']}`", key=f"btn_rej_{p['plan_id']}"):
                metadata_db.execute(
                    "UPDATE remediation_plans SET status = 'REJECTED' WHERE plan_id = ?",
                    (p["plan_id"],)
                )
                st.info("Plan rejected.")
                st.rerun()

        st.markdown("---")
else:
    st.success("🎉 Zero pending approvals — all remediation plans have been resolved!")
