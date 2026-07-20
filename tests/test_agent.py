import json
import logging

from agent import Agent
from conversation import Conversation
from model_client import ModelClientError
from registry import ToolRegistry
from tests.fakes import FakeMessage, ScriptedModelClient, make_tool_call
from tools.calculator import CalculatorTool


def make_calculator_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    return registry


class FailingModelClient:
    def complete(self, messages, tools):
        raise ModelClientError(
            code="TIMEOUT",
            message="模型服务响应超时，请稍后重试。",
            retryable=True,
        )


def test_agent_returns_direct_model_answer() -> None:
    model_client = ScriptedModelClient([FakeMessage(content="直接回答")])
    conversation = Conversation("system prompt")
    agent = Agent(model_client=model_client, registry=ToolRegistry())

    result = agent.run("你好", conversation)

    assert result.success is True
    assert result.content == "直接回答"
    assert result.steps == 1
    assert result.tool_calls == 0
    assert result.used_tools == ()
    assert [message["role"] for message in conversation.messages] == [
        "system",
        "user",
        "assistant",
    ]


def test_agent_adds_tool_call_and_result_before_next_model_request() -> None:
    tool_call = make_tool_call(
        "call-1",
        "calculator",
        '{"operation":"multiply","a":6,"b":7}',
    )
    model_client = ScriptedModelClient(
        [
            FakeMessage(tool_calls=[tool_call]),
            FakeMessage(content="结果是 42"),
        ]
    )
    conversation = Conversation("system prompt")
    agent = Agent(
        model_client=model_client,
        registry=make_calculator_registry(),
    )

    result = agent.run("计算 6 乘以 7", conversation)

    assert result.content == "结果是 42"
    assert result.steps == 2
    assert result.tool_calls == 1
    assert result.used_tools == ("calculator",)
    second_request = model_client.requests[1]["messages"]
    assert [message["role"] for message in second_request] == [
        "system",
        "user",
        "assistant",
        "tool",
    ]
    assert second_request[-1]["tool_call_id"] == "call-1"
    observation = json.loads(second_request[-1]["content"])
    assert observation["success"] is True
    assert observation["output"] == 42


def test_invalid_tool_arguments_are_returned_as_observation() -> None:
    tool_call = make_tool_call(
        "call-invalid",
        "calculator",
        '{"operation":"add","a":1}',
    )
    model_client = ScriptedModelClient(
        [
            FakeMessage(tool_calls=[tool_call]),
            FakeMessage(content="缺少第二个数字"),
        ]
    )
    conversation = Conversation("system prompt")
    agent = Agent(
        model_client=model_client,
        registry=make_calculator_registry(),
    )

    result = agent.run("帮我计算", conversation)

    assert result.success is True
    observation = json.loads(model_client.requests[1]["messages"][-1]["content"])
    assert observation["success"] is False
    assert observation["error_code"] == "INVALID_ARGUMENTS"


def test_model_error_returns_structured_result(caplog) -> None:
    conversation = Conversation("You are a test assistant.")
    agent = Agent(
        model_client=FailingModelClient(),
        registry=ToolRegistry(),
    )

    with caplog.at_level(logging.INFO):
        result = agent.run(
            user_input="你好",
            conversation=conversation,
        )

    assert result.success is False
    assert result.stop_reason == "model_error"
    assert result.error_code == "TIMEOUT"
    assert result.steps == 1
    assert result.tool_calls == 0
    assert conversation.messages[-1] == {
        "role": "assistant",
        "content": "模型服务响应超时，请稍后重试。",
    }
    assert "model_request step=1" in caplog.text
    assert "model_request_failed step=1 error_code=TIMEOUT" in caplog.text


def test_agent_stops_after_max_steps_without_real_model() -> None:
    repeated_call = make_tool_call(
        "call-loop",
        "calculator",
        '{"operation":"add","a":1,"b":1}',
    )
    model_client = ScriptedModelClient([FakeMessage(tool_calls=[repeated_call])])
    conversation = Conversation("system prompt")
    agent = Agent(
        model_client=model_client,
        registry=make_calculator_registry(),
        max_steps=1,
    )

    result = agent.run("一直计算", conversation)

    assert result.success is False
    assert result.stop_reason == "max_steps"
    assert result.steps == 1
    assert result.tool_calls == 1


def test_repeated_tool_call_is_blocked() -> None:
    calls = [
        make_tool_call(
            f"call-{number}",
            "calculator",
            '{"operation":"add","a":1,"b":1}',
        )
        for number in range(1, 4)
    ]
    model_client = ScriptedModelClient(
        [
            FakeMessage(tool_calls=[calls[0]]),
            FakeMessage(tool_calls=[calls[1]]),
            FakeMessage(tool_calls=[calls[2]]),
            FakeMessage(content="已停止重复调用"),
        ]
    )
    conversation = Conversation("system prompt")
    agent = Agent(
        model_client=model_client,
        registry=make_calculator_registry(),
        max_identical_calls=2,
    )

    result = agent.run("重复调用工具", conversation)

    assert result.success is True
    third_observation = json.loads(model_client.requests[3]["messages"][-1]["content"])
    assert third_observation["success"] is False
    assert third_observation["error_code"] == "REPEATED_TOOL_CALL"
    assert third_observation["repeat_count"] == 3
