import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from app.ui.components import (
    apply_custom_theme, render_header, render_html_table, render_mermaid
)
from app.core.db_metadata import metadata_db

st.set_page_config(page_title="Lineage - DataOps Command Center", layout="wide")
apply_custom_theme()

render_header("Data Lineage & Impact Graph",
              "Trace dataset dependencies from source to target and downstream reports", "🕸️")

lineage = metadata_db.fetch_all("SELECT * FROM lineage")

st.markdown("### 🔗 Lineage Dependency Table")
render_html_table(lineage,
                  columns=["lineage_id", "source_table", "transformation_name",
                            "target_table", "dependency_type"],
                  badge_cols={"dependency_type"})

st.divider()

# ── Fix 2: Interactive Mermaid Diagram ──
st.markdown("### 📊 Visual Lineage Flow Diagram")

# Build the mermaid code dynamically from lineage data
mermaid_nodes = set()
mermaid_edges = []
for row in lineage:
    src = row["source_table"]
    tgt = row["target_table"]
    label = row["transformation_name"]
    mermaid_nodes.add(src)
    mermaid_nodes.add(tgt)
    mermaid_edges.append(f"    {src}[{src}] -->|{label}| {tgt}[{tgt}]")

mermaid_code = "graph LR\n" + "\n".join(mermaid_edges)

render_mermaid(mermaid_code, height=350)
