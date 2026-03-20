# multiagent-dataanalysis

An end-to-end Excel and CSV analysis system built with FastAPI, Gradio, pandas, and MLflow, assembled by a Codex agent team working in parallel.

## Agent Team Architecture

```mermaid
flowchart TD
    User(["User Prompt"])
    Orch["Orchestrator\nCodex"]
    Skills[".codex/skills/\nProject Playbooks"]
    Session[".agent_memory/\nsession.json"]
    Grader["grader.py\n0–10 scorer"]

    User --> Orch
    Orch --> Skills

    Skills -->|pytorch-model\nmlflow-tracking| A1
    Skills -->|fastapi-backend\ngradio-frontend| A2
    Skills -->|jsonl-monitor\nproject-scaffold| A3

    subgraph Parallel ["Parallel Execution"]
        A1["Agent 1 — Analysis Pipeline\nCodex High Profile\n─────────────────\napp/model.py\nmodel/train.py\nmodel/register_model.py\ncompare_runs.py"]
        A2["Agent 2 — Deployment\nCodex Fast Profile\n─────────────────\nmain.py\napp/routers.py\napp/schemas.py\nui/app.py\ntests/test_api.py"]
        A3["Agent 3 — Reliability\nCodex Fast Profile\n─────────────────\napp/middleware.py\napp/drift_checker.py\nmonitor_dashboard.py\ngrader.py"]
    end

    A1 -->|Workbook heuristics\nMLflow artifacts| Merge
    A2 -->|FastAPI app\nGradio UI| Merge
    A3 -->|JSONL logger\ndrift alerts| Merge

    Merge["Orchestrator Merges\nWires middleware into main.py"]
    Merge --> Grader
    Grader --> Done(["Build Complete"])
    Merge --> Session
    Done --> Session
```

## What the Project Does

The API accepts `.xlsx`, `.xls`, and `.csv` files and returns workbook-level analysis:

- sheet counts and dataset type inference
- row, column, missing-cell, and duplicate summaries per sheet
- numeric-column summaries and sample row previews
- confidence scoring plus recommendations for cleanup or reporting

The UI provides an upload flow for workbook inspection, while the monitoring layer logs every analysis to `logs/predictions.jsonl` and raises drift alerts when average confidence drops.

## Multi-Agent Structure

The project keeps the same three-part multi-agent layout:

- Analysis pipeline agent: workbook parsing, heuristics, MLflow artifact generation, run comparison
- Deployment agent: FastAPI `/api/analyze` and `/api/health`, schemas, Gradio interface, API tests
- Reliability agent: analysis logging middleware, drift checks, CLI dashboard, grader and rerun logic

This preserves the original orchestration style while removing the old image-analysis domain.

## Project Structure

```text
multiagent-dataanalysis/
├── app/
│   ├── model.py               # Workbook analysis engine
│   ├── routers.py             # /analyze and /health endpoints
│   ├── schemas.py             # Pydantic response models
│   ├── middleware.py          # JSONL analysis logger
│   └── drift_checker.py       # Confidence-based drift detection
├── model/
│   ├── cnn.py                 # Workbook profiling placeholder model
│   ├── train.py               # Batch workbook profiling + MLflow logging
│   └── register_model.py      # Registers workbook profile artifact to MLflow
├── ui/
│   └── app.py                 # Gradio workbook analysis UI
├── tests/
│   └── test_api.py            # API tests for analyze and health endpoints
├── main.py                    # FastAPI app entry point
├── monitor_dashboard.py       # CLI monitoring dashboard
├── compare_runs.py            # MLflow run comparison table
├── grader.py                  # 0-10 project scorer
├── requirements.txt
└── .agent_memory/
```

## Running the Project

```bash
make install
make serve
make ui
make monitor
make test
make grade
```

Optional MLflow flow:

```bash
mlflow server --host 0.0.0.0 --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns

make train
python model/register_model.py
python compare_runs.py
```

## Technology Stack

| Component | Technology |
|---|---|
| Backend API | FastAPI |
| Workbook parsing | pandas + openpyxl |
| Frontend | Gradio |
| Monitoring | JSONL + tabulate |
| Experiment tracking | MLflow |
| Testing | pytest |
