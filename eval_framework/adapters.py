from abc import ABC, abstractmethod
from typing import Any


class EvalAdapter(ABC):
    """Project-specific adapter that normalizes a system under test."""

    name: str = "unnamed-adapter"
    framework: str = "custom"

    @abstractmethod
    def predict(self, sample_input: dict[str, Any]) -> dict[str, Any]:
        """Return a normalized prediction payload for one eval case."""
