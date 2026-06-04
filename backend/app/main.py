from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import db, ml
from .routers import olap, predict

app = FastAPI(
    title="LoanSight API",
    description="Análisis y riesgo crediticio sobre el dataset Lending Club.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(olap.router)
app.include_router(predict.router)
app.include_router(predict.models_router)

@app.get("/", tags=["meta"])
def root():
    return {
        "name": "LoanSight API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": ["/olap", "/predict", "/models"],
    }

@app.get("/health", tags=["meta"])
def health():
    return {
        "status": "ok",
        "warehouse_available": db.warehouse_available(),
        "models_ready": ml.artifacts_ready(),
    }
