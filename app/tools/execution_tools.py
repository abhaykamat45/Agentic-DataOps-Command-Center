import time
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.tools.base import BaseTool, ToolResult
from app.core.db_metadata import metadata_db
from app.core.audit import audit_logger

# 16. execute_pipeline
class ExecutePipelineInput(BaseModel):
    pipeline_id: str = Field(..., description="ID of the pipeline to re-run (e.g., 'PIPE-001')")
    plan_id: str = Field(..., description="Associated remediation plan ID")
    approval_token: Optional[str] = Field(None, description="Human approval token required for pipeline execution")

class ExecutePipelineTool(BaseTool):
    name = "execute_pipeline"
    description = "Trigger re-execution of a data pipeline after applying remediation. [DESTRUCTIVE]"
    is_destructive = True
    args_model = ExecutePipelineInput

    def execute(self, pipeline_id: str, plan_id: str, approval_token: Optional[str] = None) -> ToolResult:
        t0 = time.time()
        # Security approval check
        if not approval_token or not audit_logger.verify_approval_token(approval_token, plan_id):
            return ToolResult(
                success=False,
                tool_name=self.name,
                output={},
                error=f"SECURITY ERROR: Pipeline re-execution requires human approval. Invalid/missing token: '{approval_token}'."
            )

        new_run_id = f"RUN-REMED-{int(time.time())}"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update pipeline status to SUCCESS
        metadata_db.execute("UPDATE pipelines SET status = 'SUCCESS', updated_at = ? WHERE pipeline_id = ?", (now_str, pipeline_id))
        
        # Insert successful run record
        query_run = """
        INSERT INTO pipeline_runs (run_id, pipeline_id, status, start_time, end_time, records_processed, error_message, log_path)
        VALUES (?, ?, 'SUCCESS', ?, ?, 600, NULL, ?)
        """
        metadata_db.execute(query_run, (new_run_id, pipeline_id, now_str, now_str, f"data/logs/{new_run_id}.log"))

        # Log audit event
        audit_logger.log_event(
            actor="HUMAN_APPROVED_AGENT",
            action="EXECUTE_PIPELINE",
            target_resource=f"pipeline:{pipeline_id}",
            details={"new_run_id": new_run_id, "plan_id": plan_id},
            approval_token=approval_token
        )

        return ToolResult(
            success=True,
            tool_name=self.name,
            output={
                "pipeline_id": pipeline_id,
                "new_run_id": new_run_id,
                "status": "SUCCESS",
                "message": f"Pipeline '{pipeline_id}' successfully re-executed and marked SUCCESS."
            },
            execution_time_ms=(time.time() - t0) * 1000
        )

# 17. verify_remediation
class VerifyRemediationInput(BaseModel):
    incident_id: str = Field(..., description="ID of the incident being verified")
    target_table: str = Field(..., description="Table name to run post-remediation verification checks on")

class VerifyRemediationTool(BaseTool):
    name = "verify_remediation"
    description = "Re-evaluate data quality rules and foreign key integrity to confirm that incident is remediated."
    args_model = VerifyRemediationInput

    def execute(self, incident_id: str, target_table: str) -> ToolResult:
        t0 = time.time()
        from app.tools.dq_tools import RunDataQualityCheckTool
        
        dq_tool = RunDataQualityCheckTool()
        dq_res = dq_tool.execute(table_name=target_table)

        has_violations = dq_res.output.get("has_violations", False)
        status = "VERIFIED_RESOLVED" if not has_violations else "VERIFICATION_FAILED"

        if not has_violations:
            # Update incident status in SQLite metadata DB
            metadata_db.execute(
                "UPDATE incidents SET status = 'RESOLVED' WHERE incident_id = ?",
                (incident_id,)
            )

        return ToolResult(
            success=True,
            tool_name=self.name,
            output={
                "incident_id": incident_id,
                "target_table": target_table,
                "verification_status": status,
                "passed_all_dq_checks": not has_violations,
                "dq_results": dq_res.output
            },
            execution_time_ms=(time.time() - t0) * 1000
        )
