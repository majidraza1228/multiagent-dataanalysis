---
name: fastapi-backend
description: FastAPI backend scaffold for ML model serving with predict and health endpoints
---

```python
# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import time

from app.model import get_model
from app.routers import predict_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_model()  # load once at startup
    app.state.start_time = time.time()
    yield

app = FastAPI(title="ML Image Classifier", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router, prefix="/api")
```

```python
# app/model.py
import torch
from torchvision import models, transforms
from PIL import Image
import io

_model = None
MODEL_VERSION = "1.0.0"
CLASSES = ["airplane","automobile","bird","cat","deer","dog","frog","horse","ship","truck"]

def get_model():
    global _model
    if _model is None:
        _model = torch.load("checkpoints/model.pt", map_location="cpu")
        _model.eval()
    return _model

TRANSFORM = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,)),
])

def predict(image_bytes: bytes) -> dict:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = TRANSFORM(img).unsqueeze(0)
    with torch.no_grad():
        logits = get_model()(tensor)
        probs = torch.softmax(logits, dim=1)[0]
    top3_vals, top3_idx = probs.topk(3)
    return {
        "class": CLASSES[top3_idx[0].item()],
        "confidence": round(top3_vals[0].item(), 4),
        "top3": [
            {"class": CLASSES[i.item()], "confidence": round(v.item(), 4)}
            for v, i in zip(top3_vals, top3_idx)
        ],
    }
```

```python
# app/schemas.py
from pydantic import BaseModel
from typing import List

class Top3Item(BaseModel):
    class_name: str
    confidence: float

class PredictResponse(BaseModel):
    class_: str
    confidence: float
    top3: List[Top3Item]

class HealthResponse(BaseModel):
    status: str
    model_version: str
    uptime: float
```

```python
# app/routers.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
import time
from app.model import predict, MODEL_VERSION

predict_router = APIRouter()

@predict_router.post("/predict")
async def run_predict(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    try:
        image_bytes = await file.read()
        result = predict(image_bytes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model failure: {str(e)}")

@predict_router.get("/health")
async def health(request: Request):
    return {
        "status": "ok",
        "model_version": MODEL_VERSION,
        "uptime": round(time.time() - request.app.state.start_time, 2),
    }
```

```python
# tests/test_api.py
import httpx

resp = httpx.get("http://localhost:8000/api/health")
assert resp.status_code == 200

with open("tests/sample.jpg", "rb") as f:
    resp = httpx.post("http://localhost:8000/api/predict", files={"file": f})
assert resp.status_code == 200 and "class" in resp.json()
```

```bash
# run server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
