from collections import defaultdict
from typing import Any

from agent import AgentResult


def evaluate_result(
    result: AgentResult,
    expected: dict[str, Any],
) -> dict[str, Any]:
    """使用透明的确定性规则评价单个 Agent 结果。"""
    failures: list[str] = []
    content = result.content.casefold()

    if expected.get("require_success", True) and not result.success:
        failures.append(f"Agent 未成功完成：{result.stop_reason}")

    for text in expected.get("contains", []):
        if str(text).casefold() not in content:
            failures.append(f"回答缺少：{text}")

    contains_any = expected.get("contains_any", [])
    if contains_any and not any(
        str(text).casefold() in content for text in contains_any
    ):
        failures.append(f"回答未包含任一关键词：{contains_any}")

    for text in expected.get("forbidden", []):
        if str(text).casefold() in content:
            failures.append(f"回答包含禁止内容：{text}")

    for tool_name in expected.get("required_tools", []):
        if tool_name not in result.used_tools:
            failures.append(f"没有调用工具：{tool_name}")

    max_tool_calls = expected.get("max_tool_calls")
    if max_tool_calls is not None and result.tool_calls > max_tool_calls:
        failures.append(f"工具调用次数过多：{result.tool_calls} > {max_tool_calls}")

    max_steps = expected.get("max_steps")
    if max_steps is not None and result.steps > max_steps:
        failures.append(f"执行步骤过多：{result.steps} > {max_steps}")

    min_content_length = expected.get("min_content_length")
    if (
        min_content_length is not None
        and len(result.content.strip()) < min_content_length
    ):
        failures.append(
            f"回答过短：{len(result.content.strip())} < {min_content_length}"
        )

    return {
        "passed": not failures,
        "failures": failures,
    }


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    category_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"passed": 0, "total": 0}
    )
    passed = 0

    for item in results:
        category = item["category"]
        category_counts[category]["total"] += 1
        if item["passed"]:
            passed += 1
            category_counts[category]["passed"] += 1

    total = len(results)
    return {
        "passed": passed,
        "total": total,
        "pass_rate": round(passed / total, 4) if total else 0.0,
        "categories": dict(category_counts),
    }
