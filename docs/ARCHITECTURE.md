# 🏛️ Architecture Documentation - Agentic DataOps Command Center

## 1. System Overview & Core Principles
The Agentic DataOps Command Center is built around four fundamental architectural pillars:

1. **Local-First Analytical Engine**: DuckDB executes analytical queries against Parquet files with near-zero latency without external database dependencies.
2. **SQLite Metadata Store**: Manages pipelines, execution runs, schemas, data quality rules, lineage edges, incidents, remediation plans, audit logs, and evaluations.
3. **Strict Tool Registry Security**: The AI LLM cannot issue raw connection strings or system calls. All interactions pass through Pydantic validated tool classes inheriting from `BaseTool`.
4. **Human-in-the-Loop Approval Gate**: Any tool classified with `is_destructive = True` (`execute_sql`, `execute_pipeline`) is blocked unless passed a cryptographically valid approval token.

---

## 2. Component Diagram

```
+-----------------------------------------------------------------------+
|                      Streamlit Command Center (9 Pages)              |
+-----------------------------------┬-----------------------------------+
                                    │
                                    ▼
+-----------------------------------------------------------------------+
|                         FastAPI REST API Layer                        |
+-----------------------------------┬-----------------------------------+
                                    │
                                    ▼
+-----------------------------------------------------------------------+
|                       DataOps Orchestrator Agent                      |
|           PLAN -> CALL TOOLS -> EVIDENCE -> ROOT CAUSE                |
+-----------------------------------┬-----------------------------------+
                                    │
                                    ▼
+-----------------------------------------------------------------------+
|                           Typed Tool Registry                         |
|     Inspect | Schema | Data Quality | Lineage | Remediation | Safety   |
+-----------------------------------┬-----------------------------------+
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
+-----------------------------------+   +-------------------------------+
|      SQLite Metadata Engine       |   |   DuckDB & Parquet Layer      |
|  pipelines, runs, DQ, audit, eval |   |   claims, plans, benefits, etc. |
+-----------------------------------+   +-------------------------------+
```
