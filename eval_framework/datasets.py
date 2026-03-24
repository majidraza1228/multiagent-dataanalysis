from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class EvalCase:
    id: str
    sample_input: dict[str, Any]
    assertions: list[dict[str, Any]]
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def load_jsonl_dataset(path: str | Path) -> list[EvalCase]:
    dataset_path = Path(path)
    cases: list[EvalCase] = []
    for line_number, raw_line in enumerate(dataset_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        payload = json.loads(line)
        cases.append(
            EvalCase(
                id=payload["id"],
                sample_input=payload.get("input", {}),
                assertions=payload.get("assertions", []),
                tags=payload.get("tags", []),
                metadata=payload.get("metadata", {"line_number": line_number}),
            )
        )
    return cases
