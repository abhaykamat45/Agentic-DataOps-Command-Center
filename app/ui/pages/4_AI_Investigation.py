import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import json
from app.ui.components import (
    apply_custom_theme, render_header, status_badge,
    render_tool_trace_step
)
from app.ai.orchestrator import orchestrator
from app.core.db_metadata import metadata_db

st.set_page_config(page_title="AI Investigation - DataOps Command Center", layout="wide")
apply_custom_theme()

render_header("AI Agent Investigation Workspace",
              "Autonomous tool-calling trace with inputs, outputs, and evidence grounding", "🧠")

incidents = metadata_db.fetch_all("SELECT * FROM incidents ORDER BY created_at DESC")
inc_options = [f"{inc['incident_id']} — {inc['title']}" for inc in incidents]
selected_option = st.selectbox("Select Incident to Trace AI Reasoning:", inc_options)
selected_inc_id = selected_option.split(" — ")[0]

# ── Fix 4: Chat-style interaction ──
col_chat, col_trace = st.columns([2, 3])

with col_chat:
    st.markdown("### 💬 Agent Chat")

    # Show chat history
    if "ai_chat_messages" not in st.session_state:
        st.session_state["ai_chat_messages"] = []

    for msg in st.session_state["ai_chat_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if not st.session_state["ai_chat_messages"]:
        with st.chat_message("assistant"):
            st.write(f"Select an incident and ask me to investigate. "
                     f"I will use my tool registry to gather evidence, "
                     f"identify root causes, and propose remediation.")

    user_input = st.chat_input("Ask the AI agent...")

    if user_input:
        st.session_state["ai_chat_messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.spinner("Agent running ReAct loop (Plan → Tools → Evidence → Root Cause)..."):
            res = orchestrator.investigate_incident(selected_inc_id, user_input)
            st.session_state["last_investigation"] = res.dict()

        summary = f"**Root Cause:** {res.root_cause_summary}\n\n"
        summary += f"**Tools Called:** {len(res.tool_calls_executed)}\n\n"
        summary += "Investigation complete. See the tool trace panel →"
        st.session_state["ai_chat_messages"].append({"role": "assistant", "content": summary})
        st.rerun()

    if st.button("🚀 Run Full Investigation", type="primary"):
        with st.spinner("Agent running ReAct loop..."):
            res = orchestrator.investigate_incident(selected_inc_id)
            st.session_state["last_investigation"] = res.dict()

            msg = f"**Root Cause:** {res.root_cause_summary}\n\n"
            msg += f"Executed {len(res.tool_calls_executed)} tool calls. See trace →"
            st.session_state["ai_chat_messages"] = [
                {"role": "user", "content": f"Investigate incident {selected_inc_id}"},
                {"role": "assistant", "content": msg}
            ]
            st.rerun()

with col_trace:
    st.markdown("### 🛠️ Tool Execution Trace")

    if "last_investigation" in st.session_state:
        res = st.session_state["last_investigation"]

        # Plan Steps
        st.markdown(f"""
        <div class="section-card" style="margin-bottom:16px;">
            <div class="section-card-title">📋 Investigation Plan ({len(res['plan_steps'])} steps)</div>
            <div style="font-size:13px;color:var(--text-secondary);">
                {'<br>'.join(f"&nbsp;&nbsp;{i+1}. {s}" for i, s in enumerate(res['plan_steps']))}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Fix 3: Structured tool trace timeline
        for i, tc in enumerate(res["tool_calls_executed"], 1):
            render_tool_trace_step(
                step_num=i,
                tool_name=tc["tool_name"],
                success=tc["success"],
                args=tc["args"],
                output=tc["output"],
                error=tc.get("error")
            )

        # Root Cause Conclusion
        st.markdown(f"""
        <div class="section-card" style="border-color:var(--status-critical);margin-top:8px;">
            <div class="section-card-title" style="color:var(--status-critical);">
                💡 Root Cause Conclusion
            </div>
            <div style="font-size:14px;color:var(--text-secondary);">
                {res['root_cause_summary']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="section-card" style="text-align:center;padding:40px;">
            <div style="font-size:40px;margin-bottom:12px;">🔬</div>
            <div style="color:var(--text-muted);font-size:14px;">
                No investigation results yet.<br>
                Select an incident and click <b>Run Full Investigation</b> or ask a question.
            </div>
        </div>
        """, unsafe_allow_html=True)
