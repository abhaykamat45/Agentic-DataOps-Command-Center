from abc import ABC, abstractmethod
from typing import Dict, Any, Type, List, Optional
from pydantic import BaseModel, Field

class ToolResult(BaseModel):
    success: bool
    tool_name: str
    output: Dict[str, Any]
    error: Optional[str] = None
    execution_time_ms: float = 0.0

class BaseTool(ABC):
    name: str
    description: str
    is_destructive: bool = False
    args_model: Type[BaseModel]

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool logic and return ToolResult."""
        pass

    def to_llm_format(self) -> Dict[str, Any]:
        """Convert tool definition to JSON Schema format for OpenAI/Ollama tool calling."""
        schema = self.args_model.schema()
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": f"{self.description} {'[REQUIRES HUMAN APPROVAL]' if self.is_destructive else ''}",
                "parameters": {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", [])
                }
            }
        }

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[BaseTool]:
        return list(self._tools.values())

    def get_llm_tool_schemas(self) -> List[Dict[str, Any]]:
        return [tool.to_llm_format() for tool in self._tools.values()]

    def invoke(self, name: str, kwargs: Dict[str, Any], approval_token: Optional[str] = None) -> ToolResult:
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(
                success=False,
                tool_name=name,
                output={},
                error=f"Tool '{name}' is not registered in ToolRegistry."
            )

        # Destructive safety check
        if tool.is_destructive:
            if not approval_token:
                return ToolResult(
                    success=False,
                    tool_name=name,
                    output={},
                    error=f"SECURITY ERROR: Tool '{name}' is a DESTRUCTIVE operation requiring explicit human approval token. No token provided."
                )
            kwargs["approval_token"] = approval_token
            
            # Verify approval token in audit events
            from app.core.audit import audit_logger
            plan_id = kwargs.get("plan_id", "")
            if plan_id and not audit_logger.verify_approval_token(approval_token, plan_id):
                return ToolResult(
                    success=False,
                    tool_name=name,
                    output={},
                    error=f"SECURITY ERROR: Invalid or unverified approval token '{approval_token}' for plan '{plan_id}'."
                )

        try:
            # Validate args with Pydantic model
            validated_args = tool.args_model(**kwargs).dict()
            return tool.execute(**validated_args)
        except Exception as e:
            return ToolResult(
                success=False,
                tool_name=name,
                output={},
                error=f"Execution error in '{name}': {str(e)}"
            )

tool_registry = ToolRegistry()
