import json
from pathlib import Path

LOG_PATH = Path("logs/predictions.jsonl")
DRIFT_THRESHOLD = 0.55
DRIFT_WINDOW = 100


def check_drift() -> dict:
    if not LOG_PATH.exists():
        return {"status": "no_data", "avg_confidence": None, "drift_detected": False}

    try:
        with open(LOG_PATH, encoding="utf-8") as handle:
            logs = [json.loads(line) for line in handle if line.strip()]
    except Exception as exc:
        return {"status": "error", "error": str(exc), "drift_detected": False}

    if not logs:
        return {"status": "no_data", "avg_confidence": None, "drift_detected": False}

    recent = logs[-DRIFT_WINDOW:]
    valid = [entry["confidence"] for entry in recent if entry.get("confidence") is not None]
    if not valid:
        return {"status": "no_confidence", "avg_confidence": None, "drift_detected": False}

    avg_confidence = round(sum(valid) / len(valid), 4)
    return {
        "status": "ok",
        "avg_confidence": avg_confidence,
        "drift_detected": avg_confidence < DRIFT_THRESHOLD,
        "threshold": DRIFT_THRESHOLD,
        "total_analyses": len(logs),
    }
