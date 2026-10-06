from app.tools.base import BaseTool, ToolResult, tool_registry
from app.tools.inspect_tools import InspectPipelineTool, GetPipelineRunsTool, SearchLogsTool
from app.tools.schema_tools import InspectSchemaTool, CompareSchemasTool, ProfileDatasetTool
from app.tools.sql_tools import RunSQLTool, ExecuteSQLTool
from app.tools.dq_tools import RunDataQualityCheckTool, DetectAnomaliesTool
from app.tools.lineage_tools import FindDependenciesTool
from app.tools.remediation_tools import GenerateRemediationPlanTool, GenerateSQLFixTool, GeneratePySparkFixTool, SimulateImpactTool
from app.tools.execution_tools import ExecutePipelineTool, VerifyRemediationTool

# Register all tools in global tool registry
tools_to_register = [
    InspectPipelineTool(),
    GetPipelineRunsTool(),
    SearchLogsTool(),
    InspectSchemaTool(),
    CompareSchemasTool(),
    ProfileDatasetTool(),
    RunSQLTool(),
    ExecuteSQLTool(),
    RunDataQualityCheckTool(),
    DetectAnomaliesTool(),
    FindDependenciesTool(),
    GenerateRemediationPlanTool(),
    GenerateSQLFixTool(),
    GeneratePySparkFixTool(),
    SimulateImpactTool(),
    ExecutePipelineTool(),
    VerifyRemediationTool()
]

for tool in tools_to_register:
    tool_registry.register(tool)

__all__ = ["tool_registry", "ToolResult", "BaseTool"]
