from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from eval_framework.adapters import EvalAdapter
from main import app


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
            files={"file": (filename, file_path.read_bytes(), "application/octet-stream")},
        )
        response.raise_for_status()
        return response.json()
