import sys
from pathlib import Path

# Add project root to python path for Streamlit execution
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from app.ui.components import apply_custom_theme, render_header, render_metric
from app.core.db_metadata import metadata_db
from app.core.db_analytical import analytical_db
from app.core.synthetic_data import SyntheticDataGenerator

st.set_page_config(
    page_title="Agentic DataOps Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_theme()

# Ensure seed data exists on app launch
pipes = metadata_db.fetch_all("SELECT * FROM pipelines")
if not pipes:
    gen = SyntheticDataGenerator(metadata_db, analytical_db)
    gen.generate_all()

# Fix 14: Premium sidebar branding
st.sidebar.markdown("""
<div style="padding:12px 8px 16px 8px;margin-bottom:8px;">
    <div style="font-size:18px;font-weight:700;color:#f1f5f9;margin-bottom:2px;">
        🛡️ DataOps Command Center
    </div>
    <div style="font-size:12px;color:#94a3b8;">
        <code style="font-size:11px;background:rgba(59,130,246,0.12);color:#3b82f6;
              padding:2px 6px;border-radius:4px;">v1.0.0</code>
        &nbsp;·&nbsp; Local-First AI Agent
    </div>
</div>
""", unsafe_allow_html=True)
st.sidebar.divider()

render_header(
    title="Agentic DataOps Command Center",
    subtitle="AI-Powered Autonomous Data Pipeline Investigation & Human-in-the-Loop Remediation Platform",
    icon="🛡️"
)

st.markdown("""
<div class="section-card" style="text-align:center;padding:14px 20px;">
    <span style="font-size:14px;color:var(--text-secondary);">
        👈 Select a page from the sidebar to navigate the Command Center
    </span>
</div>
""", unsafe_allow_html=True)

st.markdown("")

col1, col2, col3, col4 = st.columns(4)
with col1:
    pipes_cnt = len(metadata_db.fetch_all("SELECT * FROM pipelines"))
    render_metric("Total Pipelines", str(pipes_cnt), delta="Active Monitoring", delta_type="positive")
with col2:
    inc_cnt = len(metadata_db.fetch_all("SELECT * FROM incidents WHERE status = 'OPEN'"))
    render_metric("Active Incidents", str(inc_cnt), delta="Open", delta_type="critical")
with col3:
    plans_cnt = len(metadata_db.fetch_all("SELECT * FROM remediation_plans WHERE status = 'PENDING_APPROVAL'"))
    render_metric("Pending Approvals", str(plans_cnt), delta="Action Needed", delta_type="warning")
with col4:
    audit_cnt = len(metadata_db.fetch_all("SELECT * FROM audit_events"))
    render_metric("Audit Trail Events", str(audit_cnt), delta="Immutable Log", delta_type="neutral")
