import os
import time

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from app.model import MODEL_VERSION, SUPPORTED_EXTENSIONS, analyze_workbook

analysis_router = APIRouter()
MAX_FILE_SIZE = 10 * 1024 * 1024


@analysis_router.post("/analyze")
async def analyze_excel(file: UploadFile = File(...)):
    filename = file.filename or "workbook"
    extension = os.path.splitext(filename)[1].lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File must be .xlsx, .xls, or .csv")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Workbook too large (max 10MB)")

    try:
        return analyze_workbook(file_bytes, filename)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Workbook analysis failed: {exc}") from exc


@analysis_router.get("/health")
async def health(request: Request):
    start_time = getattr(request.app.state, "start_time", time.time())
    return {
        "status": "ok",
        "model_version": MODEL_VERSION,
        "uptime": round(time.time() - start_time, 2),
    }
