from time import perf_counter
from typing import Any

from pydantic import BaseModel, ValidationError

from tools.base import Tool


class ToolResult(BaseModel):
    tool_name: str
    success: bool
    output: Any | None = None
    error_code: str | None = None
    error_message: str | None = None
    duration_ms: float


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")

        self._tools[tool.name] = tool

    def schemas(self) -> list[dict[str, Any]]:
        return [tool.schema() for tool in self._tools.values()]

    def execute(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> ToolResult:
        started_at = perf_counter()
        tool = self._tools.get(name)

        if tool is None:
            return ToolResult(
                tool_name=name,
                success=False,
                error_code="UNKNOWN_TOOL",
                error_message=f"Unknown tool: {name}",
                duration_ms=self._elapsed_ms(started_at),
            )

        try:
            validated_arguments = tool.args_model.model_validate(arguments)
            output = tool.run(validated_arguments)

            return ToolResult(
                tool_name=name,
                success=True,
                output=output,
                duration_ms=self._elapsed_ms(started_at),
            )

        except ValidationError as exc:
            return ToolResult(
                tool_name=name,
                success=False,
                error_code="INVALID_ARGUMENTS",
                error_message=str(exc),
                duration_ms=self._elapsed_ms(started_at),
            )

        except Exception as exc:
            return ToolResult(
                tool_name=name,
                success=False,
                error_code="TOOL_EXECUTION_ERROR",
                error_message=str(exc),
                duration_ms=self._elapsed_ms(started_at),
            )

    @staticmethod
    def _elapsed_ms(started_at: float) -> float:
        return round(
            (perf_counter() - started_at) * 1000,
            3,
        )
