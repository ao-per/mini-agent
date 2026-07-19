import pytest

from registry import ToolRegistry
from tools.calculator import CalculatorTool


@pytest.fixture
def registry() -> ToolRegistry:
    tool_registry = ToolRegistry()
    tool_registry.register(CalculatorTool())
    return tool_registry


def test_execute_calculator(registry: ToolRegistry) -> None:
    result = registry.execute(
        "calculator",
        {
            "operation": "multiply",
            "a": 6,
            "b": 7,
        },
    )

    assert result.success is True
    assert result.output == 42


def test_unknown_tool(registry: ToolRegistry) -> None:
    result = registry.execute(
        "not_exists",
        {},
    )

    assert result.success is False
    assert result.error_code == "UNKNOWN_TOOL"


def test_invalid_arguments(registry: ToolRegistry) -> None:
    result = registry.execute(
        "calculator",
        {
            "operation": "multiply",
            "a": 6,
        },
    )

    assert result.success is False
    assert result.error_code == "INVALID_ARGUMENTS"


def test_divide_by_zero(registry: ToolRegistry) -> None:
    result = registry.execute(
        "calculator",
        {
            "operation": "divide",
            "a": 10,
            "b": 0,
        },
    )

    assert result.success is False
    assert result.error_code == "TOOL_EXECUTION_ERROR"


def test_duplicate_registration(
    registry: ToolRegistry,
) -> None:
    with pytest.raises(ValueError):
        registry.register(CalculatorTool())


def test_schema_is_strict(registry: ToolRegistry) -> None:
    schema = registry.schemas()[0]

    assert schema["type"] == "function"
    assert schema["function"]["name"] == "calculator"
    assert schema["function"]["parameters"]["type"] == "object"
