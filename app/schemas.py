from typing import Any

from pydantic import BaseModel


class WorkbookSummary(BaseModel):
    total_rows: int
    total_columns: int
    missing_cells: int
    numeric_column_count: int


class SheetSummary(BaseModel):
    sheet_name: str
    row_count: int
    column_count: int
    missing_cells: int
    duplicate_rows: int
    numeric_columns: list[str]
    text_columns: list[str]
    column_names: list[str]
    numeric_summary: dict[str, dict[str, float]]
    preview_rows: list[dict[str, Any]]


class AnalyzeResponse(BaseModel):
    workbook_name: str
    sheet_count: int
    dataset_type: str
    confidence: float
    summary: WorkbookSummary
    issues: list[str]
    sheet_summaries: list[SheetSummary]
    recommendations: list[str]


class HealthResponse(BaseModel):
    status: str
    model_version: str
    uptime: float
