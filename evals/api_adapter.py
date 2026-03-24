from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from eval_framework.adapters import EvalAdapter
from eval_framework.types import EvalInvocationResult
from main import app


@lru_cache(maxsize=64)
def _read_file_bytes(file_path: str) -> bytes:
    return Path(file_path).read_bytes()


class FastAPIWorkbookAdapter(EvalAdapter):
    name = "fastapi-api"
    framework = "fastapi"

    def __init__(self, project_root: str | Path | None = None):
        self.project_root = Path(project_root or Path(__file__).resolve().parents[1])
        self.client = TestClient(app)

    def predict(self, sample_input: dict[str, Any]) -> dict[str, Any]:
        relative_path = sample_input["path"]
        file_path = (self.project_root / relative_path).resolve()
        filename = sample_input.get("filename") or file_path.name
        response = self.client.post(
            "/api/analyze",
            files={"file": (filename, _read_file_bytes(str(file_path)), "application/octet-stream")},
        )
        response.raise_for_status()
        return response.json()

    def invoke(self, sample_input: dict[str, Any]) -> EvalInvocationResult:
        relative_path = sample_input["path"]
        file_path = (self.project_root / relative_path).resolve()
        filename = sample_input.get("filename") or file_path.name
        file_bytes = _read_file_bytes(str(file_path))
        response = self.client.post(
            "/api/analyze",
            files={"file": (filename, file_bytes, "application/octet-stream")},
        )
        response.raise_for_status()
        return EvalInvocationResult(
            output=response.json(),
            metadata={
                "cost_usd": sample_input.get("estimated_cost_usd", 0.0),
                "input_bytes": len(file_bytes),
                "estimated_input_tokens": len(file_bytes) // 4,
            },
        )
