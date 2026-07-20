from typing import Any


class Conversation:
    def __init__(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt
        self.messages: list[dict[str, Any]] = []
        self.reset()

    def add_user(self, content: str) -> None:
        self.messages.append(
            {
                "role": "user",
                "content": content,
            }
        )

    def add_assistant(
        self,
        message: dict[str, Any],
    ) -> None:
        self.messages.append(message)

    def add_tool_result(
        self,
        tool_call_id: str,
        content: str,
    ) -> None:
        self.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": content,
            }
        )

    def reset(self) -> None:
        self.messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            }
        ]
