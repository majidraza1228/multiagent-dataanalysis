import json
from collections import Counter
from pathlib import Path

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

LOG_PATH = Path("logs/predictions.jsonl")
DRIFT_WINDOW = 100
DRIFT_THRESHOLD = 0.55


def load_logs():
    if not LOG_PATH.exists():
        return []
    with open(LOG_PATH, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def run_dashboard():
    logs = load_logs()
    if not logs:
        print("No workbook analyses logged yet.")
        return

    confidences = [entry["confidence"] for entry in logs if entry.get("confidence") is not None]
    dataset_types = [entry["dataset_type"] for entry in logs if entry.get("dataset_type")]
    sheet_counts = [entry["sheet_count"] for entry in logs if entry.get("sheet_count") is not None]
    latencies = [entry["latency_ms"] for entry in logs if entry.get("latency_ms") is not None]

    stats = [
        ["Total analyses", len(logs)],
        ["Avg confidence", f"{sum(confidences)/len(confidences):.4f}" if confidences else "N/A"],
        ["Avg sheet count", f"{sum(sheet_counts)/len(sheet_counts):.2f}" if sheet_counts else "N/A"],
        ["Avg latency (ms)", f"{sum(latencies)/len(latencies):.1f}" if latencies else "N/A"],
        ["Most common dataset type", Counter(dataset_types).most_common(1)[0][0] if dataset_types else "N/A"],
    ]

    if HAS_TABULATE:
        print(tabulate(stats, tablefmt="grid"))
    else:
        for label, value in stats:
            print(f"{label}: {value}")

    recent = logs[-DRIFT_WINDOW:]
    recent_confidences = [entry["confidence"] for entry in recent if entry.get("confidence") is not None]
    if recent_confidences:
        avg_confidence = sum(recent_confidences) / len(recent_confidences)
        if avg_confidence < DRIFT_THRESHOLD:
            print(
                f"\nDRIFT ALERT: avg confidence over last {len(recent)} analyses "
                f"= {avg_confidence:.4f} (threshold: {DRIFT_THRESHOLD})"
            )
        else:
            print(f"\nDrift OK: avg confidence = {avg_confidence:.4f} (threshold: {DRIFT_THRESHOLD})")


if __name__ == "__main__":
    run_dashboard()
