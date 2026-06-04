from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import ml

router = APIRouter(prefix="/predict", tags=["predict"])
models_router = APIRouter(prefix="/models", tags=["models"])

class LoanFeatures(BaseModel):
    loan_amnt: float = Field(..., gt=0, description="Monto solicitado (USD)", examples=[15000])
    term: int = Field(..., description="Plazo en meses (36 o 60)", examples=[36])
    annual_inc: float = Field(..., ge=0, description="Ingreso anual (USD)", examples=[65000])
    dti: float = Field(..., description="Debt-to-income ratio", examples=[18.4])
    emp_length: int = Field(..., ge=0, le=10, description="Antigüedad laboral en años (0-10)", examples=[5])
    purpose: str = Field(..., description="Propósito del préstamo", examples=["debt_consolidation"])

class ClassificationResponse(BaseModel):
    prediction: str
    probability_default: float
    model: str

class RegressionResponse(BaseModel):
    predicted_int_rate: float
    model: str

def _require_artifacts():
    try:
        return ml.artifacts_ready()
    except Exception:
        return False

@router.post("/classification", response_model=ClassificationResponse)
def predict_classification(features: LoanFeatures):
    try:
        model = ml.get_classification_model()
    except ml.ArtifactsMissing as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    X = ml.features_to_frame(features.model_dump())
    proba = float(model.predict_proba(X)[0, 1])
    label = "Charged Off" if proba >= 0.5 else "Fully Paid"
    return ClassificationResponse(
        prediction=label,
        probability_default=round(proba, 4),
        model=ml.best_model_name("classification"),
    )

@router.post("/regression", response_model=RegressionResponse)
def predict_regression(features: LoanFeatures):
    try:
        model = ml.get_regression_model()
    except ml.ArtifactsMissing as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    X = ml.features_to_frame(features.model_dump())
    rate = float(model.predict(X)[0])
    return RegressionResponse(
        predicted_int_rate=round(rate, 2),
        model=ml.best_model_name("regression"),
    )

@models_router.get("/metrics")
def model_metrics():
    try:
        return ml.get_metrics()
    except ml.ArtifactsMissing as exc:
        raise HTTPException(status_code=503, detail=str(exc))

@models_router.get("/metadata")
def model_metadata():
    try:
        return ml.get_metadata()
    except ml.ArtifactsMissing as exc:
        raise HTTPException(status_code=503, detail=str(exc))
