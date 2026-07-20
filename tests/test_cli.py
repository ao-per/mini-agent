from agent import AgentResult
from cli import run_cli
from conversation import Conversation


class RecordingAgent:
    def __init__(self) -> None:
        self.conversation_ids: list[int] = []

    def run(self, user_input: str, conversation: Conversation) -> AgentResult:
        self.conversation_ids.append(id(conversation))
        conversation.add_user(user_input)
        answer = f"收到：{user_input}"
        conversation.add_assistant({"role": "assistant", "content": answer})
        return AgentResult(
            success=True,
            content=answer,
            stop_reason="completed",
            steps=1,
            tool_calls=0,
        )


def make_input(values: list[str]):
    iterator = iter(values)
    return lambda _: next(iterator)


def test_cli_keeps_conversation_between_turns() -> None:
    agent = RecordingAgent()
    conversation = Conversation("system prompt")
    output: list[str] = []

    run_cli(
        agent=agent,  # type: ignore[arg-type]
        conversation=conversation,
        input_fn=make_input(["第一轮", "第二轮", "exit"]),
        output_fn=output.append,
    )

    assert agent.conversation_ids == [id(conversation), id(conversation)]
    assert [message["content"] for message in conversation.messages] == [
        "system prompt",
        "第一轮",
        "收到：第一轮",
        "第二轮",
        "收到：第二轮",
    ]
    assert output[-1] == "再见！"


def test_reset_clears_previous_messages() -> None:
    agent = RecordingAgent()
    conversation = Conversation("system prompt")

    run_cli(
        agent=agent,  # type: ignore[arg-type]
        conversation=conversation,
        input_fn=make_input(["旧消息", "/reset", "新消息", "/quit"]),
        output_fn=lambda _: None,
    )

    assert [message["content"] for message in conversation.messages] == [
        "system prompt",
        "新消息",
        "收到：新消息",
    ]
