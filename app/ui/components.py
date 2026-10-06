import streamlit as st
import streamlit.components.v1 as components


def apply_custom_theme():
    """Apply premium modern dark enterprise theme with glassmorphism CSS styling."""
    st.markdown("""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Theme Overrides */
    :root {
        --bg-main: #0f172a;
        --bg-card: #1e293b;
        --bg-card-hover: #334155;
        --bg-surface: #151e2e;
        --border-subtle: #334155;
        --border-strong: #475569;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --accent-blue: #3b82f6;
        --accent-blue-hover: #2563eb;
        --accent-teal: #14b8a6;
        --accent-indigo: #6366f1;
        --status-critical: #ef4444;
        --status-critical-bg: rgba(239,68,68,0.12);
        --status-warning: #f59e0b;
        --status-warning-bg: rgba(245,158,11,0.12);
        --status-success: #10b981;
        --status-success-bg: rgba(16,185,129,0.12);
        --status-info-bg: rgba(59,130,246,0.12);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ==================== Core ==================== */
    .stApp {
        background-color: var(--bg-main) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Fix 15: Responsive container density */
    .block-container {
        max-width: 1400px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }

    /* ==================== Typography ==================== */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        color: var(--text-primary) !important;
    }
    h1 { font-size: 26px !important; }
    h2 { font-size: 22px !important; }
    h3 { font-size: 18px !important; margin-top: 1.2em !important; margin-bottom: 0.6em !important; }

    p, span, div, label {
        font-family: 'Inter', sans-serif;
    }

    /* ==================== Fix 14: Sidebar ==================== */
    [data-testid="stSidebar"] {
        background-color: #0b1120 !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarNav"] li a {
        color: var(--text-muted) !important;
        padding: 8px 16px !important;
        border-radius: var(--radius-sm) !important;
        transition: var(--transition) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarNav"] li a:hover {
        color: var(--text-primary) !important;
        background-color: rgba(59,130,246,0.08) !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarNav"] li a[aria-current="page"] {
        color: var(--accent-blue) !important;
        background-color: rgba(59,130,246,0.12) !important;
        font-weight: 600 !important;
    }

    /* ==================== Premium Header ==================== */
    .premium-header {
        background: linear-gradient(135deg, #1a2744 0%, #162033 100%);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 20px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 24px -8px rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .premium-header-icon { font-size: 28px; line-height: 1; }
    .premium-header-content h1 {
        font-size: 24px !important;
        font-weight: 700 !important;
        margin: 0 0 2px 0 !important;
        padding: 0 !important;
    }
    .premium-header-content p {
        font-size: 14px !important;
        color: var(--text-muted) !important;
        margin: 0 !important;
    }

    /* ==================== Metric Cards ==================== */
    .premium-metric-card {
        background-color: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 18px 20px;
        display: flex;
        flex-direction: column;
        transition: var(--transition);
        box-shadow: 0 2px 8px -2px rgba(0,0,0,0.2);
    }
    .premium-metric-card:hover {
        transform: translateY(-2px);
        border-color: var(--accent-blue);
        box-shadow: 0 8px 16px -4px rgba(0,0,0,0.3);
    }
    .premium-metric-label {
        font-size: 11px;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }
    .premium-metric-value {
        font-size: 32px;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.1;
        margin-bottom: 4px;
    }
    .premium-metric-delta { font-size: 12px; font-weight: 500; }
    .delta-positive { color: var(--status-success); }
    .delta-negative, .delta-critical { color: var(--status-critical); }
    .delta-warning { color: var(--status-warning); }
    .delta-neutral { color: var(--text-muted); }

    /* ==================== Badges ==================== */
    .premium-badge {
        display: inline-flex;
        align-items: center;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        white-space: nowrap;
    }
    .badge-critical {
        background-color: var(--status-critical-bg);
        color: var(--status-critical);
        border: 1px solid rgba(239,68,68,0.25);
    }
    .badge-warning {
        background-color: var(--status-warning-bg);
        color: var(--status-warning);
        border: 1px solid rgba(245,158,11,0.25);
    }
    .badge-success {
        background-color: var(--status-success-bg);
        color: var(--status-success);
        border: 1px solid rgba(16,185,129,0.25);
    }
    .badge-neutral {
        background-color: rgba(148,163,184,0.12);
        color: var(--text-muted);
        border: 1px solid rgba(148,163,184,0.2);
    }

    /* ==================== Section Card ==================== */
    .section-card {
        background-color: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 20px 24px;
        margin-bottom: 16px;
    }
    .section-card-title {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ==================== Fix 1: Custom HTML Tables ==================== */
    .styled-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: var(--radius-md);
        overflow: hidden;
        border: 1px solid var(--border-subtle);
        font-size: 13px;
    }
    .styled-table thead th {
        background-color: #162033;
        color: var(--text-muted);
        font-weight: 600;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 10px 14px;
        text-align: left;
        border-bottom: 1px solid var(--border-subtle);
    }
    .styled-table tbody tr {
        background-color: var(--bg-card);
        transition: var(--transition);
    }
    .styled-table tbody tr:hover {
        background-color: var(--bg-card-hover);
    }
    .styled-table tbody tr:not(:last-child) td {
        border-bottom: 1px solid rgba(51,65,85,0.5);
    }
    .styled-table tbody td {
        padding: 10px 14px;
        color: var(--text-secondary);
    }
    .styled-table tbody td:first-child {
        color: var(--text-primary);
        font-weight: 500;
    }

    /* ==================== Buttons ==================== */
    .stButton > button {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius-sm) !important;
        transition: var(--transition) !important;
        font-weight: 500 !important;
        font-size: 14px !important;
    }
    .stButton > button:hover {
        border-color: var(--accent-blue) !important;
        color: var(--accent-blue) !important;
        background-color: rgba(59,130,246,0.06) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        border-color: transparent !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px -2px rgba(59,130,246,0.4) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        box-shadow: 0 4px 12px -2px rgba(59,130,246,0.5) !important;
    }

    /* ==================== Code Blocks ==================== */
    .stCodeBlock {
        background-color: #0b0f19 !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
    }
    code {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
    }

    /* ==================== Dataframes ==================== */
    .stDataFrame {
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        overflow: hidden !important;
    }

    /* ==================== Expander ==================== */
    .streamlit-expanderHeader {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 500 !important;
    }

    /* ==================== Selectbox & Text Input ==================== */
    .stSelectbox > div > div,
    .stTextInput > div > div > input {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
    }

    /* ==================== Tool Trace Timeline ==================== */
    .tool-trace-step {
        background-color: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 16px 20px;
        margin-bottom: 12px;
        transition: var(--transition);
    }
    .tool-trace-step:hover {
        border-color: var(--accent-blue);
    }
    .tool-trace-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .tool-trace-name {
        font-weight: 600;
        font-size: 14px;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .tool-trace-step-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--accent-blue), var(--accent-indigo));
        color: white;
        font-size: 11px;
        font-weight: 700;
    }
    .tool-trace-body {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }
    .tool-trace-panel {
        background-color: var(--bg-surface);
        border: 1px solid rgba(51,65,85,0.5);
        border-radius: var(--radius-sm);
        padding: 12px;
    }
    .tool-trace-panel-label {
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        margin-bottom: 6px;
    }
    .tool-trace-panel pre {
        margin: 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: var(--text-secondary);
        white-space: pre-wrap;
        word-break: break-word;
    }

    /* ==================== Chat Messages ==================== */
    .stChatMessage {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
    }

    /* ==================== Divider ==================== */
    hr {
        border-color: var(--border-subtle) !important;
        opacity: 0.5;
    }

    </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str, icon: str = "🛡️"):
    """Render a premium page header."""
    st.markdown(f"""
    <div class="premium-header">
        <div class="premium-header-icon">{icon}</div>
        <div class="premium-header-content">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric(label: str, value: str, delta: str = None, delta_type: str = "neutral"):
    """Render a premium metric card."""
    delta_html = ""
    if delta:
        delta_class = f"delta-{delta_type}"
        arrows = {"positive": "↑", "critical": "↓", "warning": "⚠", "neutral": "→"}
        icon = arrows.get(delta_type, "→")
        delta_html = f'<div class="premium-metric-delta {delta_class}">{icon} {delta}</div>'

    st.markdown(f"""
    <div class="premium-metric-card">
        <div class="premium-metric-label">{label}</div>
        <div class="premium-metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def status_badge(status: str) -> str:
    """Return HTML string for a styled status badge."""
    s = status.upper()
    if s in ("SUCCESS", "RESOLVED", "APPROVED", "EXECUTED", "ACTIVE", "HEALTHY"):
        return f'<span class="premium-badge badge-success">{s}</span>'
    elif s in ("FAILED", "CRITICAL", "ERROR"):
        return f'<span class="premium-badge badge-critical">{s}</span>'
    elif s in ("WARNING", "OPEN", "PENDING_APPROVAL", "PENDING"):
        return f'<span class="premium-badge badge-warning">{s}</span>'
    else:
        return f'<span class="premium-badge badge-neutral">{s}</span>'


def render_html_table(rows: list[dict], columns: list[str] = None,
                      badge_cols: set = None) -> None:
    """Render a list of dicts as a fully styled HTML table with optional badge columns.

    Args:
        rows: List of row dicts (from metadata_db.fetch_all).
        columns: Ordered column keys to display. If None, uses keys from first row.
        badge_cols: Set of column names whose values should be rendered as status badges.
    """
    if not rows:
        st.info("No data available.")
        return

    badge_cols = badge_cols or set()
    if columns is None:
        columns = list(rows[0].keys())

    header_html = "".join(f"<th>{c.replace('_', ' ').title()}</th>" for c in columns)
    body_rows = []
    for row in rows:
        cells = []
        for c in columns:
            val = row.get(c, "")
            if c in badge_cols and val:
                cells.append(f"<td>{status_badge(str(val))}</td>")
            else:
                cells.append(f"<td>{val}</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")

    st.markdown(f"""
    <table class="styled-table">
        <thead><tr>{header_html}</tr></thead>
        <tbody>{''.join(body_rows)}</tbody>
    </table>
    """, unsafe_allow_html=True)


def render_section_card(title: str, icon: str = ""):
    """Return an opening div for a section card. Call render_section_card_end() after content."""
    st.markdown(f"""
    <div class="section-card">
        <div class="section-card-title">{icon} {title}</div>
    """, unsafe_allow_html=True)


def render_section_card_end():
    """Close a section card div."""
    st.markdown("</div>", unsafe_allow_html=True)


def render_mermaid(mermaid_code: str, height: int = 400):
    """Render a Mermaid diagram as an interactive SVG using Mermaid JS CDN."""
    html_content = f"""
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <style>
            body {{ margin: 0; background: transparent; display: flex; justify-content: center; }}
            .mermaid {{ font-family: 'Inter', sans-serif; }}
        </style>
    </head>
    <body>
        <div class="mermaid">
{mermaid_code}
        </div>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'dark',
                themeVariables: {{
                    primaryColor: '#1e293b',
                    primaryTextColor: '#f1f5f9',
                    primaryBorderColor: '#3b82f6',
                    lineColor: '#475569',
                    secondaryColor: '#1e293b',
                    tertiaryColor: '#0f172a',
                    edgeLabelBackground: '#1e293b',
                    fontSize: '14px'
                }}
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=height, scrolling=False)


def render_tool_trace_step(step_num: int, tool_name: str, success: bool,
                           args: dict, output, error: str = None):
    """Render a single tool trace step as a premium card."""
    import json
    status_html = status_badge("SUCCESS" if success else "FAILED")
    args_str = json.dumps(args, indent=2, default=str)
    output_str = json.dumps(output, indent=2, default=str) if isinstance(output, (dict, list)) else str(output)

    error_html = ""
    if error:
        error_html = f"""
        <div style="margin-top:10px;padding:8px 12px;background:var(--status-critical-bg);
             border:1px solid rgba(239,68,68,0.25);border-radius:var(--radius-sm);
             color:var(--status-critical);font-size:12px;">
            ⚠ {error}
        </div>"""

    st.markdown(f"""
    <div class="tool-trace-step">
        <div class="tool-trace-header">
            <div class="tool-trace-name">
                <span class="tool-trace-step-num">{step_num}</span>
                <code style="font-size:13px;color:var(--accent-blue);">{tool_name}</code>
            </div>
            {status_html}
        </div>
        <div class="tool-trace-body">
            <div class="tool-trace-panel">
                <div class="tool-trace-panel-label">Input Arguments</div>
                <pre>{args_str}</pre>
            </div>
            <div class="tool-trace-panel">
                <div class="tool-trace-panel-label">Output Result</div>
                <pre>{output_str}</pre>
            </div>
        </div>
        {error_html}
    </div>
    """, unsafe_allow_html=True)
