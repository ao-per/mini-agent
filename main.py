from agent import SYSTEM_PROMPT, Agent
from cli import run_cli
from config import settings
from conversation import Conversation
from logging_config import configure_logging
from model_client import ModelClient
from registry import ToolRegistry
from tools.calculator import CalculatorTool
from tools.current_time import CurrentTimeTool
from tools.search_notes import SearchNotesTool


def create_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(CurrentTimeTool())
    registry.register(SearchNotesTool(notes_root=settings.notes_root))
    return registry


def main() -> None:
    configure_logging(settings.log_level)

    agent = Agent(
        model_client=ModelClient(),
        registry=create_registry(),
        max_steps=8,
        max_identical_calls=2,
    )
    conversation = Conversation(SYSTEM_PROMPT)
    run_cli(agent=agent, conversation=conversation)


if __name__ == "__main__":
    main()
