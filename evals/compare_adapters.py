import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from eval_framework.datasets import load_jsonl_dataset
from eval_framework.reporter import (
    log_comparison_to_mlflow,
    write_html_comparison_report,
    write_json_report,
)
from eval_framework.runner import run_eval
from evals.registry import build_registry


DEFAULT_DATASET = Path("evals/cases/workbook_cases.jsonl")
DEFAULT_SUMMARY_REPORT = Path("evals/reports/comparison.json")
DEFAULT_HTML_REPORT = Path("evals/reports/comparison.html")
DEFAULT_EXPERIMENT = "excel-sheet-analysis-evals"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare multiple eval adapters on the same dataset.")
    parser.add_argument(
        "--adapters",
        default="workbook-analyzer,fastapi-api",
        help="Comma-separated adapter names to compare.",
    )
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET), help="Path to the eval dataset JSONL file.")
    parser.add_argument("--report", default=str(DEFAULT_SUMMARY_REPORT), help="Path to write the summary JSON.")
    parser.add_argument("--html-report", default=str(DEFAULT_HTML_REPORT), help="Path to write the HTML report.")
    parser.add_argument(
        "--log-mlflow",
        action="store_true",
        help="Log comparison metrics and report artifacts to MLflow.",
    )
    parser.add_argument(
        "--experiment",
        default=DEFAULT_EXPERIMENT,
        help="MLflow experiment name used when --log-mlflow is enabled.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    registry = build_registry()
    requested_adapters = [name.strip() for name in args.adapters.split(",") if name.strip()]
    cases = load_jsonl_dataset(args.dataset)

    run_results = []
    report_paths: list[Path] = []
    for name in requested_adapters:
        adapter = registry.create(name)
        result = run_eval(adapter, cases)
        result_payload = result.to_dict()
        run_results.append(result_payload)
        adapter_report_path = Path(args.report).with_name(f"{name}.json")
        write_json_report(adapter_report_path, result_payload)
        report_paths.append(adapter_report_path)

        print(
            f"{result.adapter_name}: "
            f"cases {result.passed_cases}/{result.total_cases} "
            f"({result.pass_rate:.2%}), avg latency {result.average_latency_ms:.2f} ms"
        )

    payload = {
        "run_name": "eval-comparison",
        "dataset": args.dataset,
        "runs": run_results,
    }
    summary_report_path = write_json_report(args.report, payload)
    html_report_path = write_html_comparison_report(args.html_report, payload)
    report_paths.extend([summary_report_path, html_report_path])

    print(f"Summary report: {summary_report_path}")
    print(f"HTML report: {html_report_path}")

    if args.log_mlflow:
        run_id = log_comparison_to_mlflow(payload, report_paths, args.experiment)
        print(f"MLflow run: {run_id}")

    return 0 if all(item["failed_cases"] == 0 for item in run_results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
