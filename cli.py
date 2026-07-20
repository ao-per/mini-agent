from collections.abc import Callable

from agent import Agent
from conversation import Conversation


EXIT_COMMANDS = {"exit", "quit", "/exit", "/quit"}


def run_cli(
    agent: Agent,
    conversation: Conversation,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> None:
    output_fn("Mini Agent 已启动。输入 /reset 清空对话，输入 exit 退出。")

    while True:
        try:
            user_input = input_fn("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            output_fn("再见！")
            return

        if not user_input:
            continue

        command = user_input.casefold()
        if command in EXIT_COMMANDS:
            output_fn("再见！")
            return

        if command == "/reset":
            conversation.reset()
            output_fn("对话历史已清空。")
            continue

        result = agent.run(
            user_input=user_input,
            conversation=conversation,
        )

        output_fn(f"Agent: {result.content}")
        output_fn(
            f"[success={result.success}, "
            f"stop_reason={result.stop_reason}, "
            f"steps={result.steps}, "
            f"tool_calls={result.tool_calls}, "
            f"error_code={result.error_code}]"
        )
