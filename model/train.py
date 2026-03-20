import json
import os
from pathlib import Path

import mlflow
import pandas as pd

DATA_DIR = Path("data")
PROFILE_PATH = Path("checkpoints/model.pt")
SUPPORTED_SUFFIXES = {".csv", ".xlsx", ".xls"}
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")


def load_frame(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    return pd.read_excel(path)


def summarize_frame(path: Path) -> dict:
    frame = load_frame(path)
    numeric_columns = frame.select_dtypes(include="number").columns.tolist()
    return {
        "file": path.name,
        "rows": int(frame.shape[0]),
        "columns": int(frame.shape[1]),
        "missing_cells": int(frame.isna().sum().sum()),
        "duplicate_rows": int(frame.duplicated().sum()) if not frame.empty else 0,
        "numeric_columns": numeric_columns,
        "quality_score": round(compute_quality_score(frame), 4),
    }


def compute_quality_score(frame: pd.DataFrame) -> float:
    if frame.empty or frame.shape[1] == 0:
        return 0.1
    total_cells = max(frame.shape[0] * frame.shape[1], 1)
    missing_ratio = frame.isna().sum().sum() / total_cells
    duplicate_ratio = frame.duplicated().sum() / max(frame.shape[0], 1)
    score = 0.95 - (missing_ratio * 0.5) - (duplicate_ratio * 0.2)
    return max(0.1, min(score, 0.99))


def main():
    DATA_DIR.mkdir(exist_ok=True)
    PROFILE_PATH.parent.mkdir(exist_ok=True)

    files = [path for path in DATA_DIR.iterdir() if path.suffix.lower() in SUPPORTED_SUFFIXES]
    if not files:
        print("No workbook files found in data/. Add .csv, .xlsx, or .xls files before training.")
        return

    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment("excel-sheet-analysis")

    summaries = []
    with mlflow.start_run(run_name="workbook-profile-baseline") as run:
        for path in files:
            summary = summarize_frame(path)
            summaries.append(summary)
            mlflow.log_metric(f"quality_score_{path.stem}", summary["quality_score"])
            mlflow.log_metric(f"rows_{path.stem}", summary["rows"])
            mlflow.log_metric(f"columns_{path.stem}", summary["columns"])

        overall_quality = round(sum(item["quality_score"] for item in summaries) / len(summaries), 4)
        artifact = {
            "files_analyzed": len(summaries),
            "overall_quality": overall_quality,
            "profiles": summaries,
        }
        PROFILE_PATH.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
        mlflow.log_metric("overall_quality", overall_quality)
        mlflow.log_artifact(str(PROFILE_PATH), artifact_path="model")
        print(f"Profile artifact saved to {PROFILE_PATH}")
        print(f"Run ID: {run.info.run_id}")


if __name__ == "__main__":
    main()
