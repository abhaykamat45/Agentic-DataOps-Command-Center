import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from app.ui.components import (
    apply_custom_theme, render_header, render_metric, render_html_table
)
from app.core.db_metadata import metadata_db

st.set_page_config(page_title="Audit Log - DataOps Command Center", layout="wide")
apply_custom_theme()

render_header("Immutable Audit Log & Security Trail",
              "Complete audit trail of system events, human approvals, and tool invocations", "📜")

events = metadata_db.fetch_all("SELECT * FROM audit_events ORDER BY timestamp DESC")

if not events:
    st.info("No audit events recorded yet.")
    st.stop()

# ── KPI row ──
col1, col2, col3 = st.columns(3)
with col1:
    render_metric("Total Events", str(len(events)), delta="Immutable", delta_type="neutral")
with col2:
    actors = set(e.get("actor", "") for e in events)
    render_metric("Unique Actors", str(len(actors)), delta="System & Users", delta_type="neutral")
with col3:
    actions = set(e.get("action", "") for e in events)
    render_metric("Action Types", str(len(actions)), delta="Tracked", delta_type="neutral")

st.markdown("")

# ── Fix 11: Audit Log Filters ──
st.markdown("### 🔍 Filter Events")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    all_actors = sorted(set(e.get("actor", "N/A") for e in events))
    selected_actor = st.selectbox("Filter by Actor:", ["All"] + all_actors)

with col_f2:
    all_actions = sorted(set(e.get("action", "N/A") for e in events))
    selected_action = st.selectbox("Filter by Action:", ["All"] + all_actions)

with col_f3:
    search_term = st.text_input("Search Details:", placeholder="e.g. PIPE-001")

# Apply filters
filtered = events
if selected_actor != "All":
    filtered = [e for e in filtered if e.get("actor") == selected_actor]
if selected_action != "All":
    filtered = [e for e in filtered if e.get("action") == selected_action]
if search_term:
    filtered = [e for e in filtered if search_term.lower() in str(e).lower()]

st.markdown(f"### 📋 Audit Events ({len(filtered)} of {len(events)})")
if filtered:
    render_html_table(
        filtered,
        columns=["event_id", "timestamp", "actor", "action", "target_resource", "approval_token"],
        badge_cols={"action"}
    )
else:
    st.info("No events match your filters.")
