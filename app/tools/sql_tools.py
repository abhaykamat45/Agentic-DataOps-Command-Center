import time
from typing import Optional
from pydantic import BaseModel, Field
from app.tools.base import BaseTool, ToolResult
from app.core.db_analytical import analytical_db
from app.core.audit import audit_logger

# 7. run_sql
class RunSQLInput(BaseModel):
    sql: str = Field(..., description="Read-only SELECT query to run against local analytical views")

class RunSQLTool(BaseTool):
    name = "run_sql"
    description = "Execute a read-only analytical SQL query against local Parquet tables via DuckDB."
    args_model = RunSQLInput

    def execute(self, sql: str) -> ToolResult:
        t0 = time.time()
        sql_clean = sql.strip()
        if not sql_clean.upper().startswith("SELECT") and not sql_clean.upper().startswith("WITH") and not sql_clean.upper().startswith("DESCRIBE"):
            return ToolResult(
                success=False,
                tool_name=self.name,
                output={},
                error="SECURITY ERROR: 'run_sql' only supports read-only SELECT/WITH/DESCRIBE queries. Use 'execute_sql' for modifications."
            )

        try:
            results = analytical_db.query(sql_clean)
            return ToolResult(
                success=True,
                tool_name=self.name,
                output={"row_count": len(results), "records": results[:50]},
                execution_time_ms=(time.time() - t0) * 1000
            )
        except Exception as e:
            return ToolResult(success=False, tool_name=self.name, output={}, error=str(e))

# 8. execute_sql
class ExecuteSQLInput(BaseModel):
    sql: str = Field(..., description="State-changing SQL query (DELETE/UPDATE/INSERT) or cleanup statement")
    target_table: str = Field(..., description="Name of the Parquet table being modified (e.g., 'claims')")
    plan_id: str = Field(..., description="Associated remediation plan ID requiring approval")
    approval_token: Optional[str] = Field(None, description="Cryptographic human approval token")

class ExecuteSQLTool(BaseTool):
    name = "execute_sql"
    description = "Execute state-changing remediation SQL queries to clean, update, or remove bad records in Parquet storage. [DESTRUCTIVE]"
    is_destructive = True
    args_model = ExecuteSQLInput

    def execute(self, sql: str, target_table: str, plan_id: str, approval_token: Optional[str] = None) -> ToolResult:
        t0 = time.time()
        # Verify approval token
        if not approval_token or not audit_logger.verify_approval_token(approval_token, plan_id):
            return ToolResult(
                success=False,
                tool_name=self.name,
                output={},
                error=f"SECURITY ERROR: Destructive tool 'execute_sql' requires a verified human approval token. Provided token '{approval_token}' is invalid or missing."
            )

        try:
            # Query existing table, apply SQL transformation via DuckDB, save back to Parquet
            df_current = analytical_db.query_df(f"SELECT * FROM {target_table}")
            conn = analytical_db.get_connection()
            # Perform query in duckdb memory
            df_updated = conn.execute(sql).df()
            conn.close()

            # Save updated table back to parquet
            saved_path = analytical_db.save_dataframe_as_table(df_updated, target_table)

            rows_before = len(df_current)
            rows_after = len(df_updated)
            rows_changed = abs(rows_before - rows_after)

            audit_logger.log_event(
                actor="AI_REMEDIATION_AGENT",
                action="EXECUTE_SQL_REMEDIATION",
                target_resource=f"table:{target_table}",
                details={"sql": sql, "rows_before": rows_before, "rows_after": rows_after, "plan_id": plan_id},
                approval_token=approval_token
            )

            return ToolResult(
                success=True,
                tool_name=self.name,
                output={
                    "status": "SUCCESS",
                    "target_table": target_table,
                    "rows_before": rows_before,
                    "rows_after": rows_after,
                    "rows_modified": rows_changed,
                    "saved_path": saved_path
                },
                execution_time_ms=(time.time() - t0) * 1000
            )
        except Exception as e:
            return ToolResult(success=False, tool_name=self.name, output={}, error=str(e))
