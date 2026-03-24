from eval_framework.datasets import load_jsonl_dataset
from eval_framework.runner import run_eval
from evals.api_adapter import FastAPIWorkbookAdapter
from evals.workbook_adapter import WorkbookAnalyzerAdapter


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
