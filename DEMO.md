# Demo Guide

This project should be demoed with `3` terminals by default. Use `4` terminals if you also want to show MLflow.

## Local Environment Setup

Use Python `3.11` and a local virtual environment before starting the demo.

```bash
cd /Users/syedraza/multiagent-dataanalysis
python3.11 -m venv .venv
source .venv/bin/activate
python --version
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Every new terminal used for the demo should activate the same environment first:

```bash
cd /Users/syedraza/multiagent-dataanalysis
source .venv/bin/activate
```

## Recommended 3-Terminal Demo

### Terminal 1: FastAPI backend

```bash
cd /Users/syedraza/multiagent-dataanalysis
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Gradio UI

```bash
cd /Users/syedraza/multiagent-dataanalysis
source .venv/bin/activate
python ui/app.py
```

Open these in the browser:

- Gradio UI: `http://localhost:7860`
- FastAPI docs: `http://localhost:8000/docs`

### Terminal 3: Monitoring dashboard

```bash
cd /Users/syedraza/multiagent-dataanalysis
source .venv/bin/activate
python monitor_dashboard.py
```

Use this terminal during the demo to show that every workbook analysis is logged and checked for drift in real time.

## Recommended 4-Terminal Demo

If you want to show the analysis pipeline and experiment tracking as well, add MLflow.

### Terminal 3: MLflow server

```bash
cd /Users/syedraza/multiagent-dataanalysis
source .venv/bin/activate
mlflow server --host 0.0.0.0 --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns
```

If port `5000` is already in use, run MLflow on `5001` instead:

```bash
cd /Users/syedraza/multiagent-dataanalysis
source .venv/bin/activate
export MLFLOW_TRACKING_URI=http://localhost:5001
mlflow server --host 0.0.0.0 --port 5001 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns
```

### Terminal 4: Run profiling scripts

```bash
cd /Users/syedraza/multiagent-dataanalysis
source .venv/bin/activate
export MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI:-http://localhost:5000}
python model/train.py
python compare_runs.py
```

Open MLflow here:

- MLflow UI: `http://localhost:5000`

### Terminal 4: Monitoring dashboard

```bash
cd /Users/syedraza/multiagent-dataanalysis
source .venv/bin/activate
python monitor_dashboard.py
```

## Best Demo Flow

1. Start in the Gradio UI.
2. Upload a `.csv`, `.xlsx`, or `.xls` file.
3. Show workbook overview, detected issues, and recommendations.
4. Show the sheet summary table.
5. Move to FastAPI docs and repeat the same upload via `POST /api/analyze`.
6. Show the monitoring dashboard output in the third terminal.
7. If using 4 terminals, show MLflow runs and profiling artifacts.

## What To Highlight

- The app accepts spreadsheet files instead of images.
- The API returns workbook structure, confidence, issues, and recommendations.
- The Gradio UI is a lightweight analyst-facing interface.
- The monitoring layer logs every analysis to JSONL.
- The project keeps a Codex-style multi-agent structure even though the domain is now spreadsheet analysis.

## How To Explain MLflow

### 30-second business script

"MLflow is the tracking layer for this workflow. It keeps a record of each analysis run, the quality metrics that were produced, and the generated artifacts. From a business perspective, that gives us better traceability, repeatability, and visibility into how the workflow performs over time instead of relying on one-off scripts."

### 30-second engineering script

"MLflow is being used here as the experiment tracking and artifact storage layer for workbook profiling runs. The pipeline logs quality metrics, saves generated artifacts, and lets us compare runs across different input datasets. That gives us reproducibility and a structured way to evaluate changes in the analysis workflow."

## Suggested Demo Files

Use these sample CSV files from the `samples/` folder:

- `samples/sales.csv` for a clean workbook-style demo
- `samples/messy_sales.csv` to show missing values and duplicates
- `samples/operations_report.csv` to show a different business dataset

If needed, convert these CSV files into `.xlsx` files before the demo and upload those instead.

## Terminal Recommendation

- Use `3` terminals for the main demo: backend, UI, monitoring.
- Use `4` terminals for the fuller engineering demo: backend, UI, MLflow, monitoring.
- Use `2` terminals only if you need a shortened backup version.
