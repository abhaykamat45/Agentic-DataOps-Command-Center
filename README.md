# 🛡️ Agentic DataOps Command Center

> **A Local-First AI Data Engineering Platform that observes, investigates, explains, and safely remediates data pipeline failures and data-quality anomalies using tool-calling Agentic AI, local analytical stores, and human-in-the-loop safety guardrails.**

---

## 📌 Problem & Why It Matters
Modern data platforms handle complex ETL/ELT pipelines, schema migrations, and high-frequency analytical ingestions. When a pipeline fails (e.g., due to schema drift, severe null spikes, or orphan foreign key references like terminated plan IDs), data engineers are forced to manually parse through thousands of log lines, execute ad-hoc SQL queries, and guess root causes—leading to prolonged downtime and risky unverified hotfixes.

The **Agentic DataOps Command Center** bridges **Data Engineering** and **Agentic AI**:
- **Tool-Gated Agent**: The LLM *never* directly accesses databases or raw filesystems. All actions are executed via strict, typed Pydantic tools.
- **Human-in-the-Loop Safety**: State-changing operations (SQL updates, pipeline re-execution) require cryptographically generated human approval tokens.
- **Deterministic Offline Capability**: Features a **Mock LLM Mode** for 100% offline demo execution and automated evaluation without requiring external API keys.

---

## 🏗️ System Architecture

```
                                  ┌───────────────────────────────┐
                                  │   Streamlit Command Center    │
                                  │          (9 Pages)            │
                                  └──────────────┬────────────────┘
                                                 │
                                                 ▼
                                  ┌───────────────────────────────┐
                                  │      FastAPI REST Layer       │
                                  └──────────────┬────────────────┘
                                                 │
                                                 ▼
                                  ┌───────────────────────────────┐
                                  │    DataOps AI Orchestrator    │
                                  │   (Plan -> Tools -> Evidence) │
                                  └──────────────┬────────────────┘
                                                 │
                                                 ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │                                   TYPED TOOL REGISTRY                                  │
 ├────────────────────────┬────────────────────────┬─────────────────────┬────────────────┤
 │  Inspect & Search      │  Schema & Profiling    │  Data Quality & Lineage│ Remediation & Safety│
 │  • inspect_pipeline    │  • inspect_schema      │  • run_dq_check     │ • generate_plan│
 │  • get_pipeline_runs   │  • compare_schemas     │  • detect_anomalies │ • simulate_impact│
 │  • search_logs         │  • profile_dataset     │  • find_dependencies│ • execute_sql* │
 │                        │  • run_sql (read-only) │                     │ • execute_pipe*│
 └────────────────────────┴────────────────────────┴─────────────────────┴────────────────┘
                                                 │ *Requires Human Approval Token
                                                 ▼
                     ┌───────────────────────────────────────────────────────┐
                     │                      DATA LAYER                       │
                     ├───────────────────────────┬───────────────────────────┤
                     │   SQLite Metadata DB      │     DuckDB & Parquet      │
                     │  • pipelines, runs, DQ    │  • customers, employees   │
                     │  • incidents, audit, eval │  • plans, gaids, claims   │
                     └───────────────────────────┴───────────────────────────┘
```

---

## 🛠️ Technology Stack
- **Language**: Python 3.10+
- **Backend API**: FastAPI, Uvicorn
- **Dashboard UI**: Streamlit (Dark Enterprise Theme, 9 pages)
- **Analytical Engine**: DuckDB & Apache Parquet
- **Metadata Store**: SQLite
- **Data Engineering**: PySpark, Pandas, PyArrow
- **Agentic AI & Validation**: Pydantic v2, ReAct Tool-Calling Loop, Mock/OpenAI/Ollama LLM Drivers
- **Testing & Evals**: Pytest, Automated Benchmark Suite (20 Incident Scenarios)

---

## 🌟 Primary Domain Scenario: "Plan & GAID Integrity Failure"
1. **Incident Trigger**: Master table `plans.parquet` has Plan `PLAN-104` set to status `TERMINATED`. Pipeline `pipe_claims_integrity` fails SLA validation.
2. **AI Investigation**:
   - Agent invokes `inspect_pipeline` & `search_logs` to isolate `IntegrityValidationError`.
   - Agent profiles `claims` & `benefits` datasets and detects **45 active claims** and **28 benefits** referencing `PLAN-104`, as well as 15 claims referencing inactive `GAID-999`.
   - Agent calls `simulate_impact` to compute exact affected row counts and downstream table impact.
3. **Remediation & Human-in-the-Loop Safety**:
   - Agent formulates parameterized cleanup SQL and PySpark transformation.
   - Action is flagged `PENDING_APPROVAL`.
   - Human clicks **Approve & Execute**, generating a verified cryptographic token.
   - Agent invokes `execute_sql`, re-triggers `execute_pipeline`, and runs `verify_remediation` confirming 100% resolution.

---

## 🚀 Quickstart & Local Setup

### 1. Clone & Install Dependencies
```bash
git clone <repo-url>
cd DATA_AI_PROJECT

python -m venv venv
# On Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env`. Default configuration runs in **Mock LLM Mode** (no external API keys required):
```env
LLM_PROVIDER=mock
DATA_DIR=./data
METADATA_DB_PATH=./data/metadata.db
PARQUET_DIR=./data/parquet
```

### 3. Run Automated Tests
```bash
python -m pytest tests/
```

### 4. Seed Data & Launch Dashboard
```bash
# Seed synthetic datasets & demo incidents
python -m app.core.synthetic_data

# Launch Streamlit Enterprise Command Center UI
streamlit run app/ui/app.py
```

### 5. Launch FastAPI Backend Service (Optional)
```bash
uvicorn app.api.main:app --reload --port 8000
```

---

## 📄 Documentation Matrix
- [Architecture Details](docs/ARCHITECTURE.md)
- [AI Design & Agentic Loop](docs/AI_DESIGN.md)
- [Data Model & Schemas](docs/DATA_MODEL.md)
- [Typed Tool Registry](docs/TOOL_REGISTRY.md)
- [Evaluation Methodology](docs/EVALUATION.md)
- [Demo Scenario Guide](docs/DEMO.md)
