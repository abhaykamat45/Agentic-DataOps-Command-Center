# 🛠️ Tool Registry Specification - Agentic DataOps Command Center

Every tool implements `BaseTool` with Pydantic validated arguments and structured `ToolResult` outputs.

| Tool Name | Type | Destructive? | Description |
|---|---|---|---|
| `inspect_pipeline` | Inspection | No | Fetch pipeline configuration and SLA metrics |
| `get_pipeline_runs` | Inspection | No | Fetch recent run history and error messages |
| `search_logs` | Inspection | No | Search execution log files for stack traces |
| `inspect_schema` | Schema | No | Inspect column definitions and data types |
| `compare_schemas` | Schema | No | Compare physical parquet schema against expected metadata |
| `profile_dataset` | Profiling | No | Compute row count, null rates, and statistics |
| `run_sql` | SQL | No | Execute read-only SELECT query against DuckDB |
| `execute_sql` | Remediation | **Yes** | Execute state-changing SQL updates/deletes in Parquet |
| `run_data_quality_check` | Quality | No | Run DQ rules (null rate, referential integrity) |
| `detect_anomalies` | Profiling | No | Detect null spikes, duplicates, or orphan foreign keys |
| `find_dependencies` | Lineage | No | Discover upstream sources and downstream targets |
| `generate_remediation_plan` | Remediation | No | Formulate structured plan awaiting human approval |
| `generate_sql_fix` | Remediation | No | Produce parameterized SQL DDL/DML cleanup statement |
| `generate_pyspark_fix` | Remediation | No | Generate PySpark transformation script |
| `simulate_impact` | Simulation | No | Calculate affected row count & downstream table impact |
| `execute_pipeline` | Execution | **Yes** | Re-trigger data pipeline execution after remediation |
| `verify_remediation` | Verification | No | Re-evaluate DQ rules to confirm incident resolution |
