from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvalInvocationResult:
    output: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

