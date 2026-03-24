from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any


def write_json_report(path: str | Path, payload: dict[str, Any]) -> Path:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return report_path


def write_html_comparison_report(path: str | Path, payload: dict[str, Any]) -> Path:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    for run in payload.get("runs", []):
        summary_rows.append(
            "<tr>"
            f"<td>{html.escape(run['adapter_name'])}</td>"
            f"<td>{html.escape(run.get('framework', 'custom'))}</td>"
            f"<td>{run['passed_cases']}/{run['total_cases']}</td>"
            f"<td>{run['pass_rate']:.2%}</td>"
            f"<td>{run['passed_assertions']}/{run['total_assertions']}</td>"
            f"<td>{run['assertion_pass_rate']:.2%}</td>"
            f"<td>{run.get('average_latency_ms', 0.0):.2f}</td>"
            f"<td>${run.get('total_cost_usd', 0.0):.4f}</td>"
            "</tr>"
        )

    failure_sections = []
    for run in payload.get("runs", []):
        failures = [case for case in run.get("cases", []) if not case.get("passed")]
        if not failures:
            failure_sections.append(
                f"<section><h3>{html.escape(run['adapter_name'])}</h3><p>No failing cases.</p></section>"
            )
            continue

        items = []
        for case in failures:
            failed_assertions = [item for item in case["assertions"] if not item["passed"]]
            assertion_rows = "".join(
                "<li>"
                f"{html.escape(item['path'])} {html.escape(item['op'])} "
                f"{html.escape(str(item.get('expected')))} | actual={html.escape(str(item.get('actual')))}"
                "</li>"
                for item in failed_assertions
            )
            items.append(
                "<details>"
                f"<summary>{html.escape(case['id'])} ({case.get('latency_ms', 0.0):.2f} ms)</summary>"
                f"<ul>{assertion_rows}</ul>"
                "</details>"
            )
        failure_sections.append(
            f"<section><h3>{html.escape(run['adapter_name'])}</h3>{''.join(items)}</section>"
        )

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Eval Comparison Report</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f1e8;
      --panel: #fffaf0;
      --ink: #1d1b18;
      --muted: #6f665b;
      --line: #d2c7b8;
      --accent: #0f766e;
      --accent-2: #92400e;
    }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      background:
        radial-gradient(circle at top left, rgba(15, 118, 110, 0.10), transparent 30%),
        radial-gradient(circle at top right, rgba(146, 64, 14, 0.10), transparent 30%),
        var(--bg);
      color: var(--ink);
    }}
    main {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 32px 20px 64px;
    }}
    h1, h2, h3 {{
      margin-bottom: 8px;
    }}
    p {{
      color: var(--muted);
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 20px;
      margin-top: 20px;
      box-shadow: 0 12px 30px rgba(29, 27, 24, 0.06);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
    }}
    th, td {{
      text-align: left;
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
    }}
    th {{
      color: var(--accent);
      font-size: 0.92rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    summary {{
      cursor: pointer;
      font-weight: 600;
      color: var(--accent-2);
    }}
    details {{
      margin: 10px 0;
      padding: 10px 12px;
      background: rgba(255, 255, 255, 0.65);
      border-radius: 10px;
      border: 1px solid var(--line);
    }}
  </style>
</head>
<body>
  <main>
    <h1>Eval Comparison Report</h1>
    <p>Dataset: {html.escape(str(payload.get('dataset', 'unknown')))}</p>
    <div class="card">
      <h2>Run Summary</h2>
      <table>
        <thead>
          <tr>
            <th>Adapter</th>
            <th>Framework</th>
            <th>Cases</th>
            <th>Case Pass Rate</th>
            <th>Assertions</th>
            <th>Assertion Pass Rate</th>
            <th>Avg Latency ms</th>
            <th>Total Cost USD</th>
          </tr>
        </thead>
        <tbody>
          {''.join(summary_rows)}
        </tbody>
      </table>
    </div>
    <div class="card">
      <h2>Failing Cases</h2>
      {''.join(failure_sections)}
    </div>
  </main>
</body>
</html>
"""
    report_path.write_text(document, encoding="utf-8")
    return report_path


def log_run_to_mlflow(result: dict[str, Any], report_paths: list[str | Path], experiment_name: str) -> str:
    try:
        import mlflow
    except ImportError as exc:
        raise RuntimeError("mlflow is not installed in the current interpreter") from exc

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name=result["adapter_name"]) as run:
        mlflow.log_params(
            {
                "adapter_name": result["adapter_name"],
                "framework": result.get("framework", "custom"),
                "total_cases": result["total_cases"],
                "total_assertions": result["total_assertions"],
            }
        )
        mlflow.log_metrics(
            {
                "pass_rate": result["pass_rate"],
                "assertion_pass_rate": result["assertion_pass_rate"],
                "average_latency_ms": result.get("average_latency_ms", 0.0),
                "failed_cases": result["failed_cases"],
                "total_cost_usd": result.get("total_cost_usd", 0.0),
            }
        )
        for report_path in report_paths:
            if Path(report_path).exists():
                mlflow.log_artifact(str(report_path), artifact_path="eval_reports")
        return run.info.run_id


def log_comparison_to_mlflow(payload: dict[str, Any], report_paths: list[str | Path], experiment_name: str) -> str:
    try:
        import mlflow
    except ImportError as exc:
        raise RuntimeError("mlflow is not installed in the current interpreter") from exc

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name=payload.get("run_name", "eval-comparison")) as run:
        mlflow.log_param("dataset", payload.get("dataset", "unknown"))
        mlflow.log_param("adapter_count", len(payload.get("runs", [])))
        for index, item in enumerate(payload.get("runs", []), start=1):
            prefix = f"adapter_{index}"
            mlflow.log_param(f"{prefix}_name", item["adapter_name"])
            mlflow.log_param(f"{prefix}_framework", item.get("framework", "custom"))
            mlflow.log_metric(f"{prefix}_pass_rate", item["pass_rate"])
            mlflow.log_metric(f"{prefix}_assertion_pass_rate", item["assertion_pass_rate"])
            mlflow.log_metric(f"{prefix}_average_latency_ms", item.get("average_latency_ms", 0.0))
            mlflow.log_metric(f"{prefix}_total_cost_usd", item.get("total_cost_usd", 0.0))
        for report_path in report_paths:
            if Path(report_path).exists():
                mlflow.log_artifact(str(report_path), artifact_path="eval_reports")
        return run.info.run_id
