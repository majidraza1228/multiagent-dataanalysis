"""Reusable evaluation framework primitives."""

from eval_framework.adapters import EvalAdapter
from eval_framework.datasets import EvalCase, load_jsonl_dataset
from eval_framework.registry import AdapterRegistry
from eval_framework.runner import EvalRunResult, run_eval

__all__ = [
    "AdapterRegistry",
    "EvalAdapter",
    "EvalCase",
    "EvalRunResult",
    "load_jsonl_dataset",
    "run_eval",
]
