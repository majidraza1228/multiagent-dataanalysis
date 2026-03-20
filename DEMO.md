# Demo Guide

This project should be demoed with `3` terminals by default. Use `4` terminals if you also want to show MLflow.

## Recommended 3-Terminal Demo

### Terminal 1: FastAPI backend

```bash
cd /Users/syedraza/multiagent-dataanalysis
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Gradio UI

```bash
cd /Users/syedraza/multiagent-dataanalysis
python ui/app.py
```

Open these in the browser:

- Gradio UI: `http://localhost:7860`
- FastAPI docs: `http://localhost:8000/docs`

### Terminal 3: Monitoring dashboard

```bash
cd /Users/syedraza/multiagent-dataanalysis
python monitor_dashboard.py
```

Use this terminal during the demo to show that every workbook analysis is logged and checked for drift in real time.

## Recommended 4-Terminal Demo

If you want to show the analysis pipeline and experiment tracking as well, add MLflow.

### Terminal 3: MLflow server

```bash
cd /Users/syedraza/multiagent-dataanalysis
mlflow server --host 0.0.0.0 --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns
```

### Terminal 4: Run profiling scripts

```bash
cd /Users/syedraza/multiagent-dataanalysis
python model/train.py
python compare_runs.py
```

Open MLflow here:

- MLflow UI: `http://localhost:5000`

### Terminal 4: Monitoring dashboard

```bash
cd /Users/syedraza/multiagent-dataanalysis
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

## Suggested Demo Files

Prepare `2` or `3` files before presenting:

- `sales.csv` with columns like `date,revenue,region`
- `finance.xlsx` with multiple sheets
- one intentionally messy file with missing values or duplicates

## Terminal Recommendation

- Use `3` terminals for the main demo: backend, UI, monitoring.
- Use `4` terminals for the fuller engineering demo: backend, UI, MLflow, monitoring.
- Use `2` terminals only if you need a shortened backup version.
