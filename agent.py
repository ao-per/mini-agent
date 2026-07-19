import json
from json import JSONDecodeError
from typing import Any

from model_client import ModelClient
from registry import ToolRegistry


SYSTEM_PROMPT = """
You are a helpful assistant.

Use the provided tools when they are needed.
Do not fabricate tool results.
If a tool fails, use the error information to correct the call
or explain the failure to the user.
""".strip()


class Agent:
    def __init__(
        self,
        model_client: ModelClient,
        registry: ToolRegistry,
        max_steps: int = 8,
    ) -> None:
        self.model_client = model_client
        self.registry = registry
        self.max_steps = max_steps

    def run(self, user_input: str) -> str:
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_input,
            },
        ]

        for step in range(1, self.max_steps + 1):
            print(f"[step {step}] 请求模型")

            response = self.model_client.complete(
                messages=messages,
                tools=self.registry.schemas(),
            )

            message = response.choices[0].message

            # 必须保存模型产生的 tool_calls
            messages.append(
                message.model_dump(exclude_none=True)
            )

            if not message.tool_calls:
                return message.content or ""

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name

                print(f"[tool] {tool_name}")

                try:
                    arguments = json.loads(
                        tool_call.function.arguments
                    )

                    if not isinstance(arguments, dict):
                        raise TypeError(
                            "Tool arguments must be a JSON object"
                        )

                    result = self.registry.execute(
                        tool_name,
                        arguments,
                    )

                    output = result.model_dump_json()

                except (JSONDecodeError, TypeError) as exc:
                    output = json.dumps(
                        {
                            "tool_name": tool_name,
                            "success": False,
                            "error_code": "INVALID_JSON_ARGUMENTS",
                            "error_message": str(exc),
                        },
                        ensure_ascii=False,
                    )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": output,
                    }
                )

        raise RuntimeError(
            f"Agent exceeded max_steps={self.max_steps}"
        )