import time
from typing import Optional
from pydantic import BaseModel, Field
from app.tools.base import BaseTool, ToolResult
from app.core.db_metadata import metadata_db
from app.config import settings

# 1. inspect_pipeline
class InspectPipelineInput(BaseModel):
    pipeline_id: str = Field(..., description="The unique ID of the pipeline to inspect (e.g., PIPE-001)")

class InspectPipelineTool(BaseTool):
    name = "inspect_pipeline"
    description = "Inspect pipeline configuration, domain metadata, schedule, and current status."
    args_model = InspectPipelineInput

    def execute(self, pipeline_id: str) -> ToolResult:
        t0 = time.time()
        pipeline = metadata_db.fetch_one("SELECT * FROM pipelines WHERE pipeline_id = ?", (pipeline_id,))
        if not pipeline:
            return ToolResult(
                success=False, tool_name=self.name, output={}, error=f"Pipeline '{pipeline_id}' not found."
            )
        
        runs = metadata_db.fetch_all("SELECT status FROM pipeline_runs WHERE pipeline_id = ?", (pipeline_id,))
        total_runs = len(runs)
        failed_runs = sum(1 for r in runs if r["status"] == "FAILED")
        success_rate = round(((total_runs - failed_runs) / total_runs * 100), 2) if total_runs > 0 else 100.0

        output = {
            "pipeline": pipeline,
            "metrics": {
                "total_runs": total_runs,
                "failed_runs": failed_runs,
                "success_rate_pct": success_rate
            }
        }
        return ToolResult(
            success=True, tool_name=self.name, output=output, execution_time_ms=(time.time() - t0) * 1000
        )

# 2. get_pipeline_runs
class GetPipelineRunsInput(BaseModel):
    pipeline_id: str = Field(..., description="The pipeline ID to fetch execution runs for")
    limit: int = Field(5, description="Maximum number of recent runs to return")

class GetPipelineRunsTool(BaseTool):
    name = "get_pipeline_runs"
    description = "Get recent execution run logs, status codes, and error traces for a pipeline."
    args_model = GetPipelineRunsInput

    def execute(self, pipeline_id: str, limit: int = 5) -> ToolResult:
        t0 = time.time()
        runs = metadata_db.fetch_all(
            "SELECT * FROM pipeline_runs WHERE pipeline_id = ? ORDER BY start_time DESC LIMIT ?",
            (pipeline_id, limit)
        )
        return ToolResult(
            success=True,
            tool_name=self.name,
            output={"pipeline_id": pipeline_id, "count": len(runs), "runs": runs},
            execution_time_ms=(time.time() - t0) * 1000
        )

# 3. search_logs
class SearchLogsInput(BaseModel):
    run_id: Optional[str] = Field(None, description="Optional pipeline run_id (e.g. RUN-001-A)")
    keyword: Optional[str] = Field(None, description="Keyword to search in log traces (e.g. 'ERROR', 'TERMINATED')")

class SearchLogsTool(BaseTool):
    name = "search_logs"
    description = "Search log trace files for error messages, stack traces, and detailed execution info."
    args_model = SearchLogsInput

    def execute(self, run_id: Optional[str] = None, keyword: Optional[str] = None) -> ToolResult:
        t0 = time.time()
        matched_logs = []

        if run_id:
            run = metadata_db.fetch_one("SELECT log_path FROM pipeline_runs WHERE run_id = ?", (run_id,))
            if run and run.get("log_path"):
                log_file = settings.BASE_DIR / run["log_path"]
                if log_file.exists():
                    with open(log_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        if keyword:
                            lines = [l for l in lines if keyword.lower() in l.lower()]
                        matched_logs.append({"run_id": run_id, "lines": lines})
        else:
            # Search all log files
            for log_file in settings.LOGS_DIR.glob("*.log"):
                with open(log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if keyword:
                        lines = [l for l in lines if keyword.lower() in l.lower()]
                    if lines:
                        matched_logs.append({"file": log_file.name, "lines": lines[:20]})

        return ToolResult(
            success=True,
            tool_name=self.name,
            output={"matches_count": len(matched_logs), "results": matched_logs},
            execution_time_ms=(time.time() - t0) * 1000
        )
