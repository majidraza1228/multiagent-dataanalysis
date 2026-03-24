from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Any

import pandas as pd

MODEL_VERSION = "2.0.0"
SUPPORTED_EXTENSIONS = {".xlsx", ".xls", ".csv"}


@dataclass
class WorkbookAnalyzer:
    version: str = MODEL_VERSION

    def analyze(self, file_bytes: bytes, filename: str) -> dict[str, Any]:
        sheets = load_workbook(file_bytes, filename)
        sheet_summaries = [summarize_sheet(name, frame) for name, frame in sheets.items()]

        total_rows = sum(item["row_count"] for item in sheet_summaries)
        total_columns = sum(item["column_count"] for item in sheet_summaries)
        total_missing = sum(item["missing_cells"] for item in sheet_summaries)
        numeric_columns = sum(len(item["numeric_columns"]) for item in sheet_summaries)
        empty_sheets = [item["sheet_name"] for item in sheet_summaries if item["row_count"] == 0]

        confidence = compute_confidence(total_rows, total_columns, total_missing)
        dataset_type = infer_dataset_type(sheet_summaries)

        issues = []
        if empty_sheets:
            issues.append(f"Empty sheets: {', '.join(empty_sheets)}")
        if total_missing:
            issues.append(f"Workbook contains {total_missing} missing cells")
        if numeric_columns == 0:
            issues.append("No numeric columns detected")

        recommendations = build_recommendations(sheet_summaries, issues)

        return {
            "workbook_name": filename,
            "sheet_count": len(sheet_summaries),
            "dataset_type": dataset_type,
            "confidence": confidence,
            "summary": {
                "total_rows": total_rows,
                "total_columns": total_columns,
                "missing_cells": total_missing,
                "numeric_column_count": numeric_columns,
            },
            "issues": issues,
            "sheet_summaries": sheet_summaries,
            "recommendations": recommendations,
        }


_analyzer: WorkbookAnalyzer | None = None


def get_model() -> WorkbookAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = WorkbookAnalyzer()
    return _analyzer


def analyze_workbook(file_bytes: bytes, filename: str) -> dict[str, Any]:
    return get_model().analyze(file_bytes, filename)


def load_workbook(file_bytes: bytes, filename: str) -> dict[str, pd.DataFrame]:
    lower = filename.lower()
    if lower.endswith(".csv"):
        return {"Sheet1": pd.read_csv(io.BytesIO(file_bytes))}

    workbook = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
    return {name: frame for name, frame in workbook.items()}


def summarize_sheet(sheet_name: str, frame: pd.DataFrame) -> dict[str, Any]:
    row_count, column_count = frame.shape
    missing_cells = int(frame.isna().sum().sum())
    duplicate_rows = int(frame.duplicated().sum()) if row_count else 0
    numeric_columns = frame.select_dtypes(include="number").columns.tolist()
    text_columns = frame.select_dtypes(include=["object", "string"]).columns.tolist()

    numeric_summary = {}
    for column in numeric_columns[:5]:
        series = frame[column].dropna()
        if series.empty:
            continue
        numeric_summary[column] = {
            "min": round(float(series.min()), 4),
            "max": round(float(series.max()), 4),
            "mean": round(float(series.mean()), 4),
        }

    preview_rows = frame.head(3).fillna("").to_dict(orient="records")

    return {
        "sheet_name": sheet_name,
        "row_count": int(row_count),
        "column_count": int(column_count),
        "missing_cells": missing_cells,
        "duplicate_rows": duplicate_rows,
        "numeric_columns": numeric_columns,
        "text_columns": text_columns,
        "column_names": frame.columns.astype(str).tolist(),
        "numeric_summary": numeric_summary,
        "preview_rows": preview_rows,
    }


def compute_confidence(total_rows: int, total_columns: int, total_missing: int) -> float:
    if total_rows == 0 or total_columns == 0:
        return 0.15
    completeness_penalty = min(total_missing / max(total_rows * total_columns, 1), 0.8)
    structure_bonus = min((total_rows / 2000) + (total_columns / 50), 0.35)
    confidence = 0.55 + structure_bonus - completeness_penalty
    return round(max(0.1, min(confidence, 0.99)), 4)


def infer_dataset_type(sheet_summaries: list[dict[str, Any]]) -> str:
    combined_columns = {column.lower() for sheet in sheet_summaries for column in sheet["column_names"]}
    if {"date", "revenue", "sales", "amount"} & combined_columns:
        return "financial"
    if {"employee", "department", "salary"} & combined_columns:
        return "hr"
    if {"sku", "inventory", "stock", "warehouse"} & combined_columns:
        return "inventory"
    if {"customer", "region", "order"} & combined_columns:
        return "operations"
    return "general_tabular"


def build_recommendations(sheet_summaries: list[dict[str, Any]], issues: list[str]) -> list[str]:
    recommendations: list[str] = []
    total_duplicates = sum(sheet["duplicate_rows"] for sheet in sheet_summaries)
    if total_duplicates:
        recommendations.append(f"Review {total_duplicates} duplicate rows before downstream reporting")
    if any(sheet["missing_cells"] for sheet in sheet_summaries):
        recommendations.append("Impute or remove missing values in critical columns")
    if any(len(sheet["numeric_columns"]) >= 2 for sheet in sheet_summaries):
        recommendations.append("Use the detected numeric columns to build pivot summaries and trend checks")
    if not recommendations and not issues:
        recommendations.append("Workbook structure looks clean enough for downstream BI or automation")
    return recommendations[:5]
