import time
import uuid
from typing import Optional
from pydantic import BaseModel, Field
from app.tools.base import BaseTool, ToolResult
from app.core.db_metadata import metadata_db
from app.core.db_analytical import analytical_db

# 12. generate_remediation_plan
class GenerateRemediationPlanInput(BaseModel):
    incident_id: str = Field(..., description="ID of the incident to generate remediation plan for (e.g., 'INC-101')")
    sql_fix: str = Field(..., description="Proposed SQL remediation statement")
    pyspark_fix: Optional[str] = Field(None, description="Optional PySpark transformation script")
    impact_summary: str = Field(..., description="Human-readable impact assessment summary")

class GenerateRemediationPlanTool(BaseTool):
    name = "generate_remediation_plan"
    description = "Generate and register a structured remediation plan awaiting human approval."
    args_model = GenerateRemediationPlanInput

    def execute(self, incident_id: str, sql_fix: str, impact_summary: str, pyspark_fix: Optional[str] = None) -> ToolResult:
        t0 = time.time()
        plan_id = f"PLAN-REM-{uuid.uuid4().hex[:8].upper()}"
        
        query = """
        INSERT INTO remediation_plans (plan_id, incident_id, status, sql_fix, pyspark_fix, impact_summary, requires_approval)
        VALUES (?, ?, 'PENDING_APPROVAL', ?, ?, ?, 1)
        """
        metadata_db.execute(query, (plan_id, incident_id, sql_fix, pyspark_fix or "", impact_summary))

        return ToolResult(
            success=True,
            tool_name=self.name,
            output={
                "plan_id": plan_id,
                "incident_id": incident_id,
                "status": "PENDING_APPROVAL",
                "sql_fix": sql_fix,
                "pyspark_fix": pyspark_fix,
                "impact_summary": impact_summary,
                "requires_approval": True
            },
            execution_time_ms=(time.time() - t0) * 1000
        )

# 13. generate_sql_fix
class GenerateSQLFixInput(BaseModel):
    table_name: str = Field(..., description="Target table for SQL fix (e.g., 'claims')")
    fix_type: str = Field(..., description="Type of fix ('DELETE_STALE_REFS', 'UPDATE_NULLS', 'ALTER_COLUMN')")
    condition: Optional[str] = Field(None, description="SQL WHERE clause filter condition")

class GenerateSQLFixTool(BaseTool):
    name = "generate_sql_fix"
    description = "Generate standardized parameterized SQL DDL/DML cleanup query for pipeline errors."
    args_model = GenerateSQLFixInput

    def execute(self, table_name: str, fix_type: str, condition: Optional[str] = None) -> ToolResult:
        t0 = time.time()
        if fix_type == "DELETE_STALE_REFS":
            sql = f"SELECT * FROM {table_name} WHERE {condition or '1=1'}"
            cleanup_sql = f"DELETE FROM {table_name} WHERE {condition}" if condition else f"SELECT * FROM {table_name}"
        elif fix_type == "UPDATE_NULLS":
            sql = f"UPDATE {table_name} SET amount = 0.0 WHERE amount IS NULL"
            cleanup_sql = sql
        else:
            sql = f"SELECT * FROM {table_name}"
            cleanup_sql = sql

        return ToolResult(
            success=True,
            tool_name=self.name,
            output={
                "target_table": table_name,
                "fix_type": fix_type,
                "generated_sql": cleanup_sql
            },
            execution_time_ms=(time.time() - t0) * 1000
        )

# 14. generate_pyspark_fix
class GeneratePySparkFixInput(BaseModel):
    table_name: str = Field(..., description="Target dataset table")
    transformation_logic: str = Field(..., description="Description of Spark transformation logic")

class GeneratePySparkFixTool(BaseTool):
    name = "generate_pyspark_fix"
    description = "Generate PySpark script for complex batch data cleaning, filtering, or schema mapping."
    args_model = GeneratePySparkFixInput

    def execute(self, table_name: str, transformation_logic: str) -> ToolResult:
        t0 = time.time()
        spark_code = f"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when

spark = SparkSession.builder.appName("DataOps_Remediation_{table_name}").getOrCreate()
df = spark.read.parquet("data/parquet/{table_name}.parquet")

# Apply remediation logic: {transformation_logic}
if "{table_name}" == "claims":
    df_clean = df.filter(col("plan_id") != "PLAN-104").filter(col("gaid_id") != "GAID-999")
elif "{table_name}" == "transactions":
    df_clean = df.fillna({{"amount": 0.0, "currency": "USD"}})
else:
    df_clean = df

df_clean.write.mode("overwrite").parquet("data/parquet/{table_name}.parquet")
print("PySpark remediation completed successfully.")
"""
        return ToolResult(
            success=True,
            tool_name=self.name,
            output={
                "table_name": table_name,
                "generated_pyspark_code": spark_code.strip()
            },
            execution_time_ms=(time.time() - t0) * 1000
        )

# 15. simulate_impact
class SimulateImpactInput(BaseModel):
    target_table: str = Field(..., description="Target parquet table being modified")
    filter_condition: str = Field(..., description="SQL WHERE clause filter condition to simulate")

class SimulateImpactTool(BaseTool):
    name = "simulate_impact"
    description = "Dry-run SQL query to calculate exact number of affected rows and downstream datasets before execution."
    args_model = SimulateImpactInput

    def execute(self, target_table: str, filter_condition: str) -> ToolResult:
        t0 = time.time()
        try:
            total_res = analytical_db.query(f"SELECT count(*) as total FROM {target_table}")
            affected_res = analytical_db.query(f"SELECT count(*) as affected FROM {target_table} WHERE {filter_condition}")
            
            total_rows = total_res[0]["total"] if total_res else 0
            affected_rows = affected_res[0]["affected"] if affected_res else 0
            remaining_rows = total_rows - affected_rows

            # Lineage downstream impact check
            downstream = metadata_db.fetch_all("SELECT target_table FROM lineage WHERE source_table = ?", (target_table,))
            downstream_tables = [d["target_table"] for d in downstream]

            return ToolResult(
                success=True,
                tool_name=self.name,
                output={
                    "target_table": target_table,
                    "total_rows_before": total_rows,
                    "affected_rows_count": affected_rows,
                    "remaining_rows_after": remaining_rows,
                    "affected_percentage": round((affected_rows / total_rows * 100), 2) if total_rows > 0 else 0.0,
                    "downstream_impacted_tables": downstream_tables
                },
                execution_time_ms=(time.time() - t0) * 1000
            )
        except Exception as e:
            return ToolResult(success=False, tool_name=self.name, output={}, error=str(e))
