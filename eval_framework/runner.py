from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from typing import Any

from eval_framework.adapters import EvalAdapter
from eval_framework.datasets import EvalCase
from eval_framework.metrics import evaluate_assertion


@dataclass
class EvalRunResult:
    adapter_name: str
    framework: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    total_assertions: int
    passed_assertions: int
    assertion_pass_rate: float
    total_latency_ms: float
    average_latency_ms: float
    total_cost_usd: float
    average_cost_usd: float
    cases: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _evaluate_case(case: EvalCase, adapter: EvalAdapter, judges: dict[str, Any] | None = None) -> dict[str, Any]:
        started_at = time.perf_counter()
        invocation = adapter.invoke(case.sample_input)
        latency_ms = round((time.perf_counter() - started_at) * 1000, 4)
        prediction = invocation.output
        metadata = invocation.metadata
        assertion_results = [
            evaluate_assertion(prediction, assertion, judges=judges) for assertion in case.assertions
        ]
        case_passed = all(result["passed"] for result in assertion_results)
        return {
            "id": case.id,
            "tags": case.tags,
            "passed": case_passed,
            "latency_ms": latency_ms,
            "cost_usd": round(float(metadata.get("cost_usd", 0.0)), 8),
            "metadata": metadata,
            "assertions": assertion_results,
            "prediction": prediction,
        }


def run_eval(
    adapter: EvalAdapter,
    cases: list[EvalCase],
    *,
    workers: int = 1,
    judges: dict[str, Any] | None = None,
) -> EvalRunResult:
    case_results: list[dict[str, Any]] = []
    passed_cases = 0
    total_assertions = 0
    passed_assertions = 0

    if workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            case_results = list(executor.map(lambda case: _evaluate_case(case, adapter, judges), cases))
    else:
        case_results = [_evaluate_case(case, adapter, judges) for case in cases]

    for case_result in case_results:
        total_assertions += len(case_result["assertions"])
        passed_assertions += sum(1 for result in case_result["assertions"] if result["passed"])
        passed_cases += int(case_result["passed"])

    total_cases = len(cases)
    failed_cases = total_cases - passed_cases
    pass_rate = round(passed_cases / total_cases, 4) if total_cases else 0.0
    assertion_pass_rate = round(passed_assertions / total_assertions, 4) if total_assertions else 0.0
    total_latency_ms = round(sum(case["latency_ms"] for case in case_results), 4)
    average_latency_ms = round(total_latency_ms / total_cases, 4) if total_cases else 0.0
    total_cost_usd = round(sum(case.get("cost_usd", 0.0) for case in case_results), 8)
    average_cost_usd = round(total_cost_usd / total_cases, 8) if total_cases else 0.0

    return EvalRunResult(
        adapter_name=adapter.name,
        framework=adapter.framework,
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        pass_rate=pass_rate,
        total_assertions=total_assertions,
        passed_assertions=passed_assertions,
        assertion_pass_rate=assertion_pass_rate,
        total_latency_ms=total_latency_ms,
        average_latency_ms=average_latency_ms,
        total_cost_usd=total_cost_usd,
        average_cost_usd=average_cost_usd,
        cases=case_results,
    )
