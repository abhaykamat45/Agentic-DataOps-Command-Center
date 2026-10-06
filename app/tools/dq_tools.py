import time
from typing import Optional, List
from pydantic import BaseModel, Field
from app.tools.base import BaseTool, ToolResult
from app.core.db_metadata import metadata_db
from app.core.db_analytical import analytical_db

# 9. run_data_quality_check
class RunDQCheckInput(BaseModel):
    table_name: str = Field(..., description="Table name to evaluate Data Quality rules for (e.g., 'claims', 'transactions')")

class RunDataQualityCheckTool(BaseTool):
    name = "run_data_quality_check"
    description = "Run configurable data quality rules (null rate, referential integrity, allowed values) against a table."
    args_model = RunDQCheckInput

    def execute(self, table_name: str) -> ToolResult:
        t0 = time.time()
        rules = metadata_db.fetch_all("SELECT * FROM data_quality_rules WHERE table_name = ? AND enabled = 1", (table_name,))
        if not rules:
            return ToolResult(
                success=True,
                tool_name=self.name,
                output={"table_name": table_name, "rules_evaluated": 0, "violations": []},
                execution_time_ms=(time.time() - t0) * 1000
            )

        violations = []
        for r in rules:
            rule_type = r["rule_type"]
            col = r["column_name"]
            threshold = r["threshold"]

            if rule_type == "NULL_RATE":
                res = analytical_db.query(f"SELECT COUNT(*) as total, COUNT({col}) as non_null FROM {table_name}")
                if res:
                    tot = res[0]["total"]
                    non_null = res[0]["non_null"]
                    null_rate = (tot - non_null) / tot if tot > 0 else 0.0
                    if null_rate > threshold:
                        violations.append({
                            "rule_id": r["rule_id"],
                            "rule_type": rule_type,
                            "column": col,
                            "actual_value": round(null_rate, 4),
                            "threshold": threshold,
                            "status": "VIOLATED",
                            "description": f"Null rate {round(null_rate*100, 2)}% exceeds max allowed threshold {round(threshold*100, 2)}%"
                        })
            elif rule_type == "REFERENTIAL_INTEGRITY":
                # Check claims -> plans or claims -> gaids
                if table_name == "claims" and col == "plan_id":
                    invalid = analytical_db.query("""
                        SELECT c.claim_id, c.plan_id, p.status 
                        FROM claims c 
                        LEFT JOIN plans p ON c.plan_id = p.plan_id 
                        WHERE p.status IS NULL OR p.status = 'TERMINATED'
                    """)
                    if invalid:
                        violations.append({
                            "rule_id": r["rule_id"],
                            "rule_type": rule_type,
                            "column": col,
                            "violating_records_count": len(invalid),
                            "status": "VIOLATED",
                            "description": f"Found {len(invalid)} records referencing TERMINATED or non-existent plan IDs in 'plans' master table."
                        })
                elif table_name == "claims" and col == "gaid_id":
                    invalid_gaid = analytical_db.query("""
                        SELECT c.claim_id, c.gaid_id, g.status 
                        FROM claims c 
                        LEFT JOIN gaids g ON c.gaid_id = g.gaid_id 
                        WHERE g.status IS NULL OR g.status != 'ACTIVE'
                    """)
                    if invalid_gaid:
                        violations.append({
                            "rule_id": r["rule_id"],
                            "rule_type": rule_type,
                            "column": col,
                            "violating_records_count": len(invalid_gaid),
                            "status": "VIOLATED",
                            "description": f"Found {len(invalid_gaid)} records referencing INACTIVE/missing GAID IDs."
                        })

        return ToolResult(
            success=True,
            tool_name=self.name,
            output={
                "table_name": table_name,
                "rules_evaluated": len(rules),
                "has_violations": len(violations) > 0,
                "violations_count": len(violations),
                "violations": violations
            },
            execution_time_ms=(time.time() - t0) * 1000
        )

# 10. detect_anomalies
class DetectAnomaliesInput(BaseModel):
    table_name: str = Field(..., description="Table name to scan for statistical or structural anomalies")

class DetectAnomaliesTool(BaseTool):
    name = "detect_anomalies"
    description = "Detect anomalies such as null spikes, duplicate records, orphan foreign keys, or stale records."
    args_model = DetectAnomaliesInput

    def execute(self, table_name: str) -> ToolResult:
        t0 = time.time()
        anomalies = []

        try:
            df = analytical_db.query_df(f"SELECT * FROM {table_name}")
        except Exception as e:
            return ToolResult(success=False, tool_name=self.name, output={}, error=str(e))

        # 1. Duplicate check
        dups = df.duplicated().sum()
        if dups > 0:
            anomalies.append({"type": "DUPLICATE_ROWS", "count": int(dups), "severity": "MEDIUM"})

        # 2. Null spikes (>10% nulls)
        for col in df.columns:
            null_pct = df[col].isnull().mean()
            if null_pct > 0.10:
                anomalies.append({"type": "NULL_SPIKE", "column": col, "null_pct": round(null_pct*100, 2), "severity": "HIGH"})

        # 3. Plan & GAID Foreign Key anomalies
        if table_name in ["claims", "benefits"]:
            plan_anomalies = analytical_db.query(f"""
                SELECT t.plan_id, count(*) as cnt 
                FROM {table_name} t 
                JOIN plans p ON t.plan_id = p.plan_id 
                WHERE p.status = 'TERMINATED' 
                GROUP BY t.plan_id
            """)
            if plan_anomalies:
                anomalies.append({
                    "type": "ORPHAN_FOREIGN_KEY_TERMINATED_PLAN",
                    "details": plan_anomalies,
                    "severity": "CRITICAL",
                    "description": f"Found active records in '{table_name}' referencing TERMINATED Plan IDs."
                })

        return ToolResult(
            success=True,
            tool_name=self.name,
            output={
                "table_name": table_name,
                "anomalies_found": len(anomalies),
                "anomalies": anomalies
            },
            execution_time_ms=(time.time() - t0) * 1000
        )
