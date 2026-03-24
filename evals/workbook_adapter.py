from __future__ import annotations

from pathlib import Path
from typing import Any

from eval_framework.adapters import EvalAdapter

from app.model import analyze_workbook


class WorkbookAnalyzerAdapter(EvalAdapter):
    name = "workbook-analyzer"
    framework = "python"

    def __init__(self, project_root: str | Path | None = None):
        self.project_root = Path(project_root or Path(__file__).resolve().parents[1])

    def predict(self, sample_input: dict[str, Any]) -> dict[str, Any]:
        relative_path = sample_input["path"]
        filename = sample_input.get("filename") or Path(relative_path).name
        file_path = (self.project_root / relative_path).resolve()
        file_bytes = file_path.read_bytes()
        return analyze_workbook(file_bytes, filename)
