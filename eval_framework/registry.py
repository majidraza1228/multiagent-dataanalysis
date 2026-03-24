from __future__ import annotations

from typing import Callable

from eval_framework.adapters import EvalAdapter


class AdapterRegistry:
    """Maps adapter names to factory functions."""

    def __init__(self) -> None:
        self._factories: dict[str, Callable[[], EvalAdapter]] = {}

    def register(self, name: str, factory: Callable[[], EvalAdapter]) -> None:
        self._factories[name] = factory

    def create(self, name: str) -> EvalAdapter:
        if name not in self._factories:
            available = ", ".join(sorted(self._factories))
            raise KeyError(f"Unknown adapter '{name}'. Available adapters: {available}")
        return self._factories[name]()

    def names(self) -> list[str]:
        return sorted(self._factories)
