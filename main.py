import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware import AnalysisLogger
from app.model import get_model
from app.routers import analysis_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_model()
    app.state.start_time = time.time()
    yield


app = FastAPI(title="Excel Sheet Analysis API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AnalysisLogger)
app.include_router(analysis_router, prefix="/api")
