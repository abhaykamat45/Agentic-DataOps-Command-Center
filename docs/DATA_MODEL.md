# 📊 Data Model & Schemas - Agentic DataOps Command Center

## 1. SQLite Metadata Tables (`data/metadata.db`)
- `pipelines`: `pipeline_id`, `name`, `domain`, `schedule`, `status`, `owner`, `updated_at`
- `pipeline_runs`: `run_id`, `pipeline_id`, `status`, `start_time`, `end_time`, `records_processed`, `error_message`, `log_path`
- `schemas`: `schema_id`, `table_name`, `column_name`, `data_type`, `is_nullable`, `is_primary_key`, `version`, `updated_at`
- `data_quality_rules`: `rule_id`, `table_name`, `column_name`, `rule_type`, `threshold`, `enabled`
- `lineage`: `lineage_id`, `source_table`, `transformation_name`, `target_table`, `dependency_type`
- `incidents`: `incident_id`, `pipeline_id`, `run_id`, `severity`, `status`, `title`, `description`, `root_cause`, `evidence`, `created_at`
- `remediation_plans`: `plan_id`, `incident_id`, `status`, `sql_fix`, `pyspark_fix`, `impact_summary`, `requires_approval`, `approved_by`, `approved_at`, `execution_result`
- `audit_events`: `event_id`, `timestamp`, `actor`, `action`, `target_resource`, `details_json`, `approval_token`
- `evaluations`: `eval_id`, `incident_id`, `score`, `tool_accuracy`, `safety_passed`, `grounding_passed`, `details_json`, `eval_time`

---

## 2. Synthetic Parquet Datasets (`data/parquet/`)
- `customers.parquet`
- `employees.parquet`
- `plans.parquet`
- `gaids.parquet`
- `transactions.parquet`
- `benefits.parquet`
- `claims.parquet`
- `products.parquet`
