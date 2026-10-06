import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from app.ui.components import apply_custom_theme, render_header
from app.config import settings
from app.core.db_metadata import metadata_db
from app.core.db_analytical import analytical_db
from app.core.synthetic_data import SyntheticDataGenerator

st.set_page_config(page_title="Settings - DataOps Command Center", layout="wide")
apply_custom_theme()

render_header("Platform Settings & Configuration",
              "Configure LLM providers, database connection paths, and demo data re-seeding", "⚙️")

# ── Fix 13: Grouped settings cards ──
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="section-card">
        <div class="section-card-title">🤖 LLM Provider Configuration</div>
    </div>
    """, unsafe_allow_html=True)

    provider = st.selectbox("LLM Provider Mode", ["mock", "openai", "ollama"], index=0)
    st.caption("`mock` mode allows 100% offline deterministic demo without API keys.")
    api_key = st.text_input("OpenAI API Key", value=settings.OPENAI_API_KEY, type="password")
    model_name = st.text_input("Model Name", value=settings.OPENAI_MODEL)

with col2:
    st.markdown("""
    <div class="section-card">
        <div class="section-card-title">📁 System Storage Paths</div>
    </div>
    """, unsafe_allow_html=True)

    st.text_input("Data Directory", value=str(settings.DATA_DIR), disabled=True)
    st.text_input("SQLite Metadata Path", value=str(settings.METADATA_DB_PATH), disabled=True)
    st.text_input("Parquet Storage Path", value=str(settings.PARQUET_DIR), disabled=True)

st.divider()

# ── Fix 10: Confirmation gate for re-seed ──
st.markdown("### 🔄 Re-seed Synthetic Enterprise Datasets")
st.caption("This will drop and re-create all metadata tables and regenerate all Parquet datasets.")

col_btn, col_space = st.columns([1, 3])
with col_btn:
    if st.button("🔥 Re-seed All Data", type="primary"):
        st.session_state["confirm_reseed"] = True

if st.session_state.get("confirm_reseed"):
    st.warning("⚠️ This is a destructive action. All existing data will be replaced.")
    c1, c2, _ = st.columns([1, 1, 4])
    with c1:
        if st.button("✅ Confirm Re-seed", type="primary"):
            gen = SyntheticDataGenerator(metadata_db, analytical_db)
            gen.generate_all()
            st.session_state["confirm_reseed"] = False
            st.success("Successfully re-seeded all metadata and Parquet datasets!")
            st.rerun()
    with c2:
        if st.button("❌ Cancel"):
            st.session_state["confirm_reseed"] = False
            st.rerun()
