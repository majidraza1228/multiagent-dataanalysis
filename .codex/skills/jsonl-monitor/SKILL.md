---
name: jsonl-monitor
description: FastAPI middleware for JSONL prediction logging, drift detection, and monitoring dashboard
---

```python
# app/middleware.py — append to logs/predictions.jsonl on every /predict call
import json
import time
import hashlib
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

LOG_PATH = Path("logs/predictions.jsonl")
LOG_PATH.parent.mkdir(exist_ok=True)

def image_hash(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()[:6]

class PredictionLogger(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path != "/api/predict" or request.method != "POST":
            return await call_next(request)

        body = await request.body()
        img_hash = image_hash(body)

        async def receive():
            return {"type": "http.request", "body": body}
        request._receive = receive

        start = time.time()
        response = await call_next(request)
        latency_ms = round((time.time() - start) * 1000, 2)

        # capture response body
        resp_body = b""
        async for chunk in response.body_iterator:
            resp_body += chunk
        data = json.loads(resp_body)

        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "image_hash": img_hash,
            "predicted_class": data.get("class"),
            "confidence": data.get("confidence"),
            "latency_ms": latency_ms,
        }
        with open(LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")

        from starlette.responses import Response
        return Response(content=resp_body, status_code=response.status_code,
                        headers=dict(response.headers), media_type=response.media_type)
```

```python
# register middleware in main.py
from app.middleware import PredictionLogger
app.add_middleware(PredictionLogger)
```

```python
# monitor_dashboard.py
import json
from pathlib import Path
from collections import Counter
from tabulate import tabulate

LOG_PATH = Path("logs/predictions.jsonl")
DRIFT_WINDOW = 100
DRIFT_THRESHOLD = 0.6

def load_logs():
    if not LOG_PATH.exists():
        return []
    with open(LOG_PATH) as f:
        return [json.loads(line) for line in f if line.strip()]

logs = load_logs()
if not logs:
    print("No predictions logged yet.")
else:
    confs = [e["confidence"] for e in logs]
    classes = [e["predicted_class"] for e in logs]
    latencies = [e["latency_ms"] for e in logs]

    stats = [
        ["Total predictions", len(logs)],
        ["Avg confidence", f"{sum(confs)/len(confs):.4f}"],
        ["Min confidence", f"{min(confs):.4f}"],
        ["Max confidence", f"{max(confs):.4f}"],
        ["Avg latency (ms)", f"{sum(latencies)/len(latencies):.1f}"],
        ["Most predicted class", Counter(classes).most_common(1)[0][0]],
    ]
    print(tabulate(stats, tablefmt="grid"))

    # drift alert
    recent = logs[-DRIFT_WINDOW:]
    avg_conf = sum(e["confidence"] for e in recent) / len(recent)
    if avg_conf < DRIFT_THRESHOLD:
        print(f"\n⚠ DRIFT ALERT: avg confidence over last {len(recent)} predictions = {avg_conf:.4f} (threshold: {DRIFT_THRESHOLD})")
```
