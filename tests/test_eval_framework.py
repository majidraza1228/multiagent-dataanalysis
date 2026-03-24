import time

from eval_framework.datasets import load_jsonl_dataset
from eval_framework.judges import RubricJudge
from eval_framework.runner import run_eval
from eval_framework.types import EvalInvocationResult
from evals.api_adapter import FastAPIWorkbookAdapter
from evals.workbook_adapter import WorkbookAnalyzerAdapter
from eval_framework.adapters import EvalAdapter


def test_workbook_eval_dataset_passes():
    cases = load_jsonl_dataset("evals/cases/workbook_cases.jsonl")
    result = run_eval(WorkbookAnalyzerAdapter(), cases)

    assert result.total_cases == 3
    assert result.failed_cases == 0
    assert result.pass_rate == 1.0


def test_fastapi_eval_dataset_passes():
    cases = load_jsonl_dataset("evals/cases/workbook_cases.jsonl")
    result = run_eval(FastAPIWorkbookAdapter(), cases)

    assert result.total_cases == 3
    assert result.failed_cases == 0
    assert result.pass_rate == 1.0


class SlowMetadataAdapter(EvalAdapter):
    name = "slow-metadata"
    framework = "test"

    def invoke(self, sample_input: dict) -> EvalInvocationResult:
        time.sleep(0.01)
        return EvalInvocationResult(
            output={"label": sample_input["label"], "text": "numeric summary looks good"},
            metadata={"cost_usd": sample_input.get("cost_usd", 0.0)},
        )

    def predict(self, sample_input: dict) -> dict:
        raise NotImplementedError


def test_parallel_runner_and_cost_tracking():
    adapter = SlowMetadataAdapter()
    cases = [
        type("Case", (), {"id": "a", "sample_input": {"label": "ok", "cost_usd": 0.1}, "assertions": [{"path": "label", "op": "eq", "value": "ok"}], "tags": []})(),
        type("Case", (), {"id": "b", "sample_input": {"label": "ok", "cost_usd": 0.2}, "assertions": [{"path": "label", "op": "eq", "value": "ok"}], "tags": []})(),
    ]

    result = run_eval(adapter, cases, workers=2)

    assert result.failed_cases == 0
    assert result.total_cost_usd == 0.3
    assert result.average_cost_usd == 0.15


def test_rubric_judge_assertion():
    adapter = SlowMetadataAdapter()
    cases = [
        type(
            "Case",
            (),
            {
                "id": "judge",
                "sample_input": {"label": "ok"},
                "assertions": [
                    {
                        "path": "text",
                        "op": "rubric_judge",
                        "judge": "rubric",
                        "value": ["numeric", "summary"],
                        "threshold": 2,
                    }
                ],
                "tags": [],
            },
        )(),
    ]

    result = run_eval(adapter, cases, judges={"rubric": RubricJudge()})

    assert result.failed_cases == 0
