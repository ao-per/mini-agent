import argparse
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from agent import SYSTEM_PROMPT, Agent
from conversation import Conversation
from evals.evaluator import evaluate_result, summarize
from main import create_registry
from model_client import ModelClient


EVALS_ROOT = Path(__file__).resolve().parent
DEFAULT_CASES = EVALS_ROOT / "cases.json"
DEFAULT_RESULTS_DIR = EVALS_ROOT / "results"


def load_cases(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("评测集必须是 JSON 数组")

    required_fields = {"id", "category", "input", "expected"}
    seen_ids: set[str] = set()
    for index, case in enumerate(data, start=1):
        if not isinstance(case, dict) or not required_fields.issubset(case):
            raise ValueError(f"第 {index} 条评测案例缺少必填字段")
        if case["id"] in seen_ids:
            raise ValueError(f"评测案例 ID 重复：{case['id']}")
        seen_ids.add(case["id"])

    return data


def run_evaluation(cases_path: Path, output_path: Path | None = None) -> Path:
    cases = load_cases(cases_path)
    agent = Agent(
        model_client=ModelClient(),
        registry=create_registry(),
        max_steps=8,
        max_identical_calls=2,
    )
    results: list[dict[str, Any]] = []

    for case in cases:
        conversation = Conversation(SYSTEM_PROMPT)
        result = agent.run(case["input"], conversation)
        score = evaluate_result(result, case["expected"])
        item = {
            "case_id": case["id"],
            "category": case["category"],
            "input": case["input"],
            **asdict(result),
            **score,
            "trace": conversation.messages,
        }
        results.append(item)
        mark = "PASS" if score["passed"] else "FAIL"
        print(f"[{mark}] {case['id']}: {result.content}")

    report = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "cases_file": str(cases_path.resolve()),
        "summary": summarize(results),
        "results": results,
    }

    if output_path is None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = DEFAULT_RESULTS_DIR / f"eval-{stamp}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = report["summary"]
    print(
        f"\n评测完成：{summary['passed']}/{summary['total']} 通过 "
        f"({summary['pass_rate']:.1%})"
    )
    print(f"报告：{output_path.resolve()}")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行 Mini Agent 最小评测集")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_evaluation(args.cases, args.output)


if __name__ == "__main__":
    main()
