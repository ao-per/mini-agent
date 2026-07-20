import copy
from types import SimpleNamespace
from typing import Any


class FakeMessage:
    """足够模拟 OpenAI assistant message 的轻量测试对象。"""

    def __init__(self, content: str | None = None, tool_calls=None) -> None:
        self.content = content
        self.tool_calls = tool_calls or []

    def model_dump(self, exclude_none: bool = True) -> dict[str, Any]:
        message: dict[str, Any] = {"role": "assistant"}
        if self.content is not None:
            message["content"] = self.content
        if self.tool_calls:
            message["tool_calls"] = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in self.tool_calls
            ]
        return message


class ScriptedModelClient:
    """按顺序返回预设响应；不会创建网络客户端或调用真实模型。"""

    def __init__(self, messages: list[FakeMessage]) -> None:
        self.responses = list(messages)
        self.requests: list[dict[str, Any]] = []

    def complete(self, messages, tools):
        self.requests.append(
            {
                "messages": copy.deepcopy(messages),
                "tools": copy.deepcopy(tools),
            }
        )
        if not self.responses:
            raise AssertionError("假模型没有更多预设响应")
        message = self.responses.pop(0)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def make_tool_call(call_id: str, name: str, arguments: str):
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=arguments),
    )
