from abc import ABC, abstractmethod
from typing import Any

from eval_framework.types import EvalInvocationResult


class EvalAdapter(ABC):
    """Project-specific adapter that normalizes a system under test."""

    name: str = "unnamed-adapter"
    framework: str = "custom"

    @abstractmethod
    def predict(self, sample_input: dict[str, Any]) -> dict[str, Any]:
        """Return a normalized prediction payload for one eval case."""

    def invoke(self, sample_input: dict[str, Any]) -> EvalInvocationResult:
        """Return output plus optional metadata such as tokens or estimated cost."""
        return EvalInvocationResult(output=self.predict(sample_input))
