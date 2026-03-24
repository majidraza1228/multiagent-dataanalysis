from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol


class EvalJudge(Protocol):
    name: str

    def evaluate(self, *, prediction: dict[str, Any], assertion: dict[str, Any]) -> dict[str, Any]:
        ...


@dataclass
class RubricJudge:
    """Deterministic local judge for text-oriented assertions."""

    name: str = "rubric-judge"

    def evaluate(self, *, prediction: dict[str, Any], assertion: dict[str, Any]) -> dict[str, Any]:
        path = assertion["path"]
        actual = prediction.get(path) if "." not in path else None
        if actual is None:
            from eval_framework.metrics import resolve_path

            try:
                actual = resolve_path(prediction, path)
            except KeyError:
                return {
                    "path": path,
                    "op": assertion["op"],
                    "expected": assertion.get("value"),
                    "passed": False,
                    "actual": None,
                    "judge": self.name,
                    "reason": "missing_path",
                }

        keywords = assertion.get("value", [])
        if isinstance(actual, list):
            text = " ".join(str(item) for item in actual).lower()
        else:
            text = str(actual).lower()

        matched = [keyword for keyword in keywords if str(keyword).lower() in text]
        threshold = assertion.get("threshold", len(keywords) if keywords else 1)
        passed = len(matched) >= threshold
        return {
            "path": path,
            "op": assertion["op"],
            "expected": keywords,
            "actual": actual,
            "passed": passed,
            "judge": self.name,
            "matched": matched,
            "threshold": threshold,
        }


@dataclass
class OpenAIJudge:
    """Optional LLM judge using the OpenAI Responses API if the SDK is installed."""

    model: str = "gpt-4.1-mini"
    name: str = "openai-judge"

    def evaluate(self, *, prediction: dict[str, Any], assertion: dict[str, Any]) -> dict[str, Any]:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai package is required for llm_judge assertions") from exc

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        path = assertion["path"]
        prompt = assertion.get("prompt", "Does the actual output satisfy the expectation?")
        response = client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are an evaluation judge. Return compact JSON with keys "
                        "`passed` (bool) and `reason` (string)."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "instruction": prompt,
                            "path": path,
                            "expected": assertion.get("value"),
                            "prediction": prediction,
                        }
                    ),
                },
            ],
        )
        text = response.output_text
        parsed = json.loads(text)
        return {
            "path": path,
            "op": assertion["op"],
            "expected": assertion.get("value"),
            "actual": prediction,
            "passed": bool(parsed["passed"]),
            "judge": self.name,
            "reason": parsed.get("reason", ""),
            "model": self.model,
        }

