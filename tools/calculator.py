from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from tools.base import Tool


class CalculatorArgs(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    operation: Literal["add", "subtract", "multiply", "divide"] = Field(
        description="The arithmetic operation to perform."
    )
    a: float = Field(description="The first number.")
    b: float = Field(description="The second number.")


class CalculatorTool(Tool):
    name = "calculator"
    description = (
        "Perform basic arithmetic: addition, subtraction, multiplication, or division."
    )
    args_model = CalculatorArgs

    def run(self, arguments: BaseModel) -> float:
        if not isinstance(arguments, CalculatorArgs):
            raise TypeError("Expected CalculatorArgs")

        match arguments.operation:
            case "add":
                return arguments.a + arguments.b
            case "subtract":
                return arguments.a - arguments.b
            case "multiply":
                return arguments.a * arguments.b
            case "divide":
                if arguments.b == 0:
                    raise ValueError("Cannot divide by zero")
                return arguments.a / arguments.b
            case _:
                raise ValueError(f"Unsupported operation: {arguments.operation}")
