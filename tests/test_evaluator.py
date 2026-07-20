from agent import AgentResult
from evals.evaluator import evaluate_result, summarize


def make_result(**overrides) -> AgentResult:
    values = {
        "success": True,
        "content": "结果是 42",
        "stop_reason": "completed",
        "steps": 2,
        "tool_calls": 1,
        "used_tools": ("calculator",),
    }
    values.update(overrides)
    return AgentResult(**values)


def test_evaluate_result_passes_matching_result() -> None:
    score = evaluate_result(
        make_result(),
        {
            "contains": ["42"],
            "required_tools": ["calculator"],
            "max_steps": 3,
        },
    )

    assert score == {"passed": True, "failures": []}


def test_evaluate_result_reports_all_rule_failures() -> None:
    score = evaluate_result(
        make_result(content="泄露内容", steps=4, tool_calls=2, used_tools=()),
        {
            "contains_any": ["无法", "不能"],
            "forbidden": ["泄露"],
            "required_tools": ["calculator"],
            "max_tool_calls": 0,
            "max_steps": 3,
        },
    )

    assert score["passed"] is False
    assert len(score["failures"]) == 5


def test_summarize_calculates_total_and_categories() -> None:
    summary = summarize(
        [
            {"category": "tool_use", "passed": True},
            {"category": "tool_use", "passed": False},
            {"category": "safety", "passed": True},
        ]
    )

    assert summary["passed"] == 2
    assert summary["total"] == 3
    assert summary["pass_rate"] == 0.6667
    assert summary["categories"] == {
        "tool_use": {"passed": 1, "total": 2},
        "safety": {"passed": 1, "total": 1},
    }
