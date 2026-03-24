import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from eval_framework.datasets import load_jsonl_dataset
from eval_framework.reporter import log_run_to_mlflow, write_json_report
from eval_framework.runner import run_eval
from evals.registry import build_registry


DEFAULT_DATASET = Path("evals/cases/workbook_cases.jsonl")
DEFAULT_REPORT = Path("evals/reports/latest.json")
DEFAULT_EXPERIMENT = "excel-sheet-analysis-evals"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run reusable evals against the workbook analyzer.")
    parser.add_argument(
        "--adapter",
        default="workbook-analyzer",
        help="Adapter name to run. Supported: workbook-analyzer, fastapi-api.",
    )
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET), help="Path to the eval dataset JSONL file.")
    parser.add_argument("--report", default=str(DEFAULT_REPORT), help="Path to write the eval report JSON.")
    parser.add_argument(
        "--log-mlflow",
        action="store_true",
        help="Log the eval result and report artifact to MLflow.",
    )
    parser.add_argument(
        "--experiment",
        default=DEFAULT_EXPERIMENT,
        help="MLflow experiment name used when --log-mlflow is enabled.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    cases = load_jsonl_dataset(args.dataset)
    registry = build_registry()
    adapter = registry.create(args.adapter)
    result = run_eval(adapter, cases)
    report_path = write_json_report(args.report, result.to_dict())

    print(f"Adapter: {result.adapter_name}")
    print(f"Framework: {result.framework}")
    print(f"Cases: {result.passed_cases}/{result.total_cases} passed ({result.pass_rate:.2%})")
    print(
        f"Assertions: {result.passed_assertions}/{result.total_assertions} passed "
        f"({result.assertion_pass_rate:.2%})"
    )
    print(f"Average latency: {result.average_latency_ms:.2f} ms")
    print(f"Report: {report_path}")
    if args.log_mlflow:
        run_id = log_run_to_mlflow(result.to_dict(), [report_path], args.experiment)
        print(f"MLflow run: {run_id}")
    return 0 if result.failed_cases == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
