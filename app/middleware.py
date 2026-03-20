import hashlib
import json
import time
from pathlib import Path

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

LOG_PATH = Path("logs/predictions.jsonl")
LOG_PATH.parent.mkdir(exist_ok=True)


def file_hash(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()[:8]


class AnalysisLogger(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path != "/api/analyze" or request.method != "POST":
            return await call_next(request)

        body = await request.body()
        payload_hash = file_hash(body)

        async def receive():
            return {"type": "http.request", "body": body}

        request._receive = receive
        start = time.time()
        response = await call_next(request)
        latency_ms = round((time.time() - start) * 1000, 2)

        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        try:
            data = json.loads(response_body)
            entry = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "file_hash": payload_hash,
                "workbook_name": data.get("workbook_name"),
                "dataset_type": data.get("dataset_type"),
                "sheet_count": data.get("sheet_count"),
                "confidence": data.get("confidence"),
                "latency_ms": latency_ms,
            }
            with open(LOG_PATH, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry) + "\n")
        except Exception:
            pass

        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
