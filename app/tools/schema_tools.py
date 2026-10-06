import time
from typing import Optional
from pydantic import BaseModel, Field
from app.tools.base import BaseTool, ToolResult
from app.core.db_metadata import metadata_db
from app.core.db_analytical import analytical_db

# 4. inspect_schema
class InspectSchemaInput(BaseModel):
    table_name: str = Field(..., description="Name of the analytical table to inspect schema for (e.g., 'claims', 'plans')")

class InspectSchemaTool(BaseTool):
    name = "inspect_schema"
    description = "Inspect column schema, data types, nullability, and primary keys for source/target tables."
    args_model = InspectSchemaInput

    def execute(self, table_name: str) -> ToolResult:
        t0 = time.time()
        # Fetch metadata schema
        meta_schema = metadata_db.fetch_all(
            "SELECT column_name, data_type, is_nullable, is_primary_key FROM schemas WHERE table_name = ?",
            (table_name,)
        )
        
        # Also describe active parquet file
        try:
            parquet_schema = analytical_db.get_table_schema(table_name)
        except Exception as e:
            parquet_schema = f"Could not inspect parquet schema: {str(e)}"

        return ToolResult(
            success=True,
            tool_name=self.name,
            output={
                "table_name": table_name,
                "metadata_schema": meta_schema,
                "actual_parquet_schema": parquet_schema
            },
            execution_time_ms=(time.time() - t0) * 1000
        )

# 5. compare_schemas
class CompareSchemasInput(BaseModel):
    table_name: str = Field(..., description="The table to compare schema against expected metadata specification")

class CompareSchemasTool(BaseTool):
    name = "compare_schemas"
    description = "Compare actual physical dataset schema against expected metadata version to detect schema drift."
    args_model = CompareSchemasInput

    def execute(self, table_name: str) -> ToolResult:
        t0 = time.time()
        expected = metadata_db.fetch_all("SELECT column_name, data_type FROM schemas WHERE table_name = ?", (table_name,))
        if not expected:
            return ToolResult(
                success=False, tool_name=self.name, output={}, error=f"No expected metadata schema registered for table '{table_name}'."
            )

        try:
            actual_desc = analytical_db.get_table_schema(table_name)
        except Exception as e:
            return ToolResult(success=False, tool_name=self.name, output={}, error=str(e))

        exp_dict = {row["column_name"]: row["data_type"].upper() for row in expected}
        act_dict = {row["column_name"]: row["column_type"].upper() for row in actual_desc}

        drifts = []
        for col, exp_type in exp_dict.items():
            if col not in act_dict:
                drifts.append({"column": col, "issue": "MISSING_COLUMN", "expected": exp_type, "actual": None})
            elif exp_type != act_dict[col] and not (exp_type in ["VARCHAR", "TEXT", "STRING"] and act_dict[col] in ["VARCHAR", "TEXT", "STRING"]):
                drifts.append({"column": col, "issue": "TYPE_MISMATCH", "expected": exp_type, "actual": act_dict[col]})

        for col in act_dict:
            if col not in exp_dict:
                drifts.append({"column": col, "issue": "UNEXPECTED_NEW_COLUMN", "expected": None, "actual": act_dict[col]})

        return ToolResult(
            success=True,
            tool_name=self.name,
            output={
                "table_name": table_name,
                "has_schema_drift": len(drifts) > 0,
                "drift_count": len(drifts),
                "drifts": drifts
            },
            execution_time_ms=(time.time() - t0) * 1000
        )

# 6. profile_dataset
class ProfileDatasetInput(BaseModel):
    table_name: str = Field(..., description="Table name to profile (e.g. 'transactions', 'customers')")

class ProfileDatasetTool(BaseTool):
    name = "profile_dataset"
    description = "Profile dataset to compute row counts, null rates, duplicate rates, distinct counts, and statistics."
    args_model = ProfileDatasetInput

    def execute(self, table_name: str) -> ToolResult:
        t0 = time.time()
        try:
            df = analytical_db.query_df(f"SELECT * FROM {table_name}")
        except Exception as e:
            return ToolResult(success=False, tool_name=self.name, output={}, error=str(e))

        total_rows = len(df)
        col_profiles = {}
        for col in df.columns:
            null_count = int(df[col].isnull().sum())
            null_rate = round(null_count / total_rows, 4) if total_rows > 0 else 0.0
            distinct_count = int(df[col].nunique())

            col_profiles[col] = {
                "null_count": null_count,
                "null_rate": null_rate,
                "distinct_count": distinct_count,
                "sample_values": [str(x) for x in df[col].dropna().unique()[:3]]
            }

        return ToolResult(
            success=True,
            tool_name=self.name,
            output={
                "table_name": table_name,
                "total_rows": total_rows,
                "column_profiles": col_profiles
            },
            execution_time_ms=(time.time() - t0) * 1000
        )
