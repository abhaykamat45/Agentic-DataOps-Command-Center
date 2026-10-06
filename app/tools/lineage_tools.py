import time
from pydantic import BaseModel, Field
from app.tools.base import BaseTool, ToolResult
from app.core.db_metadata import metadata_db

# 11. find_dependencies
class FindDependenciesInput(BaseModel):
    table_name: str = Field(..., description="Table name to discover upstream sources and downstream target dependencies for")

class FindDependenciesTool(BaseTool):
    name = "find_dependencies"
    description = "Trace lineage dependency graph to determine upstream data sources and downstream affected datasets."
    args_model = FindDependenciesInput

    def execute(self, table_name: str) -> ToolResult:
        t0 = time.time()
        # Upstream: tables where target_table = table_name
        upstream = metadata_db.fetch_all("SELECT * FROM lineage WHERE target_table = ?", (table_name,))
        # Downstream: tables where source_table = table_name
        downstream = metadata_db.fetch_all("SELECT * FROM lineage WHERE source_table = ?", (table_name,))

        return ToolResult(
            success=True,
            tool_name=self.name,
            output={
                "table_name": table_name,
                "upstream_sources": [u["source_table"] for u in upstream],
                "downstream_targets": [d["target_table"] for d in downstream],
                "lineage_records": upstream + downstream
            },
            execution_time_ms=(time.time() - t0) * 1000
        )
