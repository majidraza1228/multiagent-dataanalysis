from __future__ import annotations

import time
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
    cases: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_eval(adapter: EvalAdapter, cases: list[EvalCase]) -> EvalRunResult:
    case_results: list[dict[str, Any]] = []
    passed_cases = 0
    total_assertions = 0
    passed_assertions = 0

    for case in cases:
        started_at = time.perf_counter()
        prediction = adapter.predict(case.sample_input)
        latency_ms = round((time.perf_counter() - started_at) * 1000, 4)
        assertion_results = [evaluate_assertion(prediction, assertion) for assertion in case.assertions]
        case_passed = all(result["passed"] for result in assertion_results)

        total_assertions += len(assertion_results)
        passed_assertions += sum(1 for result in assertion_results if result["passed"])
        passed_cases += int(case_passed)

        case_results.append(
            {
                "id": case.id,
                "tags": case.tags,
                "passed": case_passed,
                "latency_ms": latency_ms,
                "assertions": assertion_results,
                "prediction": prediction,
            }
        )

    total_cases = len(cases)
    failed_cases = total_cases - passed_cases
    pass_rate = round(passed_cases / total_cases, 4) if total_cases else 0.0
    assertion_pass_rate = round(passed_assertions / total_assertions, 4) if total_assertions else 0.0
    total_latency_ms = round(sum(case["latency_ms"] for case in case_results), 4)
    average_latency_ms = round(total_latency_ms / total_cases, 4) if total_cases else 0.0

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
        cases=case_results,
    )
