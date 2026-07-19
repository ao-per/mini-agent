from agent import Agent
from model_client import ModelClient
from registry import ToolRegistry
from tools.calculator import CalculatorTool
from tools.current_time import CurrentTimeTool
from tools.search_notes import SearchNotesTool


def create_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(CurrentTimeTool())
    registry.register(SearchNotesTool())
    return registry


def main() -> None:
    agent = Agent(
        model_client=ModelClient(),
        registry=create_registry(),
        max_steps=8,
    )

    user_input = input("You: ")
    answer = agent.run(user_input)

    print(f"Agent: {answer}")


if __name__ == "__main__":
    main()