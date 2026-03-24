from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from eval_framework.adapters import EvalAdapter
from eval_framework.types import EvalInvocationResult

from app.model import analyze_workbook


@lru_cache(maxsize=64)
def _read_file_bytes(file_path: str) -> bytes:
    return Path(file_path).read_bytes()


class WorkbookAnalyzerAdapter(EvalAdapter):
    name = "workbook-analyzer"
    framework = "python"

    def __init__(self, project_root: str | Path | None = None):
        self.project_root = Path(project_root or Path(__file__).resolve().parents[1])

    def predict(self, sample_input: dict[str, Any]) -> dict[str, Any]:
        relative_path = sample_input["path"]
        filename = sample_input.get("filename") or Path(relative_path).name
        file_path = (self.project_root / relative_path).resolve()
        file_bytes = _read_file_bytes(str(file_path))
        return analyze_workbook(file_bytes, filename)

    def invoke(self, sample_input: dict[str, Any]) -> EvalInvocationResult:
        relative_path = sample_input["path"]
        filename = sample_input.get("filename") or Path(relative_path).name
        file_path = (self.project_root / relative_path).resolve()
        file_bytes = _read_file_bytes(str(file_path))
        output = analyze_workbook(file_bytes, filename)
        estimated_tokens = len(file_bytes) // 4
        return EvalInvocationResult(
            output=output,
            metadata={
                "cost_usd": sample_input.get("estimated_cost_usd", 0.0),
                "input_bytes": len(file_bytes),
                "estimated_input_tokens": estimated_tokens,
            },
        )
